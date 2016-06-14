# -*- coding: utf-8 -*-

# ----------------------------------------------------------------------
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero Public License version 3 as
# published by the Free Software Foundation.
#
# Email: asterocean@gmail.com Author: Hui Gao
# ----------------------------------------------------------------------

from snake_env import *

import json
from datetime import datetime

from nupic.engine import Network
from nupic.encoders import DateEncoder, pass_through_encoder
from nupic.regions.SPRegion import SPRegion
from nupic.regions.TPRegion import TPRegion


class Snake_Brain(object):
    def __init__(self):
        self.nsize = GRID_X * GRID_Y
        self.directiondict = dict(zip(DIRECTIONS,SDR_DIRECTIONS))
        self.network = self.createNetwork()
        pass

    def createNetwork(self):
        """Create the Network instance.

        The network has a sensor region reading data from `snake_game` and passing
        the encoded representation to an SPRegion. The SPRegion output is passed to
        a TPRegion.

        :param snake: a Snake instance to get data from
        :returns: a Network instance ready to run
        """
        network = Network()

        # Our input is sensor data from the snake.
        desireSensor = network.addRegion('desireSensor', 'ScalarSensor',
                                              json.dumps({'n': self.nsize,
                                                          'w': 21,
                                                          'minValue': SNAKE_DESIRE_DIE,
                                                          'maxValue': SNAKE_DESIRE_PEAK,
                                                          'clipInput': True}))
        painSensor = network.addRegion('painSensor', 'ScalarSensor',
                                          json.dumps({'n': self.nsize,
                                                      'w': 21,
                                                      'minValue': 0,
                                                      'maxValue': SNAKE_PAIN_DIE,
                                                      'clipInput': True}))
        timestampSensor = network.addRegion("timestampSensor",
                                            'py.PluggableEncoderSensor', "")

        timestampSensor.getSelf().encoder = DateEncoder(timeOfDay=(21, 9.5),
                                                    name="timestamp_timeOfDay")

        visionSensor = network.addRegion("visionSensor",
                                            'py.PluggableEncoderSensor', "")

        visionSensor.getSelf().encoder = pass_through_encoder.PassThroughEncoder(self.nsize, w=None, name="vision", forced=False,
               verbosity=0)

        directionSensor = network.addRegion("directionSensor",
                                         'py.PluggableEncoderSensor', "")

        directionSensor.getSelf().encoder = pass_through_encoder.PassThroughEncoder(self.nsize, w=None, name="direction",
                                                                             forced=False,
                                                                             verbosity=0)
        desireSensorN = desireSensor.getParameter('n')
        painSensorN = painSensor.getParameter('n')
        directionSensorN = directionSensor.getSelf().encoder.getWidth()
        visionSensorN = visionSensor.getSelf().encoder.getWidth()
        timestampEncoderN = timestampSensor.getSelf().encoder.getWidth()
        inputWidth = desireSensorN + painSensorN + visionSensorN + directionSensorN + timestampEncoderN

        network.addRegion("sp", "py.SPRegion",
                          json.dumps({
                              "spatialImp": "cpp",
                              "globalInhibition": 1,
                              "columnCount": 2048,
                              "inputWidth": inputWidth,
                              "numActiveColumnsPerInhArea": 40,
                              "seed": 1956,
                              "potentialPct": 0.8,
                              "synPermConnected": 0.1,
                              "synPermActiveInc": 0.0001,
                              "synPermInactiveDec": 0.0005,
                              "maxBoost": 1.0,
                          }))

        #
        # Input to the Spatial Pooler
        #
        network.link("visionSensor", "sp", "UniformLink", "")
        network.link("directionSensor", "sp", "UniformLink", "")
        network.link("desireSensor", "sp", "UniformLink", "")
        network.link("painSensor", "sp", "UniformLink", "")
        network.link("timestampSensor", "sp", "UniformLink", "")

        #
        # Add a TPRegion, a region containing a Temporal Memory
        #
        network.addRegion("tm", "py.TPRegion",
                          json.dumps({
                              "columnCount": 2048,
                              "cellsPerColumn": 32,
                              "inputWidth": 2048,
                              "seed": 1960,
                              "temporalImp": "cpp",
                              "newSynapseCount": 20,
                              "maxSynapsesPerSegment": 32,
                              "maxSegmentsPerCell": 128,
                              "initialPerm": 0.21,
                              "permanenceInc": 0.1,
                              "permanenceDec": 0.1,
                              "globalDecay": 0.0,
                              "maxAge": 0,
                              "minThreshold": 9,
                              "activationThreshold": 12,
                              "outputType": "normal",
                              "pamLength": 3,
                          }))

        network.link("sp", "tm", "UniformLink", "")
        network.link("tm", "sp", "UniformLink", "", srcOutput="topDownOut", destInput="topDownIn")

        # Add the AnomalyRegion on top of the TPRegion
        network.addRegion("anomalyRegion", "py.AnomalyRegion", json.dumps({}))

        network.link("sp", "anomalyRegion", "UniformLink", "",
                     srcOutput="bottomUpOut", destInput="activeColumns")
        network.link("tm", "anomalyRegion", "UniformLink", "",
                     srcOutput="topDownOut", destInput="predictedColumns")

        # Enable topDownMode to get the predicted columns output
        network.regions['tm'].setParameter("topDownMode", True)
        # Enable inference mode so we get predictions
        network.regions['tm'].setParameter("inferenceMode", True)

        return network


    def runNetwork(self,snakegame):
        """Run the network and write output to writer.

        :param network: a Network instance to run
        :param writer: a csv.writer instance to write output to
        """

        desireSensor = self.network.regions['desireSensor']
        painSensor = self.network.regions['painSensor']
        visionSensor = self.network.regions['visionSensor']
        directionSensor = self.network.regions['directionSensor']
        timestampSensor = self.network.regions['timestampSensor']
        anomalyRegion = self.network.regions['anomalyRegion']

        desireSensor.setParameter('sensedValue', snakegame.snake.desire)
        painSensor.setParameter('sensedValue', snakegame.snake.pain)
        visionSensor.getSelf().setSensedValue(snakegame.getvisionsdr())
        directionSensor.getSelf().setSensedValue(self.directiondict[snakegame.snake.direction])

        # For Python encoders, circumvent the Network API.
        # The inputs are often crazy Python types, for example:
        t = datetime.now()
        timestampSensor.getSelf().setSensedValue(t)

        self.network.run(1)

        anomalyScore = anomalyRegion.getOutputData('rawAnomalyScore')[0]
        print "Steps: %s, Anomaly: %f, Pain: %s, Desire: %s" % (snakegame.steps, anomalyScore, snakegame.snake.pain, snakegame.snake.desire)


if __name__ == "__main__":
    print "run snake_nupic instead"

