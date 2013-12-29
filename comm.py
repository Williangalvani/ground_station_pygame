from messages import *
from serial.tools import list_ports
import os 
#from protocol import *
import serial
import time
import threading

class FuncThread(threading.Thread):
    def __init__(self, target, *args):
        self._target = target
        self._args = args

        threading.Thread.__init__(self)

    def run(self):
        self._target(*self._args)


class TelemetryReader():

    def __init__(self,window):
        self.run = True
        self.window = window
        self.thread = FuncThread(self.loop)

        self.ser = serial.Serial(self.list_serial_ports()[0],115200,timeout=1)
        self.ser.flushInput()
        self.thread.start()


    def loop(self):
        while(self.run):
            lat,long = self.read_gps()
            self.window.set_tracked_position(lat,long)
            time.sleep(0.1)
            self.window.set_attitude(*self.read_attitude())

    def stop(self):
        self.run = False


    def list_serial_ports(self):
        # Windows
        if os.name == 'nt':
            # Scan for available ports.
            available = []
            for i in range(256):
                try:
                    s = serial.Serial(i)
                    available.append('COM'+str(i + 1))
                    s.close()
                except serial.SerialException:
                    pass
            return available
        else:
            # Mac / Linux
            return [port[0] for port in list_ports.comports ()]


    def receiveAnswer(self,expectedCommand):
        header = self.ser.read(3)
        if '$M>' not in header:
            return None
        size = ord(self.ser.read())
        command = ord(self.ser.read())
        data = []
        for i in range(size):
            data.append(ord(self.ser.read()))
        checksum = 0
        checksum ^= size;
        checksum ^= command;
        for i in data:
            checksum ^= i;
        receivedChecksum = ord(self.ser.read())
        #print 'command' , command
        #print 'size' , size
        #print 'data' , data
        #print checksum, receivedChecksum
        if command != expectedCommand:
            print "commands dont match!" , command, expectedCommand
            return None
        if checksum == receivedChecksum:
            return data
        else:
            print 'lost packet!'
            return None

    def MSPquery(self,command    ):
            self.ser.flushInput()
            o = bytearray('$M<')
            #print dir(o)
            c = 0;
            o += chr(0);
            c ^= o[3];       #no payload
            o += chr(command); c ^= o[4];
            o += chr(c);
            answer = None
            while (not answer):
                    self.ser.write(o)
                    self.ser.flushInput()
                    answer = self.receiveAnswer(command)
            return answer



    def decode32(self,data):
        #print data
        result = (data[0]&0xff) + ((data[1]&0xff)<<8) + ((data[2]&0xff)<<16) + ((data[3]&0xff)<<24)
        is_negative = data[3]>=128
        if is_negative:
            result -= 2**32
        return result

    def decode16(self,data):
        #print data
        result = (data[0]&0xff) + ((data[1]&0xff)<<8)
        is_negative = data[1]>=128
        if is_negative:
            result -= 2**16
        return result


    def read_gps(self):
        answer = self.MSPquery(MSP_RAW_GPS)
        if answer:
            lat_list = answer[2:6]
            long_list = answer[6:10]
            latitude = self.decode32(lat_list)/10000000.0
            longitude = self.decode32(long_list)/10000000.0
            #print longitude,latitude
            return longitude,latitude
        return (0,0)

    def read_attitude(self):
        answer = self.MSPquery(MSP_ATTITUDE)
        if answer:
            #print answer
            roll = -self.decode16(answer[0:2])/10.0
            pitch = self.decode16(answer[2:4])/10.0
            #print roll,pitch
            return roll,pitch
        return (0,0)

#
#
# if __name__ == "main":
#     ser.write('!hw\r')
#     print ser.readall()
#
#     print MSPquery(MSP_IDENT)
#     print MSPquery(MSP_ATTITUDE)
#     print MSPquery(MSP_RAW_GPS)
#     print MSPquery(MSP_STATUS)
#
#     read_gps()
#     # for i in range(100):
#     #     print MSPquery(MSP_RAW_GPS)
#     #     time.sleep(0.1)
#
