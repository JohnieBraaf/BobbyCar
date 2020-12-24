import pyb, util, binascii
from machine import UART

class HoverBoard(object):
    def __init__(self):
        print('board')
        self.uart = UART(2, 115200) # Use HW UART 2

        # speeds
        self.speed = 0
        self.speed_previous = 0
        self.speed_measured = 0

        # parameters
        self.debug = False
        self.speed_stepping = 5 # speed increments, for smoothness

    def process(self, message):
        if len(message) == 18:
            if message[1] == 171 and message[0] == 205: # (1)0xAB (0)0xCD 

                cmd1 = util.toDec(hex(message[3])[2:] + hex(message[2])[2:])
                cmd2 = util.toDec(hex(message[5])[2:] + hex(message[4])[2:])
                speed_r_meas = util.toDec(hex(message[7])[2:] + hex(message[6])[2:])
                speed_l_meas = util.toDec(hex(message[9])[2:] + hex(message[8])[2:])
                bat_voltage = message[11] << 8 | message[10]
                board_temp = message[13] << 8 | message[12]
                cmd_led = message[15] << 8 | message[14]
                check = message[17] << 8 | message[16]
                
                #checksum = int(0xABCD) ^ int(cmd1) ^ int(cmd2) ^ int(speed_r_meas) ^ int(speed_l_meas) ^ int(bat_voltage) ^ int(board_temp) ^ int(cmd_led)
                
                #if util.toHex(check) == util.toHex(checksum):
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

                    
                    

                '''else:
                                                                                    print('Invalid checksum: ' + str(message))
                                                                                    print('Check: ' + util.toHex(check))
                                                                                    print('checksum: ' + util.toHex(checksum))
                                                                                    print('Check: ' + str(check))
                                                                                    print('checksum: ' + str(checksum))
                                                                                    print(message[5] << 8 | message[4])
                                                                                    print(str(cmd1) + ',' +
                                                                                          str(cmd2) + ',' +
                                                                                          str(speed_r_meas) + ',' +
                                                                                          str(speed_l_meas) + ',' +
                                                                                          str(bat_voltage) + ',' +
                                                                                          str(board_temp) + ',' +
                                                                                          str(cmd_led))'''
                
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

            # if we get multiple messages process only most recent message
            messages = len(rx) // 18
            start = (messages - 1) * 18
            end = start + 18
            if end > len(rx):
                end = len(rx)
            
            result = self.process(rx[start:end])
        
        return result

    def send(self, speed, steer=0):
        
        self.speed = speed
        direction = 1
        if self.speed < self.speed_previous:
            direction = -1

        delta = (self.speed - self.speed_previous) * direction
        
        if delta > self.speed_stepping:
            print(self.measured_speed)
            print('target: ' + str(self.speed) + ', previous: ' + str(self.speed_previous) + ', delta:' + str(delta))

        
            speed = self.speed_previous + (self.speed_stepping * direction)

        #if self.speed - self.speed_previous > self.speed_stepping:
        #    print(self.speed_previous + self.speed_stepping)
        #if self.speed - self.speed_previous > self.speed_stepping:
        #    speed = self.speed_previous + self.speed_stepping

        #if speed < 0:
        #    print(self.speed - self.speed_previous)
        #    if self.speed - self.speed_previous < - self.speed_stepping:
        #        speed = self.speed_previous - self.speed_stepping


        self.speed_previous = speed
        #print(measured_speed - speed)
        #print(measured_speed)
        #print(speed)
        #print()
        #if measured_speed < speed - (speed * 0.8)
        steer_hex = util.toHex(steer)
        speed_hex = util.toHex(speed)
        check_hex = util.toHex(int(0xABCD) ^ int(steer) ^ int(speed))
        full_hex  = 'cdab' + steer_hex[2:4] + steer_hex[0:2] + speed_hex[2:4] + speed_hex[0:2] + check_hex[2:4] + check_hex[0:2]
        #print(binascii.unhexlify(full_hex))
        self.uart.write(binascii.unhexlify(full_hex))
