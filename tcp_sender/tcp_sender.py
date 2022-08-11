import math
from wmi import WMI
import psutil
import socket
import os
from os import environ
import time
import os.path
from os import path
from uptime import uptime
from datetime import datetime


TCP_IP = '192.168.222.129'
hostname = socket.getfqdn(TCP_IP)
TCP_PORT = 55555




class Sensor:
    Name = ""
    Identifier = ""
    SensorType = ""
    Parent = ""
    Index = -1

    def __init__(self, sensor):
        self.Name = sensor.Name
        self.Identifier = sensor.Identifier
        self.SensorType = sensor.SensorType
        self.Parent = sensor.Parent
        self.Index = sensor.Index

    def getValue(self):
        return WMI(namespace="root\LibreHardwareMonitor").Sensor(Identifier=self.Identifier)[0].Value



class Device:
    Name = ""
    Identifier = ""
    HardwareType = ""
    Parent = ""
    Sensors = None

    def __init__(self, device):
        self.Sensors = list()
        self.Name = device.Name
        self.Identifier = device.Identifier
        self.HardwareType = device.HardwareType
        self.Parent = device.Parent
        for sensor in WMI(namespace="root\LibreHardwareMonitor").Sensor():
            if sensor.Parent == self.Identifier:
                self.Sensors.append(Sensor(sensor))


def addDevice(deviceQuery):
    if len(deviceQuery) > 1:
        deviceList = list()
        for element in deviceQuery:
            device = Device(element)
            deviceList.append(device)
    elif len(deviceQuery) == 1:
        deviceList = Device(deviceQuery[0])
    else:
        deviceList = None

    return deviceList


class SystemInfo:
    GPU = None
    def __init__(self):
        w = WMI(namespace="root\LibreHardwareMonitor")
        self.CPU = addDevice(w.Hardware(HardwareType="CPU"))
        self.GPU = addDevice(w.Hardware(HardwareType="GpuNvidia"))
        if self.GPU is None:
            #print("GpuNvidia none")
            self.GPU = addDevice(w.Hardware(HardwareType="GpuAti"))
            if self.GPU is None:
               #print("GpuAti none")
                self.GPU = addDevice(w.Hardware(HardwareType="GpuAMD"))
                if self.GPU is None:
                    #print("GpuAMD none")
                    self.GPU = addDevice(w.Hardware(HardwareType="Gpu"))


def collectGpuInfo(device):
    gList = []
    if isinstance(device, list):
        for element in device:
            addToList(gList, element)
    else:
        addToList(gList, device)
    return listToDict(gList)


def collectCpuLoad(deviceCpu):
    cpuLoad = "NoData"
    if len(deviceCpu.Sensors) > 0:
        for sensor in deviceCpu.Sensors:
            #print(sensor.Name + " " + sensor.SensorType + " " + str(math.floor(sensor.getValue())) )
            if sensor.Name == "CPU Total" and sensor.SensorType == "Load":
                cpuLoad = str(math.floor(sensor.getValue()))
    return cpuLoad


def collectCpuTemp(deviceCpu):
    cpuTemp = "NoData"
    if len(deviceCpu.Sensors) > 0:
        for sensor in deviceCpu.Sensors:
            #print(sensor.Name + " " + sensor.SensorType + " " + str(math.floor(sensor.getValue())) )
            if sensor.Name == "Core (Tctl/Tdie)" and sensor.SensorType == "Temperature":
                cpuTemp = str(math.floor(sensor.getValue()))
            if sensor.Name == "Core Max" and sensor.SensorType == "Temperature":
                cpuTemp = str(math.floor(sensor.getValue()))
    return cpuTemp


def collectCpuPwr(deviceCpu):
    cpuPwr = "NoData"
    if len(deviceCpu.Sensors) > 0:
        for sensor in deviceCpu.Sensors:
            #print(sensor.Name + " " + sensor.SensorType + " " + str(math.floor(sensor.getValue())) )
            if sensor.Name == "CPU Package" and sensor.SensorType == "Power":
                cpuPwr = str(math.floor(sensor.getValue()))
            if sensor.Name == "Package Power" and sensor.SensorType == "Power":
                cpuPwr = str(math.floor(sensor.getValue()))
    return cpuPwr


def getCpuName(device):
    try:
        cn = device.Name
    except:
        cn = "NoData"
    return cn


def addToList(listName, deviceName):
    listName.append(getGpuName(deviceName))
    listName.append(getCoreTemp(deviceName))
    listName.append(getMemoryTemp(deviceName))
    listName.append(getFanSpeed(deviceName))
    listName.append(getGpuLoad(deviceName))
    listName.append(getCoreVoltage(deviceName))
    listName.append(getPower(deviceName))
    listName.append(getCoreClock(deviceName))
    listName.append(getMemoryClock(deviceName))


def listToDict(listName):
    dictName = {}
    objName = []
    i = 0
    while i < 13:
        objName.append("gpuName" + str(i))
        objName.append("coreTemp" + str(i))
        objName.append("memoryTemp" + str(i))
        objName.append("fanSpeed" + str(i))
        objName.append("gpuLoad" + str(i))
        objName.append("coreVoltage" + str(i))
        objName.append("Power" + str(i))
        objName.append("coreClock" + str(i))
        objName.append("memoryClock" + str(i))
        i = i + 1
    while listName:
        dictName[objName.pop(0)] = listName.pop(0)
    return dictName


def getGpuName(device):
    try:
        gn = device.Name
        gn=gn.replace("AMD ", "")
        gn=gn.replace("Series ", "")
        gn=gn.replace("Radeon ", "")
        gn=gn.replace("NVIDIA ", "")
        gn=gn.replace("GeForce ", "")
    except:
        gn = "NoData"
    return gn


def getCoreTemp(device):
    ct = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Core" and sensor.SensorType == "Temperature":
                ct = str(math.floor(sensor.getValue()))
    return ct


def getMemoryTemp(device):
    mt = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Memory" and sensor.SensorType == "Temperature":
                ct = str(math.floor(sensor.getValue()))
    return mt


def getFanSpeed(device):
    fs = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Fan" and sensor.SensorType == "Control":
                fs = str(math.floor(sensor.getValue()))
    return fs


def getGpuLoad(device):
    gl = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Core" and sensor.SensorType == "Load":
                gl = str(math.floor(sensor.getValue()))
    return gl


def getCoreVoltage(device):
    cv = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Core" and sensor.SensorType == "Voltage":
                cv = str(math.floor(sensor.getValue() * 1000))
    return cv


def getPower(device):
    pw = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Package" and sensor.SensorType == "Power":
                pw = str(math.floor(sensor.getValue() * 1))
            elif sensor.Name == "GPU Socket" and sensor.SensorType == "Power":
                pw = str(math.floor(sensor.getValue() * 1))
    return pw


def getCoreClock(device):
    cc = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Core" and sensor.SensorType == "Clock":
                cc = str(math.floor(sensor.getValue()))
    return cc


def getMemoryClock(device):
    mc = "NoData"
    if len(device.Sensors) > 0:
        for sensor in device.Sensors:
            if sensor.Name == "GPU Memory" and sensor.SensorType == "Clock":
                mc = str(math.floor(sensor.getValue()))
    return mc



def save_dict_to_file(dic, rin):
    f = open(rin+'.txt','w')
    f.write(str(dic))
    f.close()


def load_dict_from_file(rin):
    f = open(rin+'.txt','r')
    data=f.read()
    f.close()
    return eval(data)


def sendData(rin):
    
    rigName = environ.get('worker')
    path = rigName+'.txt'
    fileName = os.path.basename(path)
    print(getTime() + " Encoding file...")
    fileNameEnc = fileName.encode()
    print(getTime() + " Creating socket...")
    s = socket.socket()
    print(getTime() + " Connecting...")
    s.connect((hostname, TCP_PORT))
    print(getTime() + " Sending...")
    s.send(fileNameEnc)
    time.sleep(0.05)
    file_to_send = open(path, "rb")
    data = file_to_send.read(1024)
    print(getTime() + " Started...")
    while data:
        s.send(data)
        data = file_to_send.read(1024)

    file_to_send.close()
    print(getTime() + " Done!")
    s.shutdown(2)
    s.close()


def getTime():
    return datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]



    

if __name__ == '__main__':


    while(1):
                     
            
        rigName = environ.get('worker')
        print("\n" + rigName)
        
        
        print(getTime() + " Starting data collection...")
        myPc = SystemInfo()
        print(getTime() + " Data collected!")
        
        gpuDict = {}
        
        try:
            gpuDict = collectGpuInfo(myPc.GPU)
        except:
            print(getTime() + " Unable to read GPUs Info!")
        gpuDict['workerName'] = rigName
        gpuDict['timeNow'] = str(int(time.time()))
        gpuDict['cpuName'] = getCpuName(myPc.CPU)
        try:
            gpuDict['cpuLoad'] = collectCpuLoad(myPc.CPU)
        except:
            print(getTime() + " Unable to read CPU Load!")
        try:
            gpuDict['cpuTemp'] = collectCpuTemp(myPc.CPU)
        except:
            print(getTime() + " Unable to read CPU Temp!")
        try:
            gpuDict['cpuPwr'] = collectCpuPwr(myPc.CPU)
        except:
            print(getTime() + " Unable to read CPU Power!")
        
        gpuDict['rigName'] = str(rigName)
        gpuDict['uptimeSec'] = str(int(uptime()))
        save_dict_to_file(gpuDict, rigName)
    

        try:
            sendData(rigName)
            
        except:
            print(getTime() + " Data not send!")
            

        print(getTime() + " Waiting for the right moment...")
        time.sleep(7)




