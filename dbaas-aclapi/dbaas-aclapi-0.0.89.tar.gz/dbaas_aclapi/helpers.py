# -*- coding: utf-8 -*-
import logging
import copy
from dbaas_aclapi import exceptions

logging.basicConfig()
LOG = logging.getLogger("AclHelpers")
LOG.setLevel(logging.DEBUG)


def build_data_default_options_dict(action, bind_address, database_name,
                                    database_environment):

    description = "{} {} access for database {} in {}".format(
        action, bind_address, database_name, database_environment)

    data = {"kind": "object#acl", "rules": []}
    dafault_options = {"protocol": "tcp",
                       "source": "",
                       "destination": "",
                       "description": description,
                       "action": action,
                       "l4-options": {"dest-port-start": "",
                                      "dest-port-op": "eq"}
                       }
    LOG.info("Default options: {}".format(dafault_options))
    return data, dafault_options


def iter_on_acl_query_results(acl_client, rule):
    query_results = acl_client.query_acls(rule)
    for environment in query_results.get('envs', []):
        for vlan in environment.get('vlans', []):
            environment_id = vlan['environment']
            vlan_id = vlan['num_vlan']
            for rule in vlan.get('rules', []):
                rule_id = rule['id']
                yield environment_id, vlan_id, rule_id


def save_jobs(job_list, job_operation, database):
    from dbaas_aclapi.models import AclApiJob, PENDING
    for job in job_list:
        aclapi_job = AclApiJob(
            job_id=job, job_status=PENDING, job_operation=job_operation,
            database=database, environment=database.environment)
        try:
            aclapi_job.save()
        except Exception as e:
            LOG.warn(e)


def get_user(request=None, user=None, action=None):
    from account.models import User
    if not user:
        try:
            user = request.args[-1]
        except AttributeError:
            user = User.objects.get(username='admin')

    LOG.info("User: {}, action: {}".format(user, action))
    return user


def bind_address(database_bind, acl_client, instances=None, infra_attr_instances=None):
    from dbaas_cloudstack.models import DatabaseInfraAttr
    from dbaas_aclapi.models import (
        CREATED, DatabaseBind, DatabaseInfraInstanceBind, BIND)

    action = "permit"
    database = database_bind.database
    databaseinfra = database.databaseinfra
    acl_environment, acl_vlan = get_bind_env_and_vlan(database_bind)

    data, default_options = build_data_default_options_dict(
        action, database_bind.bind_address, database.name,
        database.environment.name)

    if not instances:
        instances = databaseinfra.instances.all()
    port = instances[0].port

    for instance in instances:
        custom_options = copy.deepcopy(default_options)
        custom_options['source'] = database_bind.bind_address
        custom_options['destination'] = instance.address + '/32'
        custom_options['l4-options']['dest-port-start'] = instance.port
        data['rules'].append(custom_options)

        LOG.debug("Creating bind for instance: {}".format(instance))

        instance_bind = DatabaseInfraInstanceBind(
            instance=instance.address, databaseinfra=databaseinfra,
            bind_address=database_bind.bind_address, instance_port=instance.port)
        instance_bind.save()

        LOG.debug("InstanceBind: {}".format(instance_bind))

    LOG.debug("Instance binds created!")

    if not infra_attr_instances:
        infra_attr_instances = DatabaseInfraAttr.objects.filter(databaseinfra=databaseinfra)

    for instance in infra_attr_instances:
        custom_options = copy.deepcopy(default_options)
        custom_options['source'] = database_bind.bind_address
        custom_options['destination'] = instance.ip + '/32'
        custom_options['l4-options']['dest-port-start'] = port
        data['rules'].append(custom_options)

        LOG.debug("Creating bind for instance: {}".format(instance))

        instance_bind = DatabaseInfraInstanceBind(
            instance=instance.ip, databaseinfra=databaseinfra,
            bind_address=database_bind.bind_address, instance_port=port)
        instance_bind.save()

        LOG.debug("DatabaseInraAttrInstanceBind: {}".format(instance_bind))

    response = acl_client.grant_acl_for(
        environment=acl_environment, vlan=acl_vlan, payload=data)

    if 'jobs' in response:
        save_jobs(response['jobs'], BIND, database)

        DatabaseBind.objects.filter(
            id=database_bind.id).update(bind_status=CREATED)

        DatabaseInfraInstanceBind.objects.filter(
            databaseinfra=database.databaseinfra, bind_address=database_bind.bind_address
        ).update(bind_status=CREATED)

        return True
    else:
        raise exceptions.ACL_API_JOB_MISSING_EXCEPTION


def unbind_address(
    database_bind, acl_client, infra_instances_binds,
    delete_database_bind=True
):
    from dbaas_aclapi.models import UNBIND

    action = "permit"
    database = database_bind.database
    _, default_options = build_data_default_options_dict(
        action, database_bind.bind_address, database.name,
        database.environment.name)

    job_list = []
    for infra_instance_bind in infra_instances_binds:
        custom_options = copy.deepcopy(default_options)
        custom_options['source'] = database_bind.bind_address
        custom_options['destination'] = infra_instance_bind.instance + '/32'
        custom_options['l4-options']['dest-port-start'] = infra_instance_bind.instance_port

        try:
            for environment_id, vlan_id, rule_id in iter_on_acl_query_results(acl_client, custom_options):
                response = acl_client.delete_acl(environment_id, vlan_id, rule_id)
                if 'job' in response:
                    job_list.append(response['job'])
            infra_instance_bind.delete()
        except Exception as e:
            raise Exception("Access {} could not be deleted! Error: {}".format(
                infra_instance_bind, e))
        finally:
            save_jobs(job_list, UNBIND, database)

    if delete_database_bind:
        database_bind.delete()
    return True


def get_bind_env_and_vlan(database_bind):
    return database_bind.bind_address.split('/')


def iter_on_acl_rules(acl_client, rule):
    query_results = acl_client.query_acls(rule)
    for environment in query_results.get('envs', []):
        for vlan in environment.get('vlans', []):
            for rule in vlan.get('rules', []):
                yield rule
