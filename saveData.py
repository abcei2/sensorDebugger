import datetime
import math
import os.path
import pandas
import requests
import time

MAX_NUM_ROWS_FOR_CSV = 1000
MAX_NUM_ROWS_FOR_DATAFRAME = 10

prefix = "data"
data = {
    "ECREAD": {
        "PATH": f"./{prefix}/ECDATA/",
        "COUNTER": 0,
        "NAME": "ECREAD",
        "DATA": {"WHOAMI": [], "VALUE": [], "DESIRED": [], "TEMP": [], "TIMESTAMP": []},
    },
    "ECCONTROL": {
        "PATH": f"./{prefix}/ECCONTROL/",
        "COUNTER": 0,
        "NAME": "ECCONTROL",
        "DATA": {
            "WHOAMI": [],
            "VALUE": [],
            "DESIRED": [],
            "GOING": [],
            "TIMESTAMP": [],
        },
    },
    "PHREAD": {
        "PATH": f"./{prefix}/PHDATA/",
        "COUNTER": 0,
        "NAME": "PHREAD",
        "DATA": {"WHOAMI": [], "VALUE": [], "DESIRED": [], "TIMESTAMP": []},
    },
    "PHCONTROL": {
        "PATH": f"./{prefix}/PHCONTROL/",
        "COUNTER": 0,
        "NAME": "PHCONTROL",
        "DATA": {
            "WHOAMI": [],
            "VALUE": [],
            "DESIRED": [],
            "GOING": [],
            "TIMESTAMP": [],
        },
    },
}


for key in data.keys():
    os.makedirs(data[key]["PATH"], exist_ok=True)


def clearData(data):
    for key in data.keys():
        data[key].clear()


def addData(command):
    appendDataToDict(data[command["WHOAMI"] + command["TASK"]], command)
    try:
        syncToInflux(command)
    except Exception as e:
        print("Error syncing to influx:", e)


def appendDataToDict(sensorPathInfo, command):

    sensorPathInfo["DATA"]["WHOAMI"].append(command["WHOAMI"])
    sensorPathInfo["DATA"]["VALUE"].append(command["VALUE"])
    sensorPathInfo["DATA"]["DESIRED"].append(command["DESIRED"])
    sensorPathInfo["DATA"]["TIMESTAMP"].append(datetime.datetime.now())
    if command["TASK"] == "CONTROL":
        sensorPathInfo["DATA"]["GOING"].append(command["GOING"])
    elif command["TASK"] == "READ":
        if command["WHOAMI"] == "EC":
            sensorPathInfo["DATA"]["TEMP"].append(command["TEMP"])
    if len(sensorPathInfo["DATA"]["VALUE"]) >= MAX_NUM_ROWS_FOR_DATAFRAME:
        dataToCsv(sensorPathInfo)
        clearData(sensorPathInfo["DATA"])


def dataToCsv(sensorPathInfo):
    dataFrame = pandas.DataFrame.from_dict(sensorPathInfo["DATA"])
    dataSaved = False
    while not dataSaved:
        filePath = sensorPathInfo["PATH"] + str(sensorPathInfo["COUNTER"]) + ".csv"
        if os.path.isfile(filePath):
            csvFile = open(filePath)
            numline = len(csvFile.readlines())
            csvFile.close()
            if numline > MAX_NUM_ROWS_FOR_CSV:
                sensorPathInfo["COUNTER"] += 1
            else:
                dataFrame.to_csv(filePath, mode="a", index=False, header=False)
                dataSaved = True
        else:
            dataFrame.to_csv(filePath, index=False)
            dataSaved = True


def getInfluxLine(command):
    if command["WHOAMI"] != "PH":
        return None

    if command["TASK"] == "READ":
        return f"basil,ph_sensor_brand=atlas ph={command['VALUE']} {math.trunc(time.time())}"

    if command["TASK"] == "CONTROL":
        return f"basil,ph_sensor_brand=atlas,direction={command['GOING']} dose={command['VALUE']} {math.trunc(time.time())}"

    return None

def syncToInflux(command):

    line = getInfluxLine(command)
    if line is None:
        return

    INFLUXDB_DOMAIN = "207.246.118.54"
    INFLUXDB_TOKEN = "loB9a7VkXuIY1Jjh3ScwRWg2Foq6Lb0p6kk9QHMBhjunp-KDCUdrc8TsB4YBVrHee0xmd9LYNtXN75J5v9hK8w=="
    INFLUXDB_ORG = "Tucano%20Robotics"
    INFLUXDB_BUCKET = "autoponico"

    headers = {
        "Authorization": f"Token {INFLUXDB_TOKEN}",
        "Content-Type": "text/plain; charset=utf-8",
        "Accept": "application/json",
    }

    requests.post(
        f"http://{INFLUXDB_DOMAIN}:8086/api/v2/write?org={INFLUXDB_ORG}&bucket={INFLUXDB_BUCKET}&precision=s",
        data=line.encode(),
        headers=headers,
    )
