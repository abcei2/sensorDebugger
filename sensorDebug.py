#! /usr/bin/python3

"""Treat input if available, otherwise exit without
blocking"""

import sys
import threading
import queue
import os
import signal

import time
import json
from json.decoder import JSONDecodeError

from serialUtils import (
    addSensorSerial, sendCommand, 
    sensorSerials, serialReadLoop
)

def finish():
    os.kill(os.getpid(), signal.SIGINT)
    exit()
def cleanup(*args):
    exit()
signal.signal(signal.SIGINT, cleanup)

def inputCommand(inputText):
    try:
        commands = json.loads(inputText)        
        if "COMMAND" not in commands.keys():
            print("[ERROR] se requiere la etiqueta 'COMMAND'")
        elif "PORT" not in commands.keys():
            if commands["COMMAND"]=="EXIT":
                finish()  
            else:
                print("[ERROR] Se requiere la que indique el puerto 'PORT'")
        else:
            if commands["COMMAND"]=="ADD":
                addSensorSerial(commands["PORT"])
            else:
                sendCommand(commands)
    except JSONDecodeError:
        print("bad json")
        
    print('read input:', inputText, end='')

input_queue = queue.Queue()

def nonBlockInputLoop():    
    while True:
        inputText = input_queue.get()
        inputCommand(inputText)

# Start serial loop
serialReadThread = threading.Thread(target=serialReadLoop)
serialReadThread.start()
# Start non blocking input
nonBlockInputThread = threading.Thread(target=nonBlockInputLoop)
nonBlockInputThread.start()
# main loop: stuff input in the queue
for line in sys.stdin:
    input_queue.put(line)
