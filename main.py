# -*- encoding: UTF-8 -*- 
from naoqi import ALBroker
import threading
from pepper_recorder import SoundProcessingModule
    
if __name__ == '__main__':
    IP = "127.0.0.1" #Change this to Pepper's IP address
    # Creation of a new Python Broker
    stop_recognition = threading.Event()
    pythonBroker = ALBroker("pythonBroker","0.0.0.0",9999, IP, 9559)

    print("connected")
    MySoundProcessingModule = SoundProcessingModule("MySoundProcessingModule", IP, stop_recognition)
    MySoundProcessingModule.startProcessing()

    pythonBroker.shutdown()
    print("disconnected")