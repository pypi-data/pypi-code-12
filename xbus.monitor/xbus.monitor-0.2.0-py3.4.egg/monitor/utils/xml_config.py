from xml.etree import ElementTree

from xbus.monitor.models.monitor import DBSession
from xbus.monitor.models.monitor import Role
from xbus.monitor.models.monitor import Service
from xbus.monitor.models.monitor import Emitter
from xbus.monitor.models.monitor import EventType
from xbus.monitor.models.monitor import EmitterProfile
from xbus.monitor.models.monitor import EventNode


def load_config(raw_xml):

    root = ElementTree.fromstring(raw_xml)
    session = DBSession()
    services = {}
    events = {}
    profiles = {}

    for service_elem in root.findall('service'):
        name = service_elem.get('name')
        consumer = service_elem.get('consumer', False)
        desc = service_elem.text.strip()
        q = session.query(Service)
        q = q.filter(Service.name == name)
        service = q.first()
        if not service:
            service = Service(name=name)
            session.add(service)
        service.consumer = consumer
        service.description = desc
        services[name] = service

    for role_elem in root.findall('role'):
        login = role_elem.get('login')
        if not login:
            login = role_elem.get('name')
        service_name = role_elem.get('service')
        service = services.get(service_name)
        if not service:
            q1 = session.query(Service)
            q1 = q1.filter(Service.name == service_name)
            service = q1.first()
            if not service:
                raise Exception('Unknown service {}'.format(service_name))
            services[service_name] = service
        q2 = session.query(Role)
        q2 = q2.filter(Role.login == login)
        role = q2.first()
        if not role:
            role = Role(login=login)
            session.add(role)
        role.service = service

    for event_elem in root.findall('event_type'):
        name = event_elem.get('name')
        desc = event_elem.text.strip()
        q1 = session.query(EventType)
        q1 = q1.filter(EventType.name == name)
        event = q1.first()
        if not event:
            event = EventType(name=name)
            session.add(event)
        service.description = desc
        events[name] = event

        elem_levels = [iter(event_elem)]
        node_levels = [event_elem]
        while elem_levels:

            try:
                elem = next(elem_levels[-1])
            except StopIteration:
                del elem_levels[-1]
                del node_levels[-1]
                continue

            if len(node_levels) > 1:
                parents = [node_levels[-1]]
                start = False
            else:
                parents = []
                start = True

            service_name = elem.get('service')
            service = services.get(service_name)
            if not service:
                q2 = session.query(Service)
                q2 = q2.filter(Service.name == service_name)
                service = q2.first()
                if not service:
                    raise Exception('Unknown service {}'.format(service_name))
                services[service_name] = service

            node = EventNode(
                type=event, service=service, parents=parents, start=start
            )
            if elem.tag == 'worker':
                node_levels.append(node)
                elem_levels.append(iter(elem))

    for profile_elem in root.findall('profile'):
        name = profile_elem.get('name')
        desc = profile_elem.text.strip()

        event_types = []
        for type_elem in profile_elem.findall('event_type'):
            type_name = type_elem.get('name')
            event_type = events.get(type_name)
            if not event_type:
                q1 = session.query(EventType)
                q1 = q1.filter(EventType.name == type_name)
                event_type = q1.first()
                if not event_type:
                    raise Exception('Unknown event type {}'.format(type_name))
                events[type_name] = event_type
            event_types.append(event_type)

        q2 = session.query(EmitterProfile)
        q2 = q2.filter(EmitterProfile.name == name)
        profile = q2.first()
        if not profile:
            profile = EmitterProfile(name=name)
            session.add(profile)
        profile.description = desc
        profile.event_types = event_types
        profiles[name] = profile

    for emitter_elem in root.findall('emitter'):
        login = emitter_elem.get('login')
        if not login:
            login = emitter_elem.get('name')

        profile_name = emitter_elem.get('profile')
        profile = services.get(profile_name)
        if not profile:
            q1 = session.query(EmitterProfile)
            q1 = q1.filter(EmitterProfile.name == profile_name)
            profile = q1.first()
            if not profile:
                raise Exception('Unknown profile {}'.format(profile_name))
            profiles[profile_name] = profile
        q2 = session.query(Emitter)
        q2 = q2.filter(Emitter.login == login)
        emitter = q2.first()
        if not emitter:
            emitter = Emitter(login=login)
            session.add(emitter)
        emitter.profile = profile
