
import logging
import os.path as osp
import sys
import yaml

from libcloud.compute import providers

DEFAULT_HOST_ALIASES = ["{node_name}.{project_name}"]

class Project(object):
    """Proxy around Apache LibCloud provider

    """
    def __init__(self, name, email_account, provider=None, pem_file=None, aliases=None):
        """
        :param name: Cloud project name
        :param email_account: service account name having proper permissions
        :param pem_file: absolute path to JSON key
        :param aliases: list of additional aliases to create, for instance {node_name}.c.{project_name}.internal
        """
        driver = providers.get_driver(provider)
        logging.info("Creating driver over {} {} project".format(provider, name))
        self.driver = driver(
            email_account,
            pem_file,
            project=name
        )
        self.provider = provider
        self.aliases = aliases or DEFAULT_HOST_ALIASES

    def write_dns_file(self, ostr):
        nodes = self.driver.list_nodes()
        if not any(nodes):
            return
        for alias in self.aliases:
            domain = self.format_node(nodes[0], alias).split('.', 1)[-1]
            ostr.write('$ORIGIN ')
            ostr.write(domain)
            ostr.write(".\n$TTL 1h\n")
            for node in nodes:
                name = self.format_node(node, alias).split('.', 1)[0]
                ostr.write('{} IN A {}\n'.format(name, node.public_ips[0]))

    def format_node(self, node, fmt):
        return fmt.format(**{
            'node_name': node.name,
            'project_name': self.driver.project
        })

    def get_hostip_tuples(self):
        logging.info("Retrieving {} {} nodes".format(self.provider, self.driver.project))
        for node in self.driver.list_nodes():
            if any(node.public_ips):
                hosts = []
                for alias in self.aliases:
                    hosts.append(alias.format(**{
                        'node_name': node.name,
                        'project_name': self.driver.project
                        }))
                yield (tuple(hosts), node.public_ips[0])
