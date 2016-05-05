import base64
import StringIO
import os

from deployer.deployment import Deployment
from deployer.utils import setup_logging, ErrorExit

from .base import Base, skip_if_offline


class FauxService(object):
    """A fake service with a unit_placement attribute, used for testing
    the sort functionality.
    """

    def __init__(self, name=None, unit_placement=None):
        self.name = name
        self.unit_placement = unit_placement


class DeploymentTest(Base):

    def setUp(self):
        self.output = setup_logging(
            debug=True, verbose=True, stream=StringIO.StringIO())

    def get_named_deployment_and_fetch_v3(self, file_name, stack_name):
        deployment = self.get_named_deployment_v3(file_name, stack_name)
        # Fetch charms in order to allow proper late binding config and
        # placement validation.
        repo_path = self.mkdir()
        os.mkdir(os.path.join(repo_path, "precise"))
        deployment.repo_path = repo_path
        deployment.fetch_charms()
        return deployment

    def get_deployment_and_fetch_v4(self, file_name):
        deployment = self.get_deployment_v4(file_name)
        # Fetch charms in order to allow proper late binding config and
        # placement validation.
        repo_path = self.mkdir()
        os.mkdir(os.path.join(repo_path, "precise"))
        deployment.repo_path = repo_path
        deployment.fetch_charms()
        return deployment

    @skip_if_offline
    def test_deployer(self):
        d = self.get_named_deployment_and_fetch_v3('blog.yaml', 'wordpress-prod')
        services = d.get_services()
        self.assertTrue([s for s in services if s.name == "newrelic"])

        # Ensure inheritance order reflects reality, instead of merge value.
        self.assertEqual(
            d.data['inherits'],
            ['wordpress-stage', 'wordpress-base', 'metrics-base'])

        # Load up overrides and resolves
        d.load_overrides(["key=abc"])
        d.resolve()

        # Verify include-base64
        self.assertEqual(d.get_service('newrelic').config, {'key': 'abc'})
        self.assertEqual(
            base64.b64decode(d.get_service('blog').config['wp-content']),
            "HelloWorld")

        # TODO verify include-file

        # Verify relations
        self.assertEqual(
            list(d.get_relations()),
            [('blog', 'db'), ('blog', 'cache'), ('blog', 'haproxy')])

    def test_maas_name_and_zone_placement(self):
        d = self.get_named_deployment_v3("stack-placement-maas.yml", "stack")
        d.validate_placement()
        placement = d.get_unit_placement('ceph', {})
        self.assertEqual(placement.get(0), "arnolt")
        placement = d.get_unit_placement('heat', {})
        self.assertEqual(placement.get(0), "zone=zebra")

    @skip_if_offline
    def test_validate_placement_sorting(self):
        d = self.get_named_deployment_and_fetch_v3("stack-placement.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            self.fail("Should not fail")

    def test_machines_placement_sort(self):
        d = Deployment('test', None, None)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(unit_placement=1),
                FauxService()
            ), 1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(),
                FauxService(unit_placement=1)
            ), -1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(name="x", unit_placement=['asdf']),
                FauxService(name="y", unit_placement=['lxc:x/1'])
            ), -1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(name="y", unit_placement=['lxc:x/1']),
                FauxService(name="x", unit_placement=['asdf'])
            ), 1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(name="x", unit_placement=['y']),
                FauxService(name="y")
            ), 1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(name="x", unit_placement=['asdf']),
                FauxService(name="y", unit_placement=['hjkl'])
            ), -1)
        self.assertEqual(
            d._machines_placement_sort(
                FauxService(name="x"),
                FauxService(name="y")
            ), -1)

    def test_colocate(self):
        status = {
            'services': {
                'foo': {
                    'units': {
                        '1': {
                            'machine': 1
                        },
                        '2': {}
                    }
                }
            }
        }
        d = self.get_named_deployment_v3("stack-placement.yaml", "stack")
        p = d.get_unit_placement('ceph', status)
        svc = FauxService(name='bar')

        self.assertEqual(p.colocate(status, 'asdf', '1', '', svc),
                         None)
        self.assertIn('Service bar to be deployed with non-existent service '
                      'asdf',
                      self.output.getvalue())
        self.assertEqual(p.colocate(status, 'foo', '2', '', svc),
                         None)
        self.assertIn('Service:bar, Deploy-with-service:foo, '
                      'Requested-unit-index=2, Cannot solve, '
                      'falling back to default placement',
                      self.output.getvalue())
        self.assertEqual(p.colocate(status, 'foo', '1', '', svc),
                         None)
        self.assertIn('Service:bar deploy-with unit missing machine 2',
                      self.output.getvalue())
        self.assertEqual(p.colocate(status, 'foo', '0', '', svc), 1)

    @skip_if_offline
    def test_validate_invalid_placement_nested(self):
        d = self.get_named_deployment_and_fetch_v3("stack-placement-invalid.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            pass
        else:
            self.fail("Should fail")

    @skip_if_offline
    def test_validate_invalid_placement_no_with_service(self):
        d = self.get_named_deployment_and_fetch_v3(
            "stack-placement-invalid-2.yaml", "stack")
        services = d.get_services()
        self.assertEqual(services[0].name, 'nova-compute')
        try:
            d.validate_placement()
        except ErrorExit:
            pass
        else:
            self.fail("Should fail")

    @skip_if_offline
    def test_validate_invalid_placement_subordinate_v3(self):
        # Placement validation fails if a subordinate charm is provided.
        deployment = self.get_named_deployment_and_fetch_v3(
            'stack-placement-invalid-subordinate.yaml', 'stack')
        with self.assertRaises(ErrorExit):
            deployment.validate_placement()
        output = self.output.getvalue()
        self.assertIn(
            'Cannot place to a subordinate service: ceph -> nrpe\n', output)
        self.assertIn(
            'Cannot place to a subordinate service: nova-compute -> nrpe\n',
            output)

    @skip_if_offline
    def test_validate_invalid_placement_subordinate_v4(self):
        # Placement validation fails if a subordinate charm is provided.
        deployment = self.get_deployment_and_fetch_v4(
            'placement-invalid-subordinate.yaml')
        with self.assertRaises(ErrorExit):
            deployment.validate_placement()
        output = self.output.getvalue()
        self.assertIn(
            'Cannot place to a subordinate service: nova-compute -> nrpe\n',
            output)

    def test_validate_invalid_unit_number(self):
        # Placement validation fails if an invalid unit number is provided.
        deployment = self.get_deployment_v4('placement-invalid-number.yaml')
        with self.assertRaises(ErrorExit):
            deployment.validate_placement()
        output = self.output.getvalue()
        self.assertIn(
            'Invalid unit number for placement: django to bad-wolf\n', output)

    def test_get_unit_placement_v3(self):
        d = self.get_named_deployment_v3("stack-placement.yaml", "stack")
        status = {
            'services': {
                'nova-compute': {
                    'units': {
                        'nova-compute/2': {'machine': '1'},
                        'nova-compute/3': {'machine': '2'},
                        'nova-compute/4': {'machine': '3'}}}}}
        placement = d.get_unit_placement('ceph', status)
        self.assertEqual(placement.get(0), '1')
        self.assertEqual(placement.get(1), '2')
        self.assertEqual(placement.get(2), None)

        placement = d.get_unit_placement('quantum', status)
        self.assertEqual(placement.get(0), 'lxc:1')
        self.assertEqual(placement.get(2), 'lxc:3')
        self.assertEqual(placement.get(3), None)

        placement = d.get_unit_placement('verity', status)
        self.assertEqual(placement.get(0), 'lxc:3')

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), '0')

        placement = d.get_unit_placement('semper', status)
        self.assertEqual(placement.get(0), '3')

        placement = d.get_unit_placement('lxc-service', status)
        self.assertEqual(placement.get(0), 'lxc:2')
        self.assertEqual(placement.get(1), 'lxc:3')
        self.assertEqual(placement.get(2), 'lxc:1')
        self.assertEqual(placement.get(3), 'lxc:1')
        self.assertEqual(placement.get(4), 'lxc:3')

    def test_fill_placement_v4(self):
        d = self.get_deployment_v4('fill_placement.yaml')
        self.assertEqual(
            d.get_unit_placement('mediawiki1', 0).service.svc_data['to'],
            ['new', 'new'])
        self.assertEqual(
            d.get_unit_placement('mediawiki2', 0).service.svc_data['to'],
            ['0', '0'])
        self.assertEqual(
            d.get_unit_placement('mediawiki3', 0).service.svc_data['to'],
            ['mediawiki1/0', 'mediawiki1/1'])

    def test_parse_placement_v4(self):
        # Short-cut to winding up with a valid placement.
        d = self.get_deployment_v4('simple.yaml')
        placement = d.get_unit_placement('mysql', {})

        c, p, u = placement._parse_placement('mysql')
        self.assertEqual(c, None)
        self.assertEqual(p, 'mysql')
        self.assertEqual(u, None)

        c, p, u = placement._parse_placement('mysql/1')
        self.assertEqual(c, None)
        self.assertEqual(p, 'mysql')
        self.assertEqual(u, '1')

        c, p, u = placement._parse_placement('lxc:mysql')
        self.assertEqual(c, 'lxc')
        self.assertEqual(p, 'mysql')
        self.assertEqual(u, None)

    def test_validate_v4(self):
        d = self.get_deployment_v4('validate.yaml')
        placement = d.get_unit_placement('mysql', {})
        feedback = placement.validate()
        self.assertEqual(feedback.get_errors(), [
            'Invalid container type: asdf service: mysql placement: asdf:0',
            'Service placement to machine not supported: mysql to asdf:0',
            'Invalid service placement: mysql to lxc:asdf',
            'Service placement to machine not supported: mysql to 1',
            'Service unit does not exist: mysql to wordpress/3',
            'Invalid service placement: mysql to asdf'])

    def test_get_unit_placement_v4_simple(self):
        d = self.get_deployment_v4('simple.yaml')
        placement = d.get_unit_placement('mysql', {})
        self.assertEqual(placement.get(0), None)

        placement = d.get_unit_placement('mediawiki', {})
        self.assertEqual(placement.get(0), None)

    def test_get_unit_placement_v4_placement(self):
        d = self.get_deployment_v4('placement.yaml')
        machines = {
            '1': 1,
            '2': 2,
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', {})
        d.set_machines(machines)
        self.assertEqual(placement.get(0), 2)

        placement = d.get_unit_placement('mediawiki', {})
        self.assertEqual(placement.get(0), 1)

    def test_get_unit_placement_v4_hulk_smash(self):
        d = self.get_deployment_v4('hulk-smash.yaml')
        machines = {
            '1': 1,
        }
        status = {
            'services': {
                'mediawiki': {
                    'units': {
                        'mediawiki/1': {'machine': 1}
                    }
                }
            }
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), 1)

        placement = d.get_unit_placement('mediawiki', status)
        self.assertEqual(placement.get(0), 1)

    def test_get_unit_placement_v4_hulk_smash_nounits(self):
        d = self.get_deployment_v4('hulk-smash-nounits.yaml')
        machines = {
            '1': 1,
        }
        status = {
            'services': {
                'mediawiki': {
                    'units': {
                        'mediawiki/1': {'machine': 1}
                    }
                }
            }
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), 1)

        placement = d.get_unit_placement('mediawiki', status)
        self.assertEqual(placement.get(0), 1)

    def test_get_unit_placement_v4_hulk_smash_nounits_nomachines(self):
        d = self.get_deployment_v4('hulk-smash-nounits-nomachines.yaml')
        machines = {
            '1': 1,
        }
        status = {
            'services': {
                'mediawiki': {
                    'units': {
                        'mediawiki/1': {'machine': 1}
                    }
                }
            }
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), 1)

        # Since we don't have a placement, even with the status, this should
        # still be None.
        placement = d.get_unit_placement('mediawiki', status)
        self.assertEqual(placement.get(0), None)

    def test_get_unit_placement_v4_container(self):
        d = self.get_deployment_v4('container.yaml')
        machines = {
            '1': 1,
        }
        status = {
            'services': {
                'mediawiki': {
                    'units': {
                        'mediawiki/1': {'machine': 1},
                    }
                }
            }
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get(0), 'lxc:1')

        placement = d.get_unit_placement('mediawiki', status)
        self.assertEqual(placement.get(0), 1)

    def test_get_unit_placement_v4_container_new(self):
        d = self.get_deployment_v4('container-new.yaml')
        machines = {
            '1': 1,
            'mysql/0': 2
        }
        status = {
            'services': {
                'mediawiki': {
                    'units': {
                        'mediawiki/1': {'machine': 1}
                    }
                }
            }
        }

        d.set_machines(machines)

        placement = d.get_unit_placement('mysql', status)
        self.assertEqual(placement.get_new_machines_for_containers(),
            ['mysql/0'])
        self.assertEqual(placement.get(0), 'lxc:2')

        placement = d.get_unit_placement('mediawiki', status)
        self.assertEqual(placement.get(0), 1)

    def test_multiple_relations_no_weight(self):
        data = {"relations": {"wordpress": {"consumes": ["mysql"]},
                              "nginx": {"consumes": ["wordpress"]}}}
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('nginx', 'wordpress'), ('wordpress', 'mysql')],
            list(d.get_relations()))

    def test_multiple_relations_weighted(self):
        data = {
            "relations": {
                "keystone": {
                    "weight": 100,
                    "consumes": ["mysql"]
                },
                "nova-compute": {
                    "weight": 50,
                    "consumes": ["mysql"]
                },
                "glance": {
                    "weight": 70,
                    "consumes": ["mysql"]
                },
            }
        }
        d = Deployment("foo", data, include_dirs=())
        self.assertEqual(
            [('keystone', 'mysql'), ('glance', 'mysql'),
             ('nova-compute', 'mysql')], list(d.get_relations()))

    def test_getting_service_names(self):
        # It is possible to retrieve the service names.
        deployment = self.get_named_deployment_v3("stack-placement.yaml", "stack")
        service_names = deployment.get_service_names()
        expected_service_names = [
            'ceph', 'mysql', 'nova-compute', 'quantum', 'semper', 'verity', 'lxc-service']
        self.assertEqual(set(expected_service_names), set(service_names))

    def test_resolve_config_handles_empty_options(self):
        """resolve_config should handle options being "empty" lp:1361883"""
        deployment = self.get_named_deployment_v3("negative.cfg", "negative")
        self.assertEqual(
            deployment.data["services"]["foo"]["options"], {})
        deployment.resolve_config()

    def test_resolve_config_handles_none_options(self):
        """resolve_config should handle options being "none" lp:1361883"""
        deployment = self.get_named_deployment_v3("negative.yaml", "negative")
        self.assertEqual(
            deployment.data["services"]["foo"]["options"], None)
        deployment.resolve_config()
