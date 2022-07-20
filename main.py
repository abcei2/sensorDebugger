#! /usr/bin/python3

"""Treat input if available, otherwise exit without
blocking"""

import json
import os
import queue
import signal
import sys
import threading

from json.decoder import JSONDecodeError

from serialUtils import (
    addSensorSerial, sendCommand, serialReadLoop
)

print("# Starting script...")

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

# Threads
input_queue = queue.Queue()

def nonBlockInputLoop():    
    while True:
        inputText = input_queue.get()
        inputCommand(inputText)

print("# Start serial thread loop")
serialReadThread = threading.Thread(target=serialReadLoop)
serialReadThread.start()

print("# Start non blocking input thread loop")
nonBlockInputThread = threading.Thread(target=nonBlockInputLoop)
nonBlockInputThread.start()

for line in sys.stdin:
    input_queue.put(line)
