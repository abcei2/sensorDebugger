#! /usr/bin/python3

"""Treat input if available, otherwise exit without
blocking"""

import sys
import threading
import queue
import os
import signal

import serial
import time
import json
from json.decoder import JSONDecodeError


sensorSerials = []

RESPONSE_TIMEOUT = 5


def portConnected(port):
    for sensorSerial in sensorSerials:
        if port == sensorSerial.port:
            return True, sensorSerial
    try:
        aux_serial = serial.Serial(port=port, baudrate=9600, timeout=.1)          
        sensorSerials.append(aux_serial)
        return True, aux_serial
    except serial.serialutil.SerialException:
        return False, None

ok, comserial = portConnected("COM4")
ok, comserial = portConnected("COM6")
# ok, comserial = portConnected("/dev/ttyUSB0")
# ok, comserial = portConnected("/dev/ttyUSB1")


def sendCommand(command):
    is_connected, arduino = portConnected(command["PORT"])
    ok = True
    if is_connected:
        arduino.write(bytes(json.dumps(command), 'utf-8'))
        return ok
    else:
        return "port doesn't exists", ok


def nonBlockInput(linein):
    try:
        commands = json.loads(linein)
        if commands["COMMAND"]=="EXIT":
            noInput()
        print(sendCommand(json.loads(linein)))
    except JSONDecodeError:
        print("bad json")
    except KeyError:
        print("bad input")
        
    print('read input:', linein, end='')


def noInput():
    print('goodbye')
    # stop main thread (which is probably blocked reading
    # input) via an interrupt signal
    # only available for windows in version 3.2 or higher
    os.kill(os.getpid(), signal.SIGINT)
    exit()

# things to be done before exiting the main thread should go
# in here
def cleanup(*args):
    exit()

# handle sigint, which is being used by the work thread to
# tell the main thread to exit
signal.signal(signal.SIGINT, cleanup)

# will hold all input read, until the work thread has chance
# to deal with it
input_queue = queue.Queue()

# read serial of all devices each 0.1 secs
def serialReadLoop():    
    while True:
        for sensorSerial in sensorSerials:
            data = sensorSerial.readline()
            if data != b'':
                try:
                    data  = json.loads(data)
                    print(data)
                    print("\n") 
                    pass
                except JSONDecodeError:
                    pass
                       
        time.sleep(0.1)

# read non blocking inputs "Commands"
def nonBlockInputLoop():    
    while True:
        nonBlockInput(input_queue.get())

serialReadThread = threading.Thread(target=serialReadLoop)
serialReadThread.start()

nonBlockInputThread = threading.Thread(target=nonBlockInputLoop)
nonBlockInputThread.start()


# main loop: stuff input in the queue
for line in sys.stdin:
    input_queue.put(line)

# wait for work thread to finish
nonBlockInputThread.join()