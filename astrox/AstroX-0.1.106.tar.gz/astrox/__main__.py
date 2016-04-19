from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory

from sense_hat import SenseHat
astroPi = SenseHat()
astroPi.set_imu_config(True, True, True)

import json
from twisted.internet import reactor, task
from twisted.internet.defer import Deferred, \
    inlineCallbacks, \
    returnValue

import sched, time

class AstroPiServerProtocol(WebSocketServerProtocol):
    def updateEnv(self):
        output = json.dumps({'command':'env-update', 'args': {'temperature':astroPi.temperature, 'pressure': astroPi.pressure, 'humidity': astroPi.humidity, 'direction': astroPi.get_compass(), 'orientation': astroPi.get_orientation(), 'accelerometer': astroPi.get_accelerometer_raw(), 'gyroscope': astroPi.get_gyroscope_raw(), 'compass': astroPi.get_compass_raw()}})
        self.sendMessage(output.encode('utf8'))

    def onOpen(self):
        self.l = task.LoopingCall(self.updateEnv)
        self.l.start(0.04)

    def onClose(self, wasClean, code, reason):
        self.l.stop();

    def lowLight(self, lowLight):
        if lowLight == "on":
            astroPi.low_light = True
        else:
            astroPi.low_light = False

    def showMessage(self, args):
        astroPi.show_message(args["message"], text_colour=[int(args["r"]), int(args["g"]), int(args["b"])])
        self.sendMessage(json.dumps({'command': 'message-complete'}).encode('utf8'))

    def onMessage(self, payload, isBinary):
        if not isBinary:
            message = json.loads(payload.decode('utf8'))
	
            {
                'show-message': lambda args: self.showMessage(args),
                'show-letter':  lambda args: astroPi.show_letter(args["letter"], text_colour=[int(args["r"]), int(args["g"]), int(args["b"])]),
                'set-rotation': lambda args: astroPi.set_rotation(int(args["rotation"])),
                'low-light':    lambda args: self.lowLight(args["on"]),
                'led-on':       lambda args: astroPi.set_pixel(int(args["x"]), int(args["y"]), int(args["r"]), int(args["g"]), int(args["b"])),
                'led-off':      lambda args: astroPi.set_pixel(int(args["x"]), int(args["y"]), 0, 0, 0),
                'fill':         lambda args: astroPi.clear(int(args["r"]), int(args["g"]), int(args["b"]))
            }[message["command"]](message["args"])


def main(args=None):
    import sys
    
    from twisted.python import log
    from twisted.internet import reactor
    
    log.startLogging(sys.stdout)
    
    factory = WebSocketServerFactory(u"ws://127.0.0.1:9000")
    factory.protocol = AstroPiServerProtocol
    
    reactor.listenTCP(9000, factory)
    reactor.run()


if __name__ == '__main__':
    main()