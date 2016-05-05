from deployer.utils import parse_constraints
from jujuclient import (UnitErrors,
                        EnvError)


class MemoryEnvironment(object):
    """ In memory deployment: not all features implemented
        (notably subordinates and their relations).
    """

    def __init__(self, name, deployment):
        """ Two main dicts: _services (return-able as part of status(),
            and _services_data (to hold e.g. config, constraints)
        """
        super(MemoryEnvironment, self).__init__()
        self.name = name
        self._deployment = deployment
        self._services = {}
        self._services_data = {}
        self._relations = {}
        self._do_deploy()

    def add_units(self, svc_name, num):
        """Add units
        """
        next_num = self._services_data[svc_name]['next_unit_num']
        for idx in xrange(next_num, next_num + num):
            self._services[svc_name]['units'].append(
                '{}/{}'.format(svc_name, idx))
        self._services_data[svc_name]['next_unit_num'] = \
            next_num + num

    def remove_unit(self, unit_name):
        """ Remove a unit by name """
        svc_name = unit_name.split('/')[0]
        units_idx = {unit: idx for idx, unit in
                     enumerate(self._services[svc_name]['units'])}
        try:
            self._services[svc_name]['units'].pop(
                units_idx[unit_name])
        except KeyError:
            raise UnitErrors("Invalid unit name")

    def _get_service(self, svc_name):
        """ Get service by name (as returned by status())
        """
        if not svc_name in self._services:
            raise EnvError("Invalid service name")
        return self._services[svc_name]

    def add_relation(self, endpoint_a, endpoint_b):
        """Add relations
        """

    def destroy_service(self, svc_name):
        """ Destroy a service
        """
        if not svc_name in self._services:
            raise EnvError("Invalid service name")
        del self._services[svc_name]

    def close(self):
        """
        """

    def connect(self):
        """
        """

    def set_config(self, svc_name, cfg_dict):
        """ Set service config from passed dict, keeping
            the structure as needed for status() return
        """
        config = self.get_config(svc_name)
        if cfg_dict:
            for cfg_k, cfg_v in cfg_dict.items():
                config_entry = config.setdefault(cfg_k, {})
                config_entry['value'] = cfg_v

    def set_constraints(self, svc_name, constr_str):
        """ Set service constraints from "key=value ..."
            passed string
        """
        constraints = parse_constraints(constr_str) if constr_str else {}
        self._services_data[svc_name]['constraints'] = constraints

    def get_config(self, svc_name):
        """ Return service configs - note its structure:
            config{thename: {'value': thevalue}, ...}
        """
        return self._services_data[svc_name]['config']

    def get_constraints(self, svc_name):
        """ Return service constraints dict
        """
        return self._services_data[svc_name]['constraints']

    def get_cli_status(self):
        pass

    def reset(self):
        pass

    def resolve_errors(self, retry_count=0, timeout=600, watch=False, delay=5):
        pass

    def _do_deploy(self):
        """ Fake deploy: build in-memory representation of the deployed set
            of services from deployment
        """
        self._compile_relations()
        for service in self._deployment.get_services():
            svc_name = service.name
            charm = self._deployment.get_charm_for(svc_name)
            relations = self._relations.setdefault(svc_name, {})
            self._services[svc_name] = {
                'units': [],
                'charm': charm.name,
                'relations': relations,
            }
            self._services_data[svc_name] = {
                'next_unit_num': 0,
                'config': {},
                'constraints': {},
            }
            # XXX: Incomplete relations support: only add units for non-subords
            num_units = 0 if charm.is_subordinate() else service.num_units
            self.add_units(svc_name, num_units)
            self.set_config(svc_name, service.config)
            self.set_constraints(svc_name, service.constraints)

    def _compile_relations(self):
        """ Compile a relation dictionary by svc_name, with
            their values structured for status() return
        """
        for rel in self._deployment.get_relations():
            for src, dst in (rel[0], rel[1]), (rel[1], rel[0]):
                try:
                    src_requires = self._deployment.get_charm_for(
                        src).get_requires()
                    dst_provides = self._deployment.get_charm_for(
                        dst).get_provides()
                except KeyError:
                    continue
                # Create dicts key-ed by:
                #  { interface_type: (interface_name, svc_name)}
                src_dict = {}
                dst_dict = {}
                # {rel_name: [{interface: name }...]}
                for _, interfaces in src_requires.items():
                    for interface in interfaces:
                        src_dict[interface.get('interface')] = (
                            interface.get('name'), src)
                for _, interfaces in dst_provides.items():
                    for interface in interfaces:
                        dst_dict[interface.get('interface')] = (
                            interface.get('name'), dst)
                # Create juju env relation entries as:
                # {svc_name: { interface_name: [ svc_name2, ...] }, ...}
                for src_rel, (if_name, src_svc_name) in src_dict.items():
                    if src_rel in dst_dict:
                        src_rels = self._relations.setdefault(src_svc_name, {})
                        src_rels.setdefault(if_name, [])
                        dst_svc_name = dst_dict[src_rel][1]
                        src_rels[if_name].append(dst_svc_name)

    def status(self):
        """ Return all services status """
        return {'services': self._services}

    def wait_for_units(self, *args, **kwargs):
        pass
