from __future__ import absolute_import
import itertools

from .feedback import Feedback
from six.moves import map


class Service(object):

    def __init__(self, name, svc_data):
        self.svc_data = svc_data
        self.name = name

    def __repr__(self):
        return "<Service %s>" % (self.name)

    @property
    def annotations(self):
        a = self.svc_data.get('annotations')
        if a is None:
            return a
        # core annotations only supports string key / values
        d = {}
        for k, v in a.items():
            d[str(k)] = str(v)
        return d

    @property
    def config(self):
        return self.svc_data.get('options', None)

    @property
    def constraints(self):
        return self.svc_data.get('constraints', None)

    @property
    def num_units(self):
        return int(self.svc_data.get('num_units', 1))

    @property
    def unit_placement(self):
        # Separate checks to support machine 0 placement.
        value = self.svc_data.get('to')
        if value is None:
            value = self.svc_data.get('force-machine')
        if value is not None and not isinstance(value, list):
            value = [value]
        return value and list(map(str, value)) or []

    @property
    def expose(self):
        return self.svc_data.get('expose', False)


class ServiceUnitPlacement(object):

    def __init__(self, service, deployment, status, arbitrary_machines=False):
        self.service = service
        self.deployment = deployment
        self.status = status
        self.arbitrary_machines = arbitrary_machines

    @staticmethod
    def _format_placement(machine, container=None):
        if container:
            return "%s:%s" % (container, machine)
        else:
            return machine

    def colocate(self, status, placement, u_idx, container, svc):
        """Colocate one service with an existing service either within a
        container alongside that service or hulk-smashed onto the same unit.

        status: the environment status.
        placement: the placement directive of the unit to be colocated.
        u_idx: the unit index of the unit to be colocated.
        container: a string containing the container type, or None.
        svc: the service object for this placement.
        """
        with_service = status['services'].get(placement)
        if with_service is None:
            # Should be caught in validate relations but sanity check
            # for concurrency.
            self.deployment.log.error(
                "Service %s to be deployed with non-existent service %s",
                svc.name, placement)
            # Prefer continuing deployment with a new machine rather
            # than an in-progress abort.
            return None

        svc_units = with_service['units']
        if int(u_idx) >= len(svc_units):
            self.deployment.log.warning(
                "Service:%s, Deploy-with-service:%s, Requested-unit-index=%s, "
                "Cannot solve, falling back to default placement",
                svc.name, placement, u_idx)
            return None
        unit_names = list(svc_units.keys())
        unit_names.sort()
        machine = svc_units[unit_names[int(u_idx)]].get('machine')
        if not machine:
            self.deployment.log.warning(
                "Service:%s deploy-with unit missing machine %s",
                svc.name, unit_names[int(u_idx)])
            return None
        return self._format_placement(machine, container)


class ServiceUnitPlacementV3(ServiceUnitPlacement):

    def _parse_placement(self, unit_placement):
        placement = unit_placement
        container = None
        u_idx = None
        if ':' in unit_placement:
            container, placement = unit_placement.split(":")
        if '=' in placement:
            placement, u_idx = placement.split("=")
        return container, placement, u_idx

    def validate(self):
        feedback = Feedback()

        unit_placement = self.service.unit_placement
        if unit_placement is None:
            return feedback

        if not isinstance(unit_placement, list):
            unit_placement = [unit_placement]
        unit_placement = list(map(str, unit_placement))

        services = dict([(s.name, s) for s in self.deployment.get_services()])
        machines = self.deployment.get_machines()

        for idx, p in enumerate(unit_placement):
            container, p, u_idx = self._parse_placement(p)
            if container and container not in ('lxc', 'kvm'):
                feedback.error(
                    "Invalid container type:%s service: %s placement: %s"
                    % (container, self.service.name, unit_placement[idx]))
            if u_idx:
                if p in ('maas', 'zone'):
                    continue
                if not u_idx.isdigit():
                    feedback.error(
                        "Invalid service:%s placement: %s" % (
                            self.service.name, unit_placement[idx]))
            if p.isdigit():
                if p == '0' or p in machines or self.arbitrary_machines:
                    continue
                else:
                    feedback.error(
                        ("Service placement to machine "
                         "not supported %s to %s") % (
                             self.service.name, unit_placement[idx]))
            elif p in services:
                if services[p].unit_placement:
                    feedback.error(
                        "Nested placement not supported %s -> %s -> %s" % (
                            self.service.name, p, services[p].unit_placement))
                elif self.deployment.get_charm_for(p).is_subordinate():
                    feedback.error(
                        "Cannot place to a subordinate service: %s -> %s" % (
                            self.service.name, p))
            else:
                feedback.error(
                    "Invalid service placement %s to %s" % (
                        self.service.name, unit_placement[idx]))
        return feedback

    def get(self, unit_number):
        """Get the placement directive for a given unit.

        unit_number: the number of the unit to deploy
        """
        status = self.status
        svc = self.service

        unit_mapping = svc.unit_placement
        if not unit_mapping:
            return None
        if len(unit_mapping) <= unit_number:
            return None

        unit_placement = placement = str(unit_mapping[unit_number])
        container = None
        u_idx = unit_number

        if ':' in unit_placement:
            container, placement = unit_placement.split(":")
        if '=' in placement:
            placement, u_idx = placement.split("=")

        if placement.isdigit():
            if self.arbitrary_machines or placement == '0':
                return self._format_placement(placement, container)
        if placement == 'maas':
            return u_idx
        elif placement == "zone":
            return "zone=%s" % u_idx

        return self.colocate(status, placement, u_idx, container, svc)


class ServiceUnitPlacementV4(ServiceUnitPlacement):

    def __init__(self, service, deployment, status, arbitrary_machines=False,
                 machines_map=None):
        super(ServiceUnitPlacementV4, self).__init__(
            service, deployment, status, arbitrary_machines=arbitrary_machines)

        # Arbitrary machines will not be allowed in v4 bundles.
        self.arbitrary_machines = False

        self.machines_map = machines_map

        # Ensure that placement spec is filled according to the bundle
        # specification.
        self._fill_placement()

    def _fill_placement(self):
        """Fill the placement spec with necessary data.

        From the spec:
        A unit placement may be specified with a service name only, in which
        case its unit number is assumed to be one more than the unit number of
        the previous unit in the list with the same service, or zero if there
        were none.

        If there are less elements in To than NumUnits, the last element is
        replicated to fill it. If there are no elements (or To is omitted),
        "new" is replicated.
        """
        unit_mapping = self.service.unit_placement
        unit_count = self.service.num_units
        if not unit_mapping:
            self.service.svc_data['to'] = ['new'] * unit_count
            return

        self.service.svc_data['to'] = (
            unit_mapping +
            list(itertools.repeat(
                unit_mapping[-1], unit_count - len(unit_mapping)))
        )
        unit_mapping = self.service.unit_placement

        colocate_counts = {}
        for idx, mapping in enumerate(unit_mapping):
            service = mapping
            if ':' in mapping:
                service = mapping.split(':')[1]
            if service in self.deployment.data['services']:
                unit_number = colocate_counts.setdefault(service, 0)
                unit_mapping[idx] = "{}/{}".format(mapping, unit_number)
                colocate_counts[service] += 1
        self.service.svc_data['to'] = unit_mapping

    def _parse_placement(self, placement):
        """Parse a unit placement statement.

        In version 4 bundles, unit placement statements take the form of

          (<containertype>:)?(<unit>|<machine>|new)

        This splits the placement into a container, a placement, and a unit
        number.  Both container and unit number are optional and can be None.
        """
        container = unit_number = None
        if ':' in placement:
            container, placement = placement.split(':')
        if '/' in placement:
            placement, unit_number = placement.split('/')
        return container, placement, unit_number

    def validate(self):
        """Validate the placement of a service and all of its units.

        If a service has a 'to' block specified, the list of machines, units,
        containers, and/or services must be internally consistent, consistent
        with other services in the deployment, and consistent with any machines
        specified in the 'machines' block of the deployment.

        A feedback object is returned, potentially with errors and warnings
        inside it.
        """
        feedback = Feedback()

        unit_placement = self.service.unit_placement
        if unit_placement is None:
            return feedback

        if not isinstance(unit_placement, (list, tuple)):
            unit_placement = [unit_placement]
        unit_placement = list(map(str, unit_placement))

        services = dict([(s.name, s) for s in self.deployment.get_services()])
        machines = self.deployment.get_machines()
        service_name = self.service.name

        for i, placement in enumerate(unit_placement):
            container, target, unit_number = self._parse_placement(placement)

            # Validate the container type.
            if container and container not in ('lxc', 'kvm'):
                feedback.error(
                    'Invalid container type: {} service: {} placement: {}'
                    ''.format(container, service_name, placement))
            # Specify an existing machine (or, if the number is in the
            # list of machine specs, one of those).
            if str(target) in machines:
                continue
            if target.isdigit():
                feedback.error(
                    'Service placement to machine not supported: {} to {}'
                    ''.format(service_name, placement))
            # Specify a service for co-location.
            elif target in services:
                # Specify a particular unit for co-location.
                if unit_number is not None:
                    try:
                        unit_number = int(unit_number)
                    except (TypeError, ValueError):
                        feedback.error(
                            'Invalid unit number for placement: {} to {}'
                            ''.format(service_name, unit_number))
                        continue
                    if unit_number > services[target].num_units:
                        feedback.error(
                            'Service unit does not exist: {} to {}/{}'
                            ''.format(service_name, target, unit_number))
                        continue
                if self.deployment.get_charm_for(target).is_subordinate():
                    feedback.error(
                        'Cannot place to a subordinate service: {} -> {}'
                        ''.format(service_name, target))
            # Create a new machine or container.
            elif target == 'new':
                continue
            else:
                feedback.error(
                    'Invalid service placement: {} to {}'
                    ''.format(service_name, placement))
        return feedback

    def get_new_machines_for_containers(self):
        """Return a list of containers in the service's unit placement that
        have been requested to be put on new machines."""
        new_machines = []
        unit = itertools.count()
        for placement in self.service.unit_placement:
            if ':new' in placement:
                # Generate a name for this machine to be used in the
                # machines_map used later; as a quick path forward, simply use
                # the unit's name.
                new_machines.append('{}/{}'.format(
                    self.service.name, next(unit)))
        return new_machines

    def get(self, unit_number):
        """Get the placement directive for a given unit.

        unit_number: the number of the unit to deploy
        """
        status = self.status
        svc = self.service

        unit_mapping = svc.unit_placement
        if not unit_mapping:
            return None
        unit_placement = placement = str(unit_mapping[unit_number])
        container = None
        u_idx = unit_number

        # Shortcut for new machines.
        if placement == 'new':
            return None

        container, placement, unit_number = self._parse_placement(
            unit_placement)

        if placement in self.machines_map:
            return self._format_placement(
                self.machines_map[placement], container)

        # Handle <container_type>:new
        if placement == 'new':
            return self._format_placement(
                self.machines_map['%s/%d' % (self.service.name, u_idx)],
                container)

        return self.colocate(status, placement, u_idx, container, svc)
