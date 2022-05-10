
import serial
from serial.serialutil import SerialException
import time
import json
from json.decoder import JSONDecodeError
import serial.tools.list_ports

from saveData import addData

sensorSerials = []
AVAILABLE_DEVICES = ["/dev/ttyUSB0","/dev/ttyUSB1","/dev/ttyUSB2","COM3","COM4","COM5","COM6"]

DEVICES = [
    {
        "PORT":"/dev/ttyUSB0",
        "BAUDRATE":57600,        
    },
    
    {
        "PORT":"/dev/ttyUSB1",
        "BAUDRATE":9600,        
    }
]

def autoAddSensorSerials():
    for p in list(serial.tools.list_ports.comports(include_links=True)):   
        if p.device in AVAILABLE_DEVICES:
            addSensorSerial(p.device)     

def manualAddSensorSerials():
    for p in DEVICES:   
        addSensorSerial(p["PORT"],p["BAUDRATE"])    

def sensorSerialExists(port):
    for sensorSerial in sensorSerials:
        if port == sensorSerial.port:
            return True, sensorSerial
    return False, None

def addSensorSerial(port, baudrate=9600):
    exists, sensorSerial = sensorSerialExists(port)
    created = False
    if not exists:    
        try:
            sensorSerial = serial.Serial(port=port,baudrate=baudrate, timeout=.1)  

            sensorSerial.reset_input_buffer()      
            sensorSerials.append(sensorSerial)
            created = True
            print("[INFO] Connected to port: ",port," baudrate: ",sensorSerial.baudrate)
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
        manualAddSensorSerials()
        for sensorSerial in sensorSerials:   
            data = ""
            while sensorSerial.in_waiting>0:   
                if sensorSerial.in_waiting>4000:
                    sensorSerial.reset_input_buffer()    
                    continue
                try:  
                    print(f"[INFO BYTES] ", sensorSerial.in_waiting)
                    data = sensorSerial.readline()       
                    data  = json.loads(data)
                    print(f"[SERIAL {sensorSerial.port}] ", data)
                    if 'WHOAMI' in data.keys() and 'TASK' in data.keys():
                        addData(data)
                    print("-----------------------")
                except JSONDecodeError:
                    print(f"[ERROR {sensorSerial.port}] Formato de json erroneo.",data)
                    print("-----------------------")
                    pass                
                except SerialException:
                    print(f"[ERROR {sensorSerial.port}] Puerto desconectado.")
                    print("-----------------------")
                    sensorSerial.close()
                    sensorSerials.remove(sensorSerial)
                
        time.sleep(0.1)