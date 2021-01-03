from board import HoverBoard
from control import Controller

class BobbyCar(object):
    def __init__(self):
        
        self.board = HoverBoard()
        self.control = Controller()

        self.gear = 0 # neutral
        self.direction = 0 # stationary

        # speeds
        self.gears_forward = 4  # number of forward gears
        self.gears_backward = 2  # number of backward gears
        self.speed_stepping = 25 # increment per gear
        self.speed_default = 75  # i.e target speed 1st gear = default + 1x stepping

        self.loop()

    def loop(self):
        while True:

            self.control.update()

            if self.control.warn: # breaker
                self.gear = 0
                self.direction = 0
                self.board.speed = 0
                self.speed_previous = 0
                self.board.send(0) # stationary
                
            elif self.control.warn_previous:
                self.board.flush() # empty rx buffer

            else:
                # forward
                if self.control.plus: 
                    self.direction = 1
                    if self.control.plus_previous != self.control.plus or self.control.minus_previous:
                        self.gear = 1  # start
                    elif not self.control.fuel_previous and self.control.fuel:
                        self.gear += 1 # shift up
                    elif not self.control.tool_previous and self.control.tool:
                        self.gear -= 1 # shift down

                    if self.gear > self.gears_forward:
                        self.gear = self.gears_forward

                # backward
                elif self.control.minus: 
                    self.direction = -1
                    if self.control.minus_previous != self.control.minus or self.control.plus_previous:
                        self.gear = 1  # start
                    elif not self.control.applause_previous and self.control.applause:
                        self.gear += 1 # shift up
                    elif not self.control.radio_previous and self.control.radio:
                        self.gear -= 1 # shift down

                    if self.gear > self.gears_backward:
                        self.gear = self.gears_backward

                # disengage
                else: 
                    self.direction = 0 
                    self.gear = 0

                # sanitize
                if self.gear < 0:
                    self.gear = 0
                if self.gear == 0 and self.direction != 0:
                    self.gear = 1

                # reply command to incoming messages
                if self.board.read(): 
                    if self.control.plus and self.control.minus:
                        self.board.send(0) # stationary
                    elif self.control.plus or self.control.minus:
                        speed = self.direction  * ((self.speed_stepping * self.gear) + self.speed_default)
                        #print('direction: ' + str(self.direction) + ', gear: ' + str(self.gear) + ', speed: ' + str(speed))
                        self.board.send(speed) # send calculated speed

                    else:
                        self.board.send(0) # stationary

car = BobbyCar()