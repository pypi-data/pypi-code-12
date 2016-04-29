#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""SpineML Bundle Module
This modual will form a convience class to bundle together related SpineML
objects into a single standard object which can be easily passed between 
programs. The bundle will be able to interact with premade spineML objects
through the other support classes, or parse directly from XML

TODO:
## export all as a loop through
## export each element, as a pass through
## import a project file
"""
import os
import pdb

import smlExperiment # SpineML layer classes 	
import smlNetwork          
import smlComponent  

class Bundle(object):
    """Bundle instances are a container class for the various spineML specifications.
    Each specification is stored a list of objects.
    """

    def __init__(self, experiments=None, networks=None, components=None):
        self.experiments = []
        self.components = []
        self.networks = []
        self.index = {}

        if type(experiments) is not type(None):
            if type(experiments) is smlExperiment.SpineMLType:
                self.experiments.append(experiments)
            elif type(experiments) is list:
                for e in experiments:
                    if type(e) is not smlExperiment.SpineMLType:
                        raise TypeError('Invalid Experiment Input: %s' % str(type(e)))
                    else:
                        self.experiments.append(e)
            else:
                raise TypeError('Invalid Experiment Input: %s' % str(type(experiments)))

        if type(networks) is not type(None):
            if type(networks) is smlNetwork.SpineMLType:
                self.networks.append(networks)
            elif type(networks) is list:
                for n in networks:
                    if type(n) is not smlNetwork.SpineMLType:
                        raise TypeError('Invalid Network Input: %s' % str(type(n)))
                    else:
                        self.networks.append(n)
            else:
                raise TypeError('Invalid Network Input: %s' % str(type(networks)))

        if type(components) is not type(None):
            if type(components) is smlComponent.SpineMLType:
                self.components.append(components)
            elif type(components) is list:
                for c in components:
                    if type(c) is not smlComponent.SpineMLType:
                        raise TypeError('Invalid Component Input: %s' % str(type(c)))
                    else:
                        self.components.append(c)
            else:
                raise TypeError('Invalid Component Input: %s' % str(type(components)))

    def add_experiment(self, experiment,recursive=False):
        """Add a SpineML Experiment stored as SpineMLType types, to the bundle
            Setting recursive=True will enable the experiment to add further subcomponents 
            which it accesses, such as the network file and the component file.

            Adding an experiment using the recursive option also builds an index, which
            may provide a more organic structure             

        """
        if type(experiment) is smlExperiment.SpineMLType:
            self.experiments.append(experiment)
        elif type(experiment) is str:
            exp_obj = smlExperiment.parse(experiment,True)
            self.experiments.append(exp_obj)
            exp_file = os.path.basename(experiment)

            # build up the experiment index
            self.index[exp_file] = {}
            self.index[exp_file]['experiment'] = {exp_file:exp_obj}
            
            if recursive:
                # Add the linked model files if recursive is set to true.
                path =  os.path.dirname(experiment) + '/'
                if path == '/':
                    path = ''
                
                for e in exp_obj.Experiment:
                    self.add_network(path+e.Model.network_layer_url,True,exp_file)

        else:
            raise TypeError('Invalid Experiment Input: %s' % str(type(experiment)))
        
        



    def add_network(self, network,recursive=False,index=None):
        """Add a SpineML Network stored as a SpineMLType, to the bundle

            When building an index recursively, pass the experiment file name as the index
        """

        if type(network) is smlNetwork.SpineMLType:
            self.networks.append(network)
        elif type(network) is str:
            net_file = os.path.basename(network)
            path =  os.path.dirname(network) + '/'
            if path == '/':
                    path = ''

            net_obj = smlNetwork.parse(network,True)
            self.networks.append(net_obj)

            if recursive:
                if index is not None:
                    self.index[index]['network'] = {net_file:net_obj}                    

                # Add the linked component files if recursive is set to true
                for n in net_obj.Population:
                    self.add_component(smlComponent.parse(path + n.Neuron.url,True))
                    if index is not None:
                        self.index[index]['component'] = {n.Neuron.url:self.components[-1]}
        else:
            raise TypeError('Invalid Network Input %s' % str(type(network)))


    def add_component(self, component):
        """Add a SpineML Component of SpineMLType type to the bundle
        """
        if type(component) is smlComponent.SpineMLType:
            self.components.append(component)
        elif type(component) is str:
            self.components.append(smlComponent.parse(component,True)) 
        else:
            raise TypeError('Invalid Component Input %s' % str(type(component)))



