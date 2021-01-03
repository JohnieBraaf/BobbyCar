import pyb, binascii, struct
from machine import UART

class HoverBoard(object):
    def __init__(self):
        self.uart = UART(2, 115200) # Use HW UART 2

        # speeds
        self.speed = 0
        self.speed_previous = 0
        self.speed_measured = 0

        # parameters
        self.debug = False
        self.speed_stepping = 3 # speed increments, for smoothness
        self.speed_minimum  = 50 # speed needed to spin up motors  

        print('HoverBoard initialized')

    def process(self, message):
        if len(message) == 18:
            if message[1] == 171 and message[0] == 205: # (1)0xAB (0)0xCD 

                header, cmd1, cmd2, speed_r_meas, speed_l_meas, bat_voltage, board_temp, cmd_led, checkbits = struct.unpack('<HhhhhhhHH' ,message)
                checksum = struct.pack('H', int(0xABCD) ^ cmd1 ^ cmd2 ^ speed_r_meas ^ speed_l_meas ^ bat_voltage ^ board_temp ^ cmd_led)
                
                if checkbits == struct.unpack('H', checksum)[0]:
                    self.cmd1 = cmd1
                    self.cmd2 = cmd2
                    self.speed_r_meas = speed_r_meas
                    self.speed_l_meas = speed_l_meas
                    self.bat_voltage = bat_voltage
                    self.board_temp = board_temp
                    self.cmd_led = cmd_led
                    self.measured_speed = - int(self.speed_r_meas) + int(self.speed_l_meas)

                    if self.debug:
                        print(str(self.cmd1) + ',' +
                          str(self.cmd2) + ',' +
                          str(self.speed_r_meas) + ',' +
                          str(self.speed_l_meas) + ',' +
                          str(self.bat_voltage) + ',' +
                          str(self.board_temp) + ',' +
                          str(self.cmd_led))
                    
                    return True
                else:
                    print('Invalid checksum: ' + str(message))
            else:
                print('Invalid start bit: ' + str(message))
        else:
            print('Invalid message length: ' + str(message))
        return False

    def read(self):
        result = False
        
        if self.uart.any():
            rx = self.uart.read()       
            pyb.LED(3).toggle()

            # if we get multiple messages, process only most recent message
            # this should normally not happen, reduce loop time to solve
            messages = len(rx) // 18
            if messages > 1:
                print('WARN: more than 1 message in buffer ' + str(messages))
            start = (messages - 1) * 18
            end = start + 18
            if end > len(rx):
                end = len(rx)
            
            result = self.process(rx[start:end])
        
        return result

    def send(self, speed, steer=0):
        
        # increase and decrease speed gradially, disregards measured_speed
        self.speed = speed # target speed
        direction = 1
        if self.speed < self.speed_previous:
            direction = -1
        delta = (self.speed - self.speed_previous) * direction
        if delta > self.speed_stepping:
            #print('target: ' + str(self.speed) + ', previous: ' + str(self.speed_previous) + ', delta:' + str(delta))
            speed = self.speed_previous + (self.speed_stepping * direction)
        self.speed_previous = speed

        # send struct
        checksum = int(0xABCD) ^ int(steer) ^ int(speed)
        msg = struct.pack('HhhH', int(0xABCD), steer, speed, checksum)
        self.uart.write(msg)

    def flush(self):
        self.uart.read()