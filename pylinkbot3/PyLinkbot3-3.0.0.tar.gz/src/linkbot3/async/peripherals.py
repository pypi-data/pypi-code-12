import asyncio
import functools
import linkbot3
from .. import _util as util
from .. import peripherals
import weakref

__all__ = [ 'Accelerometer', 
            'Battery',
            'Button',
            'Buzzer',
            'Eeprom',
            'Led',
            'Buzzer',
            'Motor',
            'Motors',
            'Twi',
            ]

class Accelerometer():
    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        self._event_callback = None
        return self

    @asyncio.coroutine
    def values(self):
        '''
        Get the current accelerometer values.

        :rtype: asyncio.Future . The future's result type is (float, float,
            float) representing the x, y, and z axes, respectively. The 
            units of each value are in Earth gravitational units (a.k.a. G's).
        '''
        fut = yield from self._proxy.getAccelerometerData()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__values,
                    user_fut )
                )
        return user_fut

    def __values(self, user_fut, fut):
        user_fut.set_result(
                ( fut.result().x, fut.result().y, fut.result().z )
                )

    @asyncio.coroutine
    def x(self):
        '''
        Get the current x axis value.

        :rtype: asyncio.Future. The future's result type is "float", in units of
            Earth gravitational units (a.k.a. G's)
        '''
        fut = yield from self.values()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__get_index,
                    0,
                    user_fut )
                )
        return user_fut

    @asyncio.coroutine
    def y(self):
        '''
        Get the current y axis value.

        :rtype: asyncio.Future. The future's result type is "float", in units of
            Earth gravitational units (a.k.a. G's)
        '''
        fut = yield from self.values()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__get_index,
                    1,
                    user_fut )
                )
        return user_fut

    @asyncio.coroutine
    def z(self):
        '''
        Get the current z axis value.

        :rtype: asyncio.Future. The future's result type is "float", in units of
            Earth gravitational units (a.k.a. G's)
        '''
        fut = yield from self.values()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__get_index,
                    2,
                    user_fut )
                )
        return user_fut

    def __get_index(self, index, user_fut, fut):
        user_fut.set_result( fut.result()[index] )

    @asyncio.coroutine
    def set_event_handler(self, callback=None, granularity=0.05):
        '''
        Set a callback function to be executed when the accelerometer
        values on the robot change.

        :param callback: async func(x, y, z, timestamp) -> None
        :param granularity: float . The callback will only be called when any
            axis of the accelerometer changes by this many G's of acceleration.
        '''
        if not callback:
            # Remove the event
            try:
                fut = yield from self._proxy.enableAccelerometerEvent(
                        enable=False,
                        granularity=granularity)
                yield from fut
                self._proxy.rb_remove_broadcast_handler('accelerometerEvent')
                self._event_callback = callback
                return fut
            except KeyError:
                # Don't worry if the bcast handler is not there.
                pass

        else:
            self._event_callback = callback
            self._proxy.rb_add_broadcast_handler( 'accelerometerEvent', 
                                                  self.__event_handler )
            rc = yield from self._proxy.enableAccelerometerEvent(
                    enable=True,
                    granularity=granularity )
            return rc

    @asyncio.coroutine
    def __event_handler(self, payload):
        yield from self._event_callback( payload.x, 
                                    payload.y, 
                                    payload.z, 
                                    payload.timestamp)

class Battery():
    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        return self

    @asyncio.coroutine
    def voltage(self):
        ''' Get the current battery voltage. 

        :returns: An asyncio.Future. The result of the future is the current
            battery voltage.
        :rtype: asyncio.Future
        '''
        fut = yield from self._proxy.getBatteryVoltage()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=lambda x:x.v)
        return user_fut

    @asyncio.coroutine
    def percentage(self):
        ''' Return an estimated battery percentage.

        This function estimates the battery charge level based on the current
        voltage of the battery. The battery voltage discharge curve is highly
        non-linear, and this function uses three cubic curve-fit equations to
        generate a "best guess" of the battery level as a percentage.

        See
        https://docs.google.com/spreadsheets/d/1nZYGi2s-gs6waFfvLNPQ9SBCAgTuzwL0sdIo_FG3BQA/edit?usp=sharing
        for the formula, charts, and graphs.

        Also note that both the battery voltage and percentage values returned
        by the robot will be inaccurate while the robot is being charged.

        :returns: A value from 0 to 100 representing the charge of the battery.
        :rtype: asyncio.Future
        '''
        def v_to_percent(v):
            if v > 2.939176:
                p = 100 - ((-1767.563651*v**3) + \
                          (16574.91975*v**2) + \
                          (-51953.36291*v) + \
                          54443.61917)
            elif v > 2.9081037:
                p = 100 - ((-77201.18865*v**3) + \
                          (666450.9575*v**2) + \
                          (-1917865.889*v) + \
                          1839890.523)
            else:
                p = 100 - ((-422.9524082*v**3) + \
                          (3210.382045*v**2) + \
                          (-8135.146192*v) + \
                          6979.444376)
            if p > 100:
                p = 100
            if p < 0:
                p = 0
            return p

        fut = yield from self.voltage()
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, v_to_percent)
        return user_fut

class Button():
    PWR = 0
    A = 1
    B = 2

    UP = 0
    DOWN = 1

    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        self._event_callback = None
        return self

    @asyncio.coroutine
    def values(self):
        '''
        Get the current button values

        :rtype: asyncio.Future . Result type is (int, int, int), indicating the
            button state for the power, A, and B buttons, respectively. The button
            state is one of either Button.UP or Button.DOWN.
        '''
        fut = yield from self._proxy.getButtonState()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__values,
                    user_fut
                    )
                )
        return user_fut

    def __values(self, user_fut, fut):
        pwr = fut.result().mask & 0x01
        a = (fut.result().mask>>1) & 0x01
        b = (fut.result().mask>>2) & 0x01
        user_fut.set_result( (pwr, a, b) )

    @asyncio.coroutine
    def pwr(self):
        '''
        Get the current state of the power button.

        :rtype: either Button.UP or Button.DOWN
        '''
        fut = yield from self._proxy.getButtonState()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__button_values,
                    0,
                    user_fut
                    )
                )
        return user_fut

    @asyncio.coroutine
    def a(self):
        '''
        Get the current state of the 'A' button.

        :rtype: either Button.UP or Button.DOWN
        '''
        fut = yield from self._proxy.getButtonState()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__button_values,
                    1,
                    user_fut
                    )
                )
        return user_fut

    @asyncio.coroutine
    def b(self):
        '''
        Get the current state of the 'B' button.

        :rtype: either Button.UP or Button.DOWN
        '''
        fut = yield from self._proxy.getButtonState()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__button_values,
                    2,
                    user_fut
                    )
                )
        return user_fut

    def __button_values(self, index, user_fut, fut):
        user_fut.set_result((fut.result().mask>>index) & 0x01)

    @asyncio.coroutine
    def set_event_handler(self, callback=None):
        '''
        Set a callback function to be executed when there is a button press or
        release.

        :param callback: func(buttonNo(int), buttonDown(bool), timestamp) -> None
        '''
        self._event_callback = callback
        if not callback:
            # Remove the event
            try:
                fut = yield from self._proxy.enableButtonEvent(
                        enable=False)
                yield from fut
                self._proxy.rb_remove_broadcast_handler('buttonEvent')
                return fut
            except KeyError:
                # Don't worry if the bcast handler is  not there.
                pass

        else:
            self._proxy.rb_add_broadcast_handler( 'buttonEvent', 
                                                  self.__event_handler )
            rc = yield from self._proxy.enableButtonEvent(
                    enable=True)
            return rc

    @asyncio.coroutine
    def __event_handler(self, payload):
        yield from self._event_callback( payload.button, 
                                    payload.state, 
                                    payload.timestamp)

class Buzzer():
    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy 
        return self

    @asyncio.coroutine
    def frequency(self):
        '''
        Get the current buzzer frequency.

        :returns: Frequency in Hz
        :rtype: float
        '''
        fut = yield from self._proxy.getBuzzerFrequency()
        return fut

    @asyncio.coroutine
    def set_frequency(self, hz):
        '''
        Set the buzzer frequency.

        :param hz: A frequency in Hz.
        :type hz: float
        '''
        fut = yield from self._proxy.setBuzzerFrequency(value=hz)
        return fut

class Eeprom():
    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        return self

    @asyncio.coroutine
    def read(self, address, size):
        '''
        Read ```size``` bytes from EEPROM address ```address``` on the robot.

        :param address: The start address to read from
        :type address: int
        :param size: The number of bytes to read
        :type size: int
        :rtype: asyncio.Future(bytearray)
        '''
        fut = yield from self._proxy.readEeprom(address=address, size=size)
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=lambda x: x.data)
        return user_fut

    @asyncio.coroutine
    def write(self, address, bytestring):
        '''
        Write data to the EEPROM.

        WARNING: This function can overwrite important EEPROM data that the
        robot uses to function properly, such as its serial ID, calibration
        values, hardware versioning information, etc. 

        :param address: Start EEPROM address to write to
        :type address: int
        :param bytestring: Bytes to write to EEPROM
        :type bytestring: bytearray or bytes
        :rtype: asyncio.Future
        '''
        fut = yield from self._proxy.writeEeprom(
                address=address,
                data=bytestring )
        return fut

class Led():
    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        return self

    @asyncio.coroutine
    def color(self):
        '''
        Get the current LED color.

        :rtype: (int, int, int) indicating the intensity of the red, green,
            and blue channels. Each intensity is a value between [0,255].
        '''
        fut = yield from self._proxy.getLedColor()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__color,
                    user_fut
                    )
                )
        return user_fut
        
    def __color(self, user_fut, fut):
        word = fut.result().value
        r = (word&0xff0000) >> 16
        g = (word&0x00ff00) >> 8
        b = word&0x0000ff
        user_fut.set_result( (r,g,b) )

    @asyncio.coroutine
    def set_color(self, r, g, b):
        '''
        Set the current LED color.

        :type r: int [0,255]
        :type g: int [0,255]
        :type b: int [0,255]
        '''
        word = b | (g<<8) | (r<<16)
        fut = yield from self._proxy.setLedColor(value=word)
        return fut

class Motor:
    '''
    The asynchronous representation of a Linkbot's motor.

    See also :class:`linkbot3.peripherals.Motor` for the synchronous counterpart.
    '''
    @classmethod
    @asyncio.coroutine
    def create(cls, index, proxy, motors_obj):
        self = cls()
        self._controller = peripherals.Motor.Controller.CONST_VEL
        self._index = index
        self._proxy = proxy
        self._state = peripherals.Motor.State.COAST
        yield from self._poll_state()
        # List of futures that should be set when this joint is done moving
        self._move_waiters = []
        self._motors = motors_obj
        return self

    @asyncio.coroutine
    def accel(self):
        ''' Get the acceleration setting of a motor

        :rtype: float
        :returns: The acceleration setting in units of deg/s/s
        '''
        rc = yield from self.__get_motor_controller_attribute(
                'getMotorControllerAlphaI',
                conv=util.rad2deg
                )
        return rc

    @asyncio.coroutine
    def controller(self):
        '''The movement controller.

        This property controls the strategy with which the motors are moved.
        Legal values are:

        * :const:`linkbot3.peripherals.Motor.Controller.PID`: Move the motors directly with the
          internal PID controller. This is typically the fastest way to get a
          motor from one position to another. The motor may experience some
          overshoot and underdamped response when moving larger distances.
        * :const:`linkbot3.peripherals.Motor.Controller.CONST_VEL`: Move the motor at a constant
          velocity. This motor controller attemts to accelerate and decelerate
          a motor infinitely fast to and from a constant velocity to move the
          motor from one position to the next. The velocity can be controlled
          by setting the property `omega`.
        * :const:`linkbot3.peripherals.Motor.Controller.SMOOTH`: Move the motor with specified
          acceleration, maximum velocity, and deceleration. For this type of
          movement, access maximum velocity with property `omega`,
          acceleration with property `acceleration`, and deceleration with property
          `deceleration`.
        '''
        fut = asyncio.Future()
        fut.set_result(self._controller)
        return fut

    @asyncio.coroutine
    def decel(self):
        ''' Get the deceleration setting of a motor

        :rtype: float
        :returns: The deceleration setting in units of deg/s/s
        '''
        rc = yield from self.__get_motor_controller_attribute(
                'getMotorControllerAlphaF',
                conv=util.rad2deg
                )
        return rc

    @asyncio.coroutine
    def omega(self):
        ''' Get the rotational velocity setting of a motor

        :rtype: float
        :returns: The speed setting of the motor in deg/s
        '''
        rc = yield from self.__get_motor_controller_attribute(
                'getMotorControllerOmega',
                conv=util.rad2deg
                )
        return rc

    @asyncio.coroutine
    def _poll_state(self):
        if (self._index == 1) and (self._proxy.form_factor == linkbot3.FormFactor.I):
            self._state = peripherals.Motor.State.COAST
        elif (self._index == 2) and (self._proxy.form_factor == linkbot3.FormFactor.L):
            self._state = peripherals.Motor.State.COAST
        else:
            fut = yield from self.__get_motor_controller_attribute(
                    'getJointStates' )
            self._state = yield from fut

    @asyncio.coroutine
    def __get_motor_controller_attribute(self, name, conv=lambda x: x):
        # 'conv' is a conversion function, in case the returned values need to
        # be converted to/from radians. Use 'id' for null conversion
        fut = yield from getattr(self._proxy, name)()
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__handle_values_result, conv, user_fut)
                )
        return user_fut

    def __handle_values_result(self, conv, user_fut, fut):
        if fut.cancelled():
            user_fut.cancel()
            return
        results_obj = fut.result()
        values = []
        for v in results_obj.values:
            values.append(conv(v))
        user_fut.set_result(values[self._index])

    @asyncio.coroutine
    def set_accel(self, value):
        ''' Set the acceleration of a motor.

        :param value: The acceleration in deg/s/s
        :type value: float
        
        See :func:`linkbot3.async.peripherals.Motor.accel`
        '''
        rc = yield from self.__set_motor_controller_attribute(
                'setMotorControllerAlphaI',
                util.deg2rad(value)
                )
        return rc

    @asyncio.coroutine
    def set_controller(self, value):
        ''' Set the controller type of a motor. 

        :type value: :class:`linkbot3.Motor.Controller`

        See alse: :func:`linkbot3.async.peripherals.Motor.controller`
        '''
        if value < 1 or value > 3:
            raise RangeError('Motor controller must be a value in range [1,3]')
        self._controller = value
        fut = asyncio.Future()
        fut2 = asyncio.Future()
        fut2.set_result(None)
        fut.set_result(fut2)
        return fut

    @asyncio.coroutine
    def set_decel(self, value):
        ''' Set the deceleration of a motor.

        :param value: Deceleration in deg/s/s
        :type value: float

        See also: :func:`linkbot3.async.peripherals.Motor.decel`
        '''
        rc = yield from self.__set_motor_controller_attribute(
                'setMotorControllerAlphaF',
                util.deg2rad(value)
                )
        return rc

    @asyncio.coroutine
    def set_omega(self, value):
        ''' Set the speed of the motor.

        :param value: The new speed in deg/s
        :type value: float

        See also: :func:`linkbot3.async.peripherals.Motor.omega`
        '''
        rc = yield from self.__set_motor_controller_attribute(
                'setMotorControllerOmega',
                util.deg2rad(value)
                )
        return rc

    @asyncio.coroutine
    def __set_motor_controller_attribute(self, name, value):
        args_obj = self._proxy.rb_get_args_obj(name)
        args_obj.mask = 1<<self._index
        args_obj.values.append(value)
        fut = yield from getattr(self._proxy, name)(args_obj)
        user_fut = asyncio.Future()
        fut.add_done_callback(
                functools.partial(
                    self.__handle_set_attribute,
                    user_fut
                    )
                )
        return user_fut

    @asyncio.coroutine
    def set_event_handler(self, callback=None, granularity=2.0):
        '''
        Set a callback function to be executed when the motor angle
        values on the robot change.

        :param callback: async func(angle, timestamp) -> None
        :param granularity: float . The callback will only be called when a
            motor moves away from its current position by more than
            'granularity' degrees.
        '''
        if not callback:
            # Remove the event
            try:
                args = self._proxy.rb_get_args_obj('enableEncoderEvent')
                names = ['encoderOne', 'encoderTwo', 'encoderThree']
                name = names[self._index]
                getattr(args, name).enable = False
                getattr(args, name).granularity = util.deg2rad(granularity)
                fut = yield from self._proxy.enableEncoderEvent(args)
                yield from fut
                self._event_callback = callback
                return fut
            except KeyError:
                # Don't worry if the bcast handler is not there.
                pass

        else:
            self._motors._callback_handler.set_event_handler(self._index, callback)
            self._proxy.rb_add_broadcast_handler( 'encoderEvent', 
                                                  self._motors._callback_handler.event_handler)
            args = self._proxy.rb_get_args_obj('enableEncoderEvent')
            names = ['encoderOne', 'encoderTwo', 'encoderThree']
            name = names[self._index]
            getattr(args, name).enable = True
            getattr(args, name).granularity = util.deg2rad(granularity)
            fut = yield from self._proxy.enableEncoderEvent(args)
            return fut

    @asyncio.coroutine
    def set_power(self, power):
        '''
        Set the motor's power.

        :type power: int [-255,255]
        '''
        
        args_obj = self._proxy.rb_get_args_obj('move')
        names = ['motorOneGoal', 'motorTwoGoal', 'motorThreeGoal']
        name = names[self._index]
        getattr(args_obj,name).type = peripherals.Motor._MoveType.INFINITE
        getattr(args_obj,name).goal = power
        getattr(args_obj,name).controller = peripherals.Motor.Controller.PID

        fut = yield from self._proxy.move(args_obj)
        return fut

    def __handle_set_attribute(self, user_fut, fut):
        user_fut.set_result( fut.result() )

    def is_moving(self):
        if self._state in [peripherals.Motor.State.COAST, 
                           peripherals.Motor.State.HOLD]:
            return False
        else:
            return True

    @property
    def state(self):
        # The current joint state. One of :class:`Motor.State`
        return self._state
    @state.setter
    def state(self, value):
        assert(value in peripherals.Motor.State.__dict__.values())
        self._state = value
        if not self.is_moving():
            for fut in self._move_waiters:
                fut.set_result(self._state)
            self._move_waiters.clear()

    @asyncio.coroutine
    def begin_accel(self, timeout, v0 = 0.0,
            state_on_timeout=peripherals.Motor.State.COAST):
        ''' Cause a motor to begin accelerating indefinitely. 

        The joint will begin accelerating at the acceleration specified
        previously by :func:`linkbot3.async.peripherals.Motor.accel`. If a 
        timeout is specified, the motor will transition states after the timeout
        expires. The state the motor transitions to is specified by the
        parameter ```state_on_timeout```. 

        If the robot reaches its maximum speed, specified by the function
        :func:`linkbot3.async.peripherals.Motor.set_omega`, it will stop
        accelerating and continue at that speed until the timeout, if any,
        expires.

        :param timeout: Seconds to wait before robot transitions states.
        :type timeout: float
        :param v0: Initial velocity in deg/s
        :type v0: float
        :param state_on_timeout: End state after timeout
        :type state_on_timeout: :class:`linkbot3.peripherals.Motor.State`
        '''
        mask = 1<<self._index
        args_obj = self._proxy.rb_get_args_obj('move')
        names = ['motorOneGoal', 'motorTwoGoal', 'motorThreeGoal']
        for i,name in enumerate(names):
            if mask&(1<<i):
                getattr(args_obj,name).type = self._MoveType.INFINITE
                getattr(args_obj,name).goal = v0
                getattr(args_obj,name).controller = peripherals.Motor.Controller.ACCEL
                getattr(args_obj,name).timeout = timeout
                getattr(args_obj,name).modeOnTimeout = state_on_timeout

        fut = yield from self._proxy.move(args_obj)
        return fut

    @asyncio.coroutine
    def begin_move(self, timeout = 0, forward=True,
            state_on_timeout=peripherals.Motor.State.COAST):
        ''' Begin moving motor at constant velocity

        The joint will begin moving at a constant velocity previously set by
        :func:`linkbot3.async.peripherals.Motor.set_omega`. 

        :param timeout: After ```timeout``` seconds, the motor will transition
            states to the state specified by the parameter
            ```state_on_timeout```.
        :type timeout: float
        :param forward: Whether to move the joint in the positive direction
            (True) or negative direction (False).
        :type forward: bool
        :param state_on_timeout: State to transition to after the motion
            times out.
        :type state_on_timeout: :class:`linkbot3.peripherals.Motor.State`
        '''
        mask = 1<<self._index
        args_obj = self._proxy.rb_get_args_obj('move')
        names = ['motorOneGoal', 'motorTwoGoal', 'motorThreeGoal']
        if forward:
            goal = 1
        else:
            goal = -1
        for i,name in enumerate(names):
            if mask&(1<<i):
                getattr(args_obj,name).type = self._MoveType.INFINITE
                getattr(args_obj,name).goal = goal
                getattr(args_obj,name).controller = peripherals.Motor.Controller.CONST_VEL
                getattr(args_obj,name).timeout = timeout
                getattr(args_obj,name).modeOnTimeout = state_on_timeout

        fut = yield from self._proxy.move(args_obj)
        return fut

    @asyncio.coroutine
    def move(self, angle, relative=True):
        ''' Move the motor.

        :param angle: The angle to move the motor.
        :type angle: float
        :param relative: Determines if the motor should move to an absolute
            position or perform a relative motion. For instance, if the motor is
            currently at a position of 45 degrees, performing a relative move of
            90 degrees will move the motor to 135 degrees, while doing an
            absolute move of 90 degrees will move the motor forward by 45
            degrees until it reaches the absolute position of 90 degrees.
        :type relative: bool
        '''
        return self._motors.move(
                [angle, angle, angle],
                mask=1<<self._index,
                relative=relative)

    @asyncio.coroutine
    def move_wait(self):
        '''
        Wait for a motor to stop moving.

        Returns an asyncio.Future(). The result of the future is set when the
        motor has stopped moving, either by transitioning into a "COAST" state
        or "HOLD" state.
        '''
        yield from self._poll_state()
        fut = asyncio.Future()
        user_fut = asyncio.Future()
        # If we are aready not moving, just return a completed future
        if not self.is_moving():
            user_fut.set_result(self.state)
        else:
            self._move_waiters.append(fut)
            poll_fut = asyncio.ensure_future(self.__poll_movewait())
            fut = asyncio.gather(poll_fut, fut)
            util.chain_futures(fut, user_fut, conv=lambda x: None)
        return user_fut

    @asyncio.coroutine
    def __poll_movewait(self):
        '''
        This internal function is used to poll the state of the motors as long
        as there is a future waiting on :func:`linkbot3.Motor.move_wait`. 
        '''
        while self._move_waiters:
            fut = self._move_waiters[0]
            try:
                yield from asyncio.wait_for(asyncio.shield(fut), 2)
            except asyncio.TimeoutError:
                yield from self._poll_state()
            else:
                continue

class Motors:
    ''' The Motors class.

    This class represents all of the motors on-board a Linkbot. To access an
    individual motor, this class may be indexed. For instance, the line::

        linkbot.motors[0] 

    accesses the first motor on a Linkbot, which is of type
    :class:`linkbot3.async.peripherals.Motor`
    '''

    class _EncoderEventHandler():
        def __init__(self):
            self._handlers = [None, None, None]
        
        @asyncio.coroutine
        def event_handler(self, payload):
            joint = payload.encoder
            value = payload.value
            timestamp = payload.timestamp
            try:
                yield from self._handlers[joint](util.rad2deg(value), timestamp)
            except IndexError as e:
                # Don't care if the callback doesn't exist
                pass
            except TypeError as e:
                pass
            except Exception as e:
                logging.warning('Could not run encoder event handler: {}'
                        .format(str(e)) )
                raise

        def set_event_handler(self, index, callback):
            assert(index >= 0 and index < 3)
            self._handlers[index] = callback

    @classmethod
    @asyncio.coroutine
    def create(cls, asynclinkbot_parent, motor_class=Motor):
        self = cls()
        self._proxy = asynclinkbot_parent._proxy
        self.motors = []
        for i in range(3):
            motor =  yield from motor_class.create(i, self._proxy, self) 
            self.motors.append(motor)
        self._timeouts = util.TimeoutCore(asyncio.get_event_loop())
        self._callback_handler = self._EncoderEventHandler()
        return self

    def __getitem__(self, key):
        return self.motors[key]

    def __len__(self):
        return 3
    
    @asyncio.coroutine
    def angles(self):
        ''' Get the current joint angles.

        :returns: (angle1, angle2, angle3, timestamp) . These are the three
            robot joint angles and a timestamp from the robot which is the
            number of milliseconds the robot has been on.
        :rtype: (float, float, float, int)
        '''

        fut = yield from self._proxy.getEncoderValues()
        user_fut = asyncio.Future()
        yield from self._timeouts.chain_futures(fut, user_fut, self.__angles)
        return user_fut

    def __angles(self, fut):
        results_obj = fut.result()
        results = ()
        for angle in results_obj.values:
            results += (util.rad2deg(angle),)
        results += (results_obj.timestamp,)
        return results

    @asyncio.coroutine
    def move(self, angles, mask=0x07, relative=True, timeouts=None,
            states_on_timeout = None):
        ''' Move a Linkbot's joints

        :param angles: A list of angles in degrees
        :type angles: [float, float, float]
        :param mask: Which joints to actually move. Valid values are:

            * 1: joint 1
            * 2: joint 2
            * 3: joints 1 and 2
            * 4: joint 3
            * 5: joints 1 and 3
            * 6: joints 2 and 3
            * 7: all 3 joints
            
        :param relative: This flag controls whether to move a relative distance
            from the motor's current position or to an absolute position.
        :type relative: bool
        :param timeouts: Sets timeouts for each motor's movement, in seconds. If
            the timeout expires while the motor is in motion, the motor will
            transition to the motor state specified by the ``states_on_timeout``
            parameter.
        :type timeouts: [float, float, float]
        :type states_on_timeout: [ linkbot3.peripherals.Motor.State,
                                   linkbot3.peripherals.Motor.State,
                                   linkbot3.peripherals.Motor.State ]
        '''
        angles = list(map(util.deg2rad, angles))
        args_obj = self._proxy.rb_get_args_obj('move')
        names = ['motorOneGoal', 'motorTwoGoal', 'motorThreeGoal']
        if relative:
            move_type = peripherals.Motor._MoveType.RELATIVE
        else:
            move_type = peripherals.Motor._MoveType.ABSOLUTE
        for i,name in enumerate(names):
            if mask&(1<<i):
                getattr(args_obj,name).type = move_type
                getattr(args_obj,name).goal = angles[i]
                getattr(args_obj,name).controller = yield from self.motors[i].controller()
                if timeouts:
                    getattr(args_obj,name).timeout = timeouts[i]
                if states_on_timeout:
                    getattr(args_obj,name).modeOnTimeout = states_on_timeout[i]

        fut = yield from self._proxy.move(args_obj)
        return fut

    @asyncio.coroutine
    def move_wait(self, mask=0x07):
        futs = []
        for i in range(3):
            if mask & (1<<i):
                fut = yield from self.motors[i].move_wait() 
                futs.append(fut)
        user_fut = asyncio.Future()
        fut = asyncio.gather(*tuple(futs))
        util.chain_futures(fut, user_fut, conv=lambda x: None)
        return user_fut

    @asyncio.coroutine
    def reset(self):
        ''' Reset the revolution-counter on the Linkbot.

        When a Linkbot's motor turns more than 360 degrees, the motor's reported
        angle does not wrap back around to zero. For instance, if a motor is
        rotated ten times, retrieving the motor angle would yield a value of
        something like 3600 degrees. Similarly, if a motor is currently at 3600
        degrees and it receives an instruction to move to an absolute position
        of 0 degrees, the motor will "wind down" backwards ten full rotations.

        This function resets the internal counter on the Linkbot that stores
        multiple revolutions on the robot. For instance, if the robot angle is
        currently 3610, after a ```reset()```, the motor will report to be at an
        angle of 10 degrees. 
        '''
        fut = yield from self._proxy.resetEncoderRevs()
        return fut

    @asyncio.coroutine
    def stop(self, mask=0x07):
        ''' Immediately stop all motors.

        :param mask: See :func:`linkbot3.async_peripherals.Motors.move`
        '''
        fut = yield from self._proxy.stop(mask=mask)
        return fut

class Twi:
    @classmethod
    @asyncio.coroutine
    def create(cls, proxy):
        self = cls()
        self._proxy = proxy
        return self

    @asyncio.coroutine
    def read(self, address, size):
        '''
        Read from an attached TWI device.

        :param address: TWI address to read from
        :type address: int
        :param size: Number of bytes to read
        :type size: int
        :returns: asyncio.Future containing a bytestring
        '''
        fut = yield from self._proxy.readTwi(address=address, recvsize=size)
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=lambda x:x.data)
        return user_fut

    @asyncio.coroutine
    def write(self, address, bytestring):
        '''
        Write to an attached TWI device.

        :param address: TWI address to write to.
        :param bytestring: a bytestring to write
        '''
        fut = yield from self._proxy.writeTwi(address=address, data=bytestring)
        return fut

    @asyncio.coroutine
    def write_read(self, write_addr, write_data, recv_size):
        '''
        Write and read from a TWI device in one step without releasing the TWI
        bus.

        :param write_addr: Address to write to.
        :param write_data: Data to write.
        :type write_data: bytes
        :param recv_size: Number of bytes to read after writing.
        :returns: asyncio.Future containing a bytestring
        '''
        fut = yield from self._proxy.writeReadTwi(
                address=write_addr,
                recvsize=recv_size,
                data=write_data)
        user_fut = asyncio.Future()
        util.chain_futures(fut, user_fut, conv=lambda x:x.data)
        return user_fut

