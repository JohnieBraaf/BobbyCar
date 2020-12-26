import pyb

class Controller(object):
    def __init__(self):

        # Pin mapping
        self.minus_pin = pyb.ADC(pyb.Pin.board.PC0)
        self.plus_pin = pyb.ADC(pyb.Pin.board.PC1)
        self.applause_pin = pyb.ADC(pyb.Pin.board.PC2)

        self.tool_pin = pyb.ADC(pyb.Pin.board.PA0)
        self.start_pin = pyb.ADC(pyb.Pin.board.PA1)
        # PA2, PA3 -> UART
        self.warn_pin = pyb.ADC(pyb.Pin.board.PA5)
        self.fuel_pin = pyb.ADC(pyb.Pin.board.PA6)
        self.radio_pin = pyb.ADC(pyb.Pin.board.PA7)

        # parameters
        self.limit = 2000 # we check if the pin voltage goes low (i.e. below the limit value)

        # initalizes states
        self.minus = self.minus_previous = False
        self.plus = self.plus_previous = False
        self.applause = self.applause_previous = False

        self.tool = self.tool_previous = False
        self.start = self.start_previous = False

        self.warn = self.warn_previous = False
        self.fuel = self.fuel_previous = False
        self.radio = self.radio_previous = False 
        
        print('Controller initialized')

    def check(self, pin):
        if pin.read() < self.limit:
            return True
        return False

    def update(self):        
        self.minus_previous = self.minus
        self.minus = self.check(self.minus_pin)
        self.plus_previous = self.plus
        self.plus = self.check(self.plus_pin)
        self.applause_previous = self.applause
        self.applause = self.check(self.applause_pin)

        self.tool_previous = self.tool
        self.tool = self.check(self.tool_pin)
        self.start_previous = self.start
        self.start = self.check(self.start_pin)

        self.warn_previous = self.warn
        self.warn = self.check(self.warn_pin)
        self.fuel_previous = self.fuel
        self.fuel = self.check(self.fuel_pin)
        self.radio_previous = self.radio
        self.radio = self.check(self.radio_pin)

    def any(self):
        if self.minus + self.plus + self.applause + self.tool + self.start + self.warn + self.fuel + self.radio > 0:
            return True
        return False