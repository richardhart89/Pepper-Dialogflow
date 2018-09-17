# -*- encoding: UTF-8 -*- 
from naoqi import ALBroker
import threading
from pepper_recorder import SoundProcessingModule
    
if __name__ == '__main__':
    #IP = "10.10.200.26" # Pepper PwC-ExpLab1
    IP = "172.20.10.2" # Using my iPhone
    # IP= "192.168.0.144"
    # Creation of a new Python Broker
    stop_recognition = threading.Event()
    pythonBroker = ALBroker("pythonBroker","0.0.0.0",9999, IP, 9559)

    print("connected")
    MySoundProcessingModule = SoundProcessingModule("MySoundProcessingModule", IP, stop_recognition)
    MySoundProcessingModule.startProcessing()

    pythonBroker.shutdown()
    print("disconnected")