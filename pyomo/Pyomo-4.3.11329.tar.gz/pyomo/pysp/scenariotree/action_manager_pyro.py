#  _________________________________________________________________________
#
#  Pyomo: Python Optimization Modeling Objects
#  Copyright (c) 2014 Sandia Corporation.
#  Under the terms of Contract DE-AC04-94AL85000 with Sandia Corporation,
#  the U.S. Government retains certain rights in this software.
#  This software is distributed under the BSD License.
#  _________________________________________________________________________

__all__ = ("ScenarioTreeActionManagerPyro",)

import time
import itertools
from collections import defaultdict

import pyutilib.pyro
from pyutilib.pyro import using_pyro3, using_pyro4, TaskProcessingError
from pyutilib.pyro import Pyro as _pyro
from pyutilib.pyro.util import _connection_problem
from pyomo.opt.parallel.manager import ActionStatus
from pyomo.opt.parallel.pyro import PyroAsynchronousActionManager

import six
from six import advance_iterator, iteritems, itervalues

#
# a specialized asynchronous action manager for the SPPyroScenarioTreeServer
#

class ScenarioTreeActionManagerPyro(PyroAsynchronousActionManager):

    def __init__(self, *args, **kwds):
        super(ScenarioTreeActionManagerPyro, self).__init__(*args, **kwds)
        # the SPPyroScenarioTreeServer objects associated with
        # this manager
        self.server_pool = []
        self._server_name_to_dispatcher_name = {}
        self._dispatcher_name_to_server_names = {}

    def close(self):
        """Close the manager."""
        if len(self.server_pool):
            self.release_servers()
        super(ScenarioTreeActionManagerPyro, self).close()

    def acquire_servers(self, servers_requested, timeout=None):

        if self._verbose:
            print("Attempting to acquire %s scenario tree servers"
                  % (servers_requested))
            if timeout is None:
                print("Timeout has been disabled")
            else:
                print("Automatic timeout in %s seconds" % (timeout))

        assert len(self.server_pool) == 0
        assert len(self._dispatcher_name_to_client) == 0
        assert len(self._server_name_to_dispatcher_name) == 0
        assert len(self._dispatcher_name_to_server_names) == 0
        assert len(self._dispatcher_proxies) == 0
        #
        # This process consists of the following steps:
        #
        # (1) Obtain the list of dispatchers from the nameserver
        # (2) Acquire all workers currently registered on each dispatcher
        # (3) Repeat (1) and (2) until we reach the timeout (if it exists)
        #     or until we obtain the number of servers requested
        # (4) Release any servers we don't need on dispatchers
        #
        wait_start = time.time()
        dispatcher_registered_servers = defaultdict(list)
        dispatcher_servers_to_release = defaultdict(list)
        dispatcher_proxies = {}
        servers_acquired = 0
        while servers_acquired < servers_requested:

            if (timeout is not None) and \
               ((time.time()-wait_start) > timeout):
                print("Timeout reached before %s servers could be acquired. "
                      "Proceeding with %s servers."
                      % (servers_requested, servers_acquired))
                break

            try:
                dispatchers = pyutilib.pyro.util.get_dispatchers(
                    host=self.host,
                    port=self.port,
                    caller_name="Client")
            except _connection_problem:
                print("Failed to obtain one or more dispatchers from nameserver")
                continue
            for (name, uri) in dispatchers:
                dispatcher = None
                server_names = None
                if name not in dispatcher_proxies:
                    # connect to the dispatcher
                    if using_pyro3:
                        dispatcher = _pyro.core.getProxyForURI(uri)
                    else:
                        dispatcher = _pyro.Proxy(uri)
                        dispatcher._pyroTimeout = 10
                    try:
                        server_names = dispatcher.acquire_available_workers()
                    except _connection_problem:
                        if using_pyro4:
                            dispatcher._pyroRelease()
                        else:
                            dispatcher._release()
                        continue
                    dispatcher_proxies[name] = dispatcher
                    if using_pyro4:
                        dispatcher._pyroTimeout = None
                else:
                    dispatcher = dispatcher_proxies[name]
                    server_names = dispatcher.acquire_available_workers()

                # collect the list of registered PySP workers
                servers_to_release = dispatcher_servers_to_release[name]
                registered_servers = dispatcher_registered_servers[name]
                for server_name in server_names:
                    if server_name.startswith("ScenarioTreeServerPyro_"):
                        registered_servers.append(server_name)
                    else:
                        servers_to_release.append(server_name)

                if (timeout is not None) and \
                   ((time.time()-wait_start) > timeout):
                    break

            servers_acquired = sum(len(_serverlist) for _serverlist
                                   in itervalues(dispatcher_registered_servers))

        for name, servers_to_release in iteritems(dispatcher_servers_to_release):
            dispatcher_proxies[name].release_acquired_workers(servers_to_release)
        del dispatcher_servers_to_release

        #
        # Decide which servers we will utilize and do this in such a way
        # as to balance the workload we place on each dispatcher
        #
        server_to_dispatcher_map = {}
        dispatcher_servers_utilized = defaultdict(list)
        servers_utilized = 0
        dispatcher_names = itertools.cycle(dispatcher_registered_servers.keys())
        while servers_utilized < min(servers_requested, servers_acquired):
            name = advance_iterator(dispatcher_names)
            if len(dispatcher_registered_servers[name]) > 0:
                servername = dispatcher_registered_servers[name].pop()
                server_to_dispatcher_map[servername] = name
                dispatcher_servers_utilized[name].append(servername)
                servers_utilized += 1

        # copy the keys as we are modifying this list
        dispatcher_proxies_byURI = {}
        for name in list(dispatcher_proxies.keys()):
            dispatcher = dispatcher_proxies[name]
            servers = dispatcher_servers_utilized[name]
            if len(dispatcher_registered_servers[name]) > 0:
                # release any servers we do not need
                dispatcher.release_acquired_workers(
                    dispatcher_registered_servers[name])
            if len(servers) == 0:
                # release the proxy to this dispatcher,
                # we don't need it
                if using_pyro4:
                    dispatcher._pyroRelease()
                else:
                    dispatcher._release()
                del dispatcher_proxies[name]
            else:
                # when we initialize a client directly with a dispatcher
                # proxy it does not need to know the nameserver host or port
                client = self._create_client(dispatcher=dispatcher)
                self._dispatcher_name_to_server_names[client.URI] = servers
                dispatcher_proxies_byURI[client.URI] = dispatcher
                for servername in servers:
                    self._server_name_to_dispatcher_name[servername] = client.URI
                    self.server_pool.append(servername)
        self._dispatcher_proxies = dispatcher_proxies_byURI

    def release_servers(self):

        if self._verbose:
            print("Releasing scenario tree servers")

        for name in self._dispatcher_proxies:
            dispatcher = self._dispatcher_proxies[name]
            servers = self._dispatcher_name_to_server_names[name]
            # tell dispatcher that the servers we have acquired are no
            # longer needed
            dispatcher.release_acquired_workers(servers)

        self.server_pool = []
        self._server_name_to_dispatcher_name = {}
        self._dispatcher_name_to_server_names = {}

    #
    # Abstract Methods
    #

    def _get_dispatcher_name(self, queue_name):
        return self._server_name_to_dispatcher_name[queue_name]

    def _get_task_data(self, ah, **kwds):
        return kwds

    def _download_results(self):

        found_results = False
        for client in itervalues(self._dispatcher_name_to_client):
            if len(self._dispatcher_name_to_client) == 1:
                # if there is a single dispatcher then we can do
                # a more efficient blocking call
                results = client.get_results(override_type=client.CLIENTNAME,
                                             block=True,
                                             timeout=None)
            else:
                results = client.get_results(override_type=client.CLIENTNAME,
                                             block=False)
            if len(results) > 0:
                found_results = True
                for task in results:
                    self.queued_action_counter -= 1
                    ah = self.event_handle.get(task['id'], None)
                    if ah is None:
                        # if we are here, this is really bad news!
                        raise RuntimeError(
                            "The %s found results for task with id=%s"
                            " - but no corresponding action handle "
                            "could be located!" % (type(self).__name__, task['id']))
                    if type(task['result']) is TaskProcessingError:
                        ah.status = ActionStatus.error
                        self.event_handle[ah.id].update(ah)
                        raise RuntimeError(
                            "SPPyroScenarioTreeServer reported a processing error "
                            "for task with id=%s. Reason: \n%s"
                            % (task['id'], task['result'].args[0]))
                    else:
                        ah.status = ActionStatus.done
                        self.event_handle[ah.id].update(ah)
                        self.results[ah.id] = task['result']

        if not found_results:
            # If the queues are all empty, wait some time for things to
            # fill up. Constantly pinging dispatch servers wastes their
            # time, and inhibits task server communication. The good
            # thing about queues_to_check is that it simultaneously
            # grabs information for any queues with results => one
            # client query can yield many results.

            # TBD: We really need to parameterize the time-out value,
            #      but it isn't clear how to propagate this though the
            #      solver manager interface layers.
            time.sleep(0.01)
