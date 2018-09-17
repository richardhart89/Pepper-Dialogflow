# -*- encoding: UTF-8 -*- 
import StringIO
from threading import Thread
from Queue import Queue
from naoqi import ALModule, ALProxy
import numpy as np
import time
import logging
import uuid
import traceback
import wave
    
from dialogflow_thread import thread_method
from detect_intent_stream import detect_intent_stream

LISTEN_RETRIES = 10

class SoundProcessingModule(ALModule):
    def __init__( self, name, ip, stop_recognition):
        try:
            ALModule.__init__( self, name );
        except Exception as e:
            logging.error(str(e))
            pass
        print("connected")
        self.ip = ip
        self.BIND_PYTHON( name, "processRemote")
        self.ALAudioDevice = ALProxy("ALAudioDevice", self.ip, 9559)
        self.framesCount=0
        self.count = LISTEN_RETRIES
        self.recordingInProgress = False
        #self.noise = None
        self.stopRecognition = stop_recognition
        #self.recognitionQueue = recognition_queue
        #self.session_id = session_id
        self.uuid = uuid.uuid4()
        self.previous_sound_data = None

    def startRecording(self, previous_sound_data):
        """init a in memory file object and save the last raw sound buffer to it."""
        self.outfile = StringIO.StringIO()
        self.procssingQueue = Queue()
        #self.processingThread = Thread(target=thread_method, args=(self.procssingQueue, ))
        #print("Thread returned: " + str(self.processingThread))
        #self.processingThread.start()
        self.recordingInProgress = True
        if not previous_sound_data is None:
            self.procssingQueue.put(previous_sound_data[0].tostring())
            self.outfile.write(previous_sound_data[0].tostring())
        print("start recording")

    def stopRecording(self):
        """saves the recording to disk"""
        print("stopped recording")
        self.previous_sound_data = None
        self.outfile.seek(0)
        try:
            detect_intent_stream("pepper-7c1d6", self.uuid, self.outfile, "en-US", self.ip)
        except:
            traceback.print_exc()
        #print "detection ended"        
        self.recordingInProgress = False
        #self.stopRecognition.set()

    def startProcessing(self):
        """init sound processing, set microphone and stream rate"""
        print("startProcessing")
        self.ALAudioDevice.setClientPreferences(self.getName(), 16000, 3, 0)
        self.ALAudioDevice.subscribe(self.getName())

        #TODO(Lilith) remove this
        while not self.stopRecognition.is_set():
            time.sleep(1)

        self.ALAudioDevice.unsubscribe(self.getName()) 

    def processRemote(self, nbOfChannels, nbOfSamplesByChannel, timeStamp, inputBuffer):
        """audio stream callback method with simple silence detection"""
        #print(str(self.count) + " " + str(self.recordingInProgress))
        self.framesCount = self.framesCount + 1;

        sound_data_interlaced = np.fromstring(str(inputBuffer), dtype=np.int16)
        sound_data = np.reshape(sound_data_interlaced, (nbOfChannels, nbOfSamplesByChannel), 'F')
        peak_value = np.max(sound_data)
        

        # noise reduction based on the first frame
        #print(np.min(sound_data))
        #print(np.max(sound_data))
        #sound_data[0] = lfilter(700, np.min(self.noise), sound_data[0])

        # detect sound
        if peak_value > 14000:
            print "Peak:", peak_value
            self.count = LISTEN_RETRIES

            if not self.recordingInProgress:
                self.startRecording(self.previous_sound_data)
        

        #print("Frames Left: "+ str(self.count))

        # if there is no sound for a few seconds we end the current recording and start audio processing
        if self.count <= 0 and self.recordingInProgress:
            #print("count <= 0: calling stopRecording()")
            self.stopRecording()
            #self.count = LISTEN_RETRIES

        # if recording is in progress we save the sound to an inmemory file
        if self.recordingInProgress:
            self.count -= 1
            self.previous_data = sound_data
            self.procssingQueue.put(sound_data[0].tostring())
            self.outfile.write(sound_data[0].tostring())