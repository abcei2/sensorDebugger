import pandas
import datetime
import os.path

MAX_NUM_ROWS_FOR_CSV = 1000
MAX_NUM_ROWS_FOR_DATAFRAME = 10

prefix = "data"
data = {
    "ECREAD":{
        "PATH":f"./{prefix}/ECDATA/",
        "COUNTER":0, 
        "NAME":"ECREAD",
        "DATA":{"VALUE":[],"DESIRED":[],"TIMESTAMP":[],"TEMP":[]} 
    },
    "ECCONTROL": {
        "PATH":f"./{prefix}/ECCONTROL/",
        "COUNTER":0,
        "NAME":"ECCONTROL",
        "DATA": {"GOING":[],"TIMESTAMP":[]}
    },
    "PHREAD" : {
        "PATH":f"./{prefix}/PHDATA/",
        "COUNTER":0, 
        "NAME":"PHREAD",
        "DATA":{"VALUE":[],"DESIRED":[],"TIMESTAMP":[]} 
    } ,
    "PHCONTROL" : {
        "PATH":f"./{prefix}/PHCONTROL/",
        "COUNTER":0, 
        "NAME":"PHCONTROL",
        "DATA": {"GOING":[],"TIMESTAMP":[]}
    }
}


for key in data.keys():
    os.makedirs(data[key]["PATH"], exist_ok=True)


def clearData(data):
    for key in data.keys():
        data[key].clear()

def addData(command):
    
    appendDataToDict(data[command["WHOAMI"]+command["TASK"]],command)  


def appendDataToDict(sensorPathInfo, command):
    if command["TASK"]=="CONTROL":
        sensorPathInfo["DATA"]["GOING"].append(command["GOING"])
        sensorPathInfo["DATA"]["TIMESTAMP"].append(datetime.datetime.now())
        if len(sensorPathInfo["DATA"]["GOING"]) >= MAX_NUM_ROWS_FOR_DATAFRAME:
            dataToCsv(sensorPathInfo)
            clearData(sensorPathInfo["DATA"])

    elif command["TASK"]=="READ":
        sensorPathInfo["DATA"]["VALUE"].append(command["VALUE"])
        sensorPathInfo["DATA"]["DESIRED"].append(command["DESIRED"])
        sensorPathInfo["DATA"]["TIMESTAMP"].append(datetime.datetime.now())
        if command["WHOAMI"]=="EC":    
            sensorPathInfo["DATA"]["TEMP"].append(command["TEMP"])            
        if len(sensorPathInfo["DATA"]["VALUE"]) >= MAX_NUM_ROWS_FOR_DATAFRAME:
            dataToCsv(sensorPathInfo)
            clearData(sensorPathInfo["DATA"])
    
def dataToCsv(sensorPathInfo):
    dataFrame = pandas.DataFrame.from_dict(sensorPathInfo["DATA"]) 
    dataSaved = False
    while not dataSaved:
        filePath = sensorPathInfo["PATH"]+str(sensorPathInfo["COUNTER"])+".csv"    
        if os.path.isfile(filePath):
            csvFile = open(filePath)
            numline = len(csvFile.readlines())
            csvFile.close()
            if numline > MAX_NUM_ROWS_FOR_CSV:
                sensorPathInfo["COUNTER"] += 1
            else:
                dataFrame.to_csv(filePath, mode='a', index=False, header=False)
                dataSaved = True
        else:        
            dataFrame.to_csv(filePath, index=False)
            dataSaved = True
    
            


