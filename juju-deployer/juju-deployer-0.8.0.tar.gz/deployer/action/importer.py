from __future__ import absolute_import
import logging
import time

from .base import BaseAction
from ..env import watchers
from ..utils import ErrorExit
from six.moves import map
from six.moves import range


class Importer(BaseAction):

    log = logging.getLogger("deployer.import")

    def __init__(self, env, deployment, options):
        self.options = options
        self.env = env
        self.deployment = deployment

    def add_units(self):
        self.log.debug("Adding units...")
        # Add units to existing services that don't match count.
        env_status = self.env.status()

        # Workaround an issue where watch output doesn't include subordinate
        # services right away, and add_unit would fail while attempting to add
        # units to a non-existant service. See lp:1421315 for details.
        cur_units = 0
        for svc in self.deployment.get_services():
            delay = time.time() + 60
            while delay > time.time():
                if svc.name in env_status['services']:
                    cur_units = len(
                        env_status['services'][svc.name].get('units', ())
                    )
                    if cur_units > 0:
                        break
                time.sleep(5)
                env_status = self.env.status()

            delta = (svc.num_units - cur_units)

            if delta <= 0:
                self.log.debug(
                    " Service %r does not need any more units added.",
                    svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            if charm.is_subordinate():
                self.log.warning(
                    "Config specifies num units for subordinate: %s",
                    svc.name)
                continue

            self.log.info(
                "Adding %d more units to %s" % (abs(delta), svc.name))
            if svc.unit_placement:
                # Reload status before each placed unit is deployed, so that
                # co-location to other units can take place properly.
                env_status = self.env.status()
                placement = self.deployment.get_unit_placement(svc, env_status)
                for mid in range(cur_units, svc.num_units):
                    self.env.add_unit(svc.name, placement.get(mid))
            else:
                self.env.add_units(svc.name, abs(delta))

    def machine_exists(self, id):
        """Checks if the given id exists on the current environment."""
        return str(id) in list(map(str, self.env.status().get('machines', {})))

    def create_machines(self):
        """Create machines as specified in the machine spec in the bundle.

        A machine spec consists of a named machine (the name is, by convention,
        an integer) with an optional series, optional constraints and optional
        annotations:

        0:
          series: "precise"
          constraints: "mem=4G arch=i386"
          annotations:
            foo: bar
        1:
          constraints: "mem=4G"

        This method first attempts to create any machines in the 'machines'
        section of the bundle specification with the given constraints and
        annotations.  Then, if there are any machines requested for containers
        in the style of <container type>:new, it creates those machines and
        adds them to the machines map.

        If the machine already exists on the environment, then the new machine
        creation is skipped.
        """
        machines = self.deployment.get_machines()
        machines_map = {}

        if machines:
            self.log.info("Creating machines...")
            for machine_name, spec in machines.items():
                if self.machine_exists(machine_name):
                    # XXX frankban: do we really want this? The machine
                    # identifiers as included in v4 bundles are not intended
                    # to refer to real machines. A mapping could be provided
                    # but this kind of implicit mapping seems weak.
                    self.log.info(
                        """Machine %s already exists on environment, """
                        """skipping creation""" % machine_name)
                    machines_map[machine_name] = str(machine_name)
                else:
                    self.log.info("Machine %s will be created" % machine_name)
                    machines_map[machine_name] = self.env.add_machine(
                        series=spec.get('series',
                                        self.deployment.data['series']),
                        constraints=spec.get('constraints'))

                if isinstance(spec, dict):
                    annotations = spec.get('annotations')
                    if annotations:
                        self.env.set_annotation(
                            machines_map[machine_name],
                            annotations,
                            entity_type='machine')

            # In the case of <container type>:new, we need to create a machine
            # before creating the container on which the service will be
            # deployed.  This is stored in the machines map which will be used
            # in the service placement.
            for service in self.deployment.get_services():
                placement = self.deployment.get_unit_placement(service, None)
                for container_host in \
                        placement.get_new_machines_for_containers():
                    if self.machine_exists(machine_name):
                        self.log.info("Machine %s already exists,"
                                      "skipping creation" % machine_name)
                        machines_map[container_host] = str(container_host)
                    else:
                        self.log.info("A new container will be created"
                                      "on machine: %s" % container_host)
                        machines_map[container_host] = self.env.add_machine()
            self.deployment.set_machines(machines_map)

    def get_charms(self):
        # Get Charms
        self.log.debug("Getting charms...")
        self.deployment.fetch_charms(
            update=self.options.update_charms,
            no_local_mods=self.options.no_local_mods)

        # Load config overrides/includes and verify rels after we can
        # validate them.
        self.deployment.resolve(self.options.overrides or ())

    def deploy_services(self, add_units=True):
        """Deploy the services specified in the deployment.

        add_units: whether or not to add units to the service as it is
          deployed; newer versions of bundles may have machines specified
          in a machine spec, and units will be placed accordingly if this
          flag is false.
        """
        self.log.info("Deploying services...")
        env_status = self.env.status()
        reloaded = False

        for svc in self.deployment.get_services():
            if svc.name in env_status['services']:
                self.log.debug(
                    " Service %r already deployed. Skipping" % svc.name)
                continue

            charm = self.deployment.get_charm_for(svc.name)
            self.log.info(
                " Deploying service %s using %s", svc.name,
                charm.charm_url if not charm.is_absolute() else charm.path
            )

            if svc.unit_placement:
                # We sorted all the non placed services first, so we only
                # need to update status once after we're done with them, in
                # the instance of v3 bundles; in the more complex case of v4
                # bundles, we'll need to refresh each time.
                if not reloaded:
                    self.log.debug(
                        " Refetching status for placement deploys")
                    time.sleep(5.1)
                    env_status = self.env.status()
                    # In the instance of version 3 deployments, we will not
                    # need to fetch the status more than once.  In version 4
                    # bundles, however, we will need to fetch the status each
                    # time in order to allow for the machine specification to
                    # be taken into account.
                    if self.deployment.version == 3:
                        reloaded = True
                num_units = 1
            else:
                num_units = svc.num_units

            # Only add a single unit if requested. This is done after the above
            # work to ensure that the status is still retrieved as necessary.
            if not add_units:
                num_units = 1

            placement = self.deployment.get_unit_placement(svc, env_status)

            if charm.is_subordinate():
                num_units = None

            self.env.deploy(
                svc.name,
                charm.charm_url,
                charm.repo_path or self.deployment.repo_path,
                svc.config,
                svc.constraints,
                num_units,
                placement.get(0),
                charm.series or self.deployment.series,
            )

            if svc.annotations:
                self.log.debug(" Setting annotations")
                self.env.set_annotation(svc.name, svc.annotations)

            if self.options.deploy_delay:
                self.log.debug(" Waiting for deploy delay")
                time.sleep(self.options.deploy_delay)

    def add_relations(self):
        self.log.info("Adding relations...")

        # Relations
        status = self.env.status()
        created = False

        for end_a, end_b in self.deployment.get_relations():
            if self._rel_exists(status, end_a, end_b):
                continue
            self.log.info(" Adding relation %s <-> %s", end_a, end_b)
            self.env.add_relation(end_a, end_b)
            created = True
        return created

    def _rel_exists(self, status, end_a, end_b):
        # Checks for a named relation on one side that matches the local
        # endpoint and remote service.
        (name_a, name_b, rem_a, rem_b) = (end_a, end_b, None, None)

        if ":" in end_a:
            name_a, rem_a = end_a.split(":", 1)
        if ":" in end_b:
            name_b, rem_b = end_b.split(":", 1)

        rels_svc_a = status['services'][name_a].get('relations', {})

        found = False
        for r, related in rels_svc_a.items():
            if name_b in related:
                if rem_a and r not in rem_a:
                    continue
                found = True
                break
        if found:
            return True
        return False

    def check_timeout(self):
        timeout = self.options.timeout - (time.time() - self.start_time)
        if timeout < 0:
            self.log.error("Reached deployment timeout.. exiting")
            raise ErrorExit()
        return timeout

    def wait_for_units(self, ignore_errors=False):
        if self.options.skip_unit_wait:
            return
        timeout = self.check_timeout()
        # Set up the callback to be called in case of unit errors: if
        # ignore_errors is True errors are just logged, otherwise we exit the
        # program.
        if ignore_errors:
            on_errors = watchers.log_on_errors(self.env)
        else:
            on_errors = watchers.exit_on_errors(self.env)
        self.env.wait_for_units(
            int(timeout), watch=self.options.watch,
            services=self.deployment.get_service_names(), on_errors=on_errors)

    def run(self):
        options = self.options
        self.start_time = time.time()

        # Get charms
        self.get_charms()
        if options.branch_only:
            return

        if options.bootstrap:
            self.env.bootstrap()
        self.env.connect()

        if self.deployment.version > 3:
            self.create_machines()

        # We can shortcut and add the units during deployment for v3 bundles.
        self.deploy_services(add_units=(self.deployment.version == 3))

        # Workaround api issue in juju-core, where any action takes 5s
        # to be consistent to subsequent watch api interactions, see
        # http://pad.lv/1203105 which will obviate this wait.
        time.sleep(5.1)
        self.add_units()

        ignore_errors = bool(options.retry_count) or options.ignore_errors
        self.log.debug("Waiting for units before adding relations")
        self.wait_for_units(ignore_errors=ignore_errors)

        # Reset our environment connection, as it may grow stale during
        # the watch (we're using a sync client so not responding to pings
        # unless actively using the conn).
        self.env.close()
        self.env.connect()

        self.check_timeout()
        rels_created = False
        if not options.no_relations:
            rels_created = self.add_relations()

        # Wait for the units to be up before waiting for rel stability.
        if rels_created and not options.skip_unit_wait:
            self.log.debug(
                "Waiting for relation convergence %ds", options.rel_wait)
            time.sleep(options.rel_wait)
            self.wait_for_units(ignore_errors=ignore_errors)

        if options.retry_count:
            self.log.info("Looking for errors to auto-retry")
            self.env.resolve_errors(
                options.retry_count,
                options.timeout - time.time() - self.start_time)

        # Finally expose things
        for svc in self.deployment.get_services():
            if svc.expose:
                self.log.info(" Exposing service %r" % svc.name)
                self.env.expose(svc.name)
