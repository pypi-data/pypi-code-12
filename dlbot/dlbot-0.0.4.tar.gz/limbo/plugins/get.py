"""!get <dashboards|agents|alerts> will return a list of items from Dataloop"""
import os
import re
import yaml
from dlcli import api

stream = open(os.path.join(os.path.expanduser("~"), "dlcli.yaml"), 'r')
settings = yaml.load(stream)


def dashboards():
    response = ''
    for d in api.get_dashboards(**settings):
        response += d['name'] + '\n'
    return response


def agents():
    response = ''
    for a in api.get_agents(**settings):
        response += a['name'] + '\n'
    return response


def alerts():
    triggered = False
    for r in api.rules.get_rules(**settings):
        for criteria in api.rules.get_criteria(rule=r['name'], **settings):
            if criteria['condition']['threshold']:
                criteria_type = criteria['scopes'][0]['type']
                if criteria_type == 'tag' or criteria_type == 'agent':
                    scope_key = 'id'
                else:
                    scope_key = 'name'
                message = "on %s %s %s %d for %d seconds" % (
                    criteria['scopes'][0]['type'],
                    criteria['scopes'][0][scope_key],
                    criteria['condition']['operator'],
                    criteria['condition']['threshold'],
                    criteria['condition']['timeout'])
            else:
                criteria_type = criteria['scopes'][0]['type']
                if criteria_type == 'tag' or criteria_type == 'agent':
                    scope_key = 'id'
                else:
                    scope_key = 'name'
                message = 'on %s %s for %d seconds' % (
                    criteria['scopes'][0]['type'],
                    criteria['scopes'][0][scope_key],
                    criteria['condition']['timeout'])

            if criteria['state'] == 'hit':
                triggered = True
                agent_names = []
                triggered_by = criteria['triggered_by']
                for agent_id in triggered_by:
                    agent_names.append(api.agents.get_agent_name_from_id(agent_id=agent_id, **settings))
                return '%s %s %s triggered by %s' % (r['name'], criteria['metric'], message, ','.join(map(str, agent_names)))
    if not triggered:
        return "all clear! no alert rule criteria are triggered"


def on_message(msg, server):
    text = msg.get("text", "")
    match = re.findall(r"!get( .*)?", text)
    if not match:
        return
    searchterm = match[0]

    if searchterm.strip() == 'dashboards':
        return dashboards()

    if searchterm.strip() == 'agents':
        return agents()

    if searchterm.strip() == 'alerts':
        return alerts()
