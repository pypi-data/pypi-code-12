class Instance(object):

    def __init__(self, eureka_information):
        self._eureka_information = eureka_information

    def get(self, value_path):
        parts = value_path.split(".")
        info = self._eureka_information

        for part in parts:
            if not isinstance(info, dict):
                raise KeyError
            result = info[part]
            info = result

        return result

    @property
    def port(self):
        return self.get("port.$")

    @property
    def port_enabled(self):
        return self.get("port.@enabled") == "true"

    @property
    def secure_port(self):
        return self.get("securePort.$")

    @property
    def secure_port_enabled(self):
        return self.get("securePort.@enabled") == "true"

    @property
    def vip_address(self):
        return self.get("vipAddress")

    @property
    def secure_vip_address(self):
        return self.get("secureVipAddress")

    @property
    def ip_address(self):
        return self.get("ipAddr")

    @property
    def hostname(self):
        return self.get("hostName")


class Application(object):

    @classmethod
    def from_info(cls, eureka_information):
        name = eureka_information["name"]

        instances_info = eureka_information["instance"]

        if not isinstance(instances_info, list):
            instances_info = [instances_info]

        instances = [Instance(info) for info in instances_info]
        return cls(name, instances)

    def __init__(self, name, instances):
        self.name = name
        self.instances = instances


class ApplicationCollection(object):

    @classmethod
    def from_info(cls, eureka_information):
        applications = {}

        for app_info in eureka_information:
            app = Application.from_info(app_info)
            applications[app.name] = app

        return cls(applications)

    def __init__(self, applications):
        self._applications = applications

    def __iter__(self):
        return self._applications.itervalues()

    def __contains__(self, name):
        return name in self._applications

    def __len__(self):
        return len(self._applications)

    def get(self, name):
        return self._applications.get(name)
