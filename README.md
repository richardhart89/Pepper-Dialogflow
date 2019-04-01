# PepperChat
## Integration of Dialogflow with Pepper

**Notes:** 
1. This application will not work without a Pepper. In order to use Dialogflow, it must have something to send to it. Without a Pepper, there is no audio to send.

2. Although the method used to call Dialogflow uses that for streaming audio, the audio is not yet streamed. It is not clear that streaming should be used. It may help reduce the latency seen.

### About this project

This is the inital work for integrating Dialogflow with Pepper. It consists of an export of PepperChat.zip which is the current implementation of the chatbot for Pepper. The remaining Python code runs on your laptop.

When Pepper and your laptop are connected to the same WiFi network, Pepper will be given an IP address. This IP address will need to be configured in the main.py file on line 7.
```
IP = "127.0.0.1" #Change this to Pepper's IP address
```

This was tested and run on my private GCP account using Dialogflow Standard Edition. Tests indicated that without really good WiFi connections, the latency of the response is not acceptable. The testing lab I used has poor WiFi. Tethering to my iPhone showed marked improvement in latency effects but it was still disappointing.

You will need to create your own GCP account and activate the Dialogflow API. Follow the GCP documentation to setup your personal Dialogflow and generate your service account key.

This software requires the use of a service account key. Download your service account key JSON file and create a GOOGLE_APPLICATION_CREDENTIALS environment variable pointing to the JSON file.

Import the PepperChat.zip agent as your agent into your GCP Dialogflow project.

This application does not prevent Pepper from using the dialogs already loaded into Pepper. Some of the responses in PepperChat are also found in dialogs on Pepper. If Pepper understands what was said, Pepper himself may respond before PepperChat does. Only load the Pepper dialogs you really need and allow PepperChat to do most of the responses.

The integration with Pepper requires the use of the Action field. There are a few different ways it can be used.

pepper_recorder.py listens to the microphone input from Pepper. When a block of recorded speech is detected, it is sent to the detect_intent_stream.py code. This code was taken directly from Google code and modified to perform the following actions:

## say
If the only thing you want Pepper to do is say some text, then use 'say' as your action code. For more information of the say action, look at Softbank documentation for Naoqi and Pepper.

## behavior
This reflects the Naoqi API documentation for ALBehaviorManager. Any behavior that is installed on Pepper can be run from this application. The only thing to put in the response text is the path to the behavior. This is the preferred way to allow Pepper to do more than saying something. Behaviors are created and installed with Choregraphe (not strictly true but it is how I work with Pepper). Included in this project is a telljokes-noncollab-2691b9-0.0.8.pkg. This is a Pepper application package that tells random jokes that can be installed on Pepper. It has been set to not be a collaborative dialog so Pepper himself does not respond to "Tell me a joke," so that only the chatbot will respond.

## url
This makes use of the Naoqi API ALTabletService to display an image to the tablet using the showImage method. Place the full http(s)://path-to-image. Alternatively, if you do not specify 'http(s)://' then the path is relative to Pepper's internal file structure. This means that the file must be installed on Pepper in a html subdirectory of a given package. This functionality needs to be better designed because there is no method to tell the tablet to stop showing the image.

## web
This is not implemented for much the same reason that only part of url is implemented, i.e. the lack of a way to stop showing the web page. It too could use the ALTbletService but call the showWebview method. Likewise with url above, if 'http(s)://' is not specified then the path is from the named package installed on Pepper in a html subdirectory. Mostly the web interface should not be used in this way. Web pages are normally interactive. Just displaying a web page on Pepper's tablet is usually not enough. In most cases, you want to be able to pass some information back to Pepper using Pepper memory events. If that is the case then it is better to make a Choregraphe package that deals with interactive tablet functions and just use the behavior action.

## dialog
If you don't already have a behavior created for Pepper, this can be used to, in essence, create a behavior. Knowledge of QiChat is necessary. Anything that you can do in QiChat, you can do here. The only thing you do not have to do is make the topic: and language: entries. This uses a fixed topic and English only. If an other language is necessary, this application can be modified to suit the desired language. I have not yet found a way to do everything you can with QiChat. Displaying web pages for example. But, at the very least, you can make use of the QiChat heirarchy to make a quasi-conversation and set Pepper memory and event values.
