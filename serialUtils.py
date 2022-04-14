
import serial
from serial.serialutil import SerialException
import time
import json
from json.decoder import JSONDecodeError
import serial.tools.list_ports

from saveData import addData

sensorSerials = []
AVAILABLE_DEVICES = ["/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyUSB2","COM3","COM4","COM5","COM6"]

def autoAddSensorSerials():
    for p in list(serial.tools.list_ports.comports(include_links=True)):   
        if p.device in AVAILABLE_DEVICES:
            addSensorSerial(p.device)            

def sensorSerialExists(port):
    for sensorSerial in sensorSerials:
        if port == sensorSerial.port:
            return True, sensorSerial
    return False, None

def addSensorSerial(port):
    exists, sensorSerial = sensorSerialExists(port)
    created = False
    if not exists:    
        try:
            sensorSerial = serial.Serial(port=port, timeout=.1)          
            sensorSerials.append(sensorSerial)
            created = True
            print("[INFO] Connected to port: ",port)
        except SerialException:
            print("[ERROR] Can't connect to port: ",port)
    
    return created, exists, sensorSerial

def sendCommand(command):
    exists, sensorSerial = sensorSerialExists(command["PORT"])
    if exists:
        try:
            sensorSerial.write(bytes(json.dumps(command), 'utf-8'))               
            print("[INFO] Command send")          
        except SerialException:
            sensorSerial.close()
            sensorSerials.remove(sensorSerial)         
    else:
        print("[ERROR] Port doen't exists")

# read serial of all devices each 0.1 secs
def serialReadLoop():    
    while True:
        autoAddSensorSerials()
        for sensorSerial in sensorSerials:   
            print(f"------{sensorSerial.port}---------")   
            data = ""
            while data != b'':
                try:     
                    data = sensorSerial.readline()
                    data  = json.loads(data)
                    if 'WHOAMI' in data.keys() and 'TASK' in data.keys():
                        addData(data)
                    print("[SERIAL] ", data)
                except JSONDecodeError:
                    print("[ERROR] Formato de json erroneo.",data)
                    pass                
                except SerialException:
                    print("[ERROR] Puerto desconectado.")
                    sensorSerial.close()
                    sensorSerials.remove(sensorSerial)
            print("-----------------------")
                       
        time.sleep(0.1)