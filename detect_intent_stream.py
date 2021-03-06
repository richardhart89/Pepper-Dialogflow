#!/usr/bin/env python
# Copyright 2017 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""DialogFlow API Detect Intent Python sample with audio files processed
as an audio stream.

Examples:
  python detect_intent_stream.py -h
  python detect_intent_stream.py --project-id PROJECT_ID \
  --session-id SESSION_ID --audio-file-path resources/book_a_room.wav
  python detect_intent_stream.py --project-id PROJECT_ID \
  --session-id SESSION_ID --audio-file-path resources/mountain_view.wav
"""
# [START dialogflow_detect_intent_streaming]

import argparse
import uuid
import logging
from naoqi import qi
import traceback

def detect_intent_stream(project_id, session_id, audio_file_path,
                         language_code, ip):
    """Returns the result of detect intent with streaming audio as input.

    Using the same `session_id` between requests allows continuation
    of the conversaion."""
    import dialogflow_v2 as dialogflow
    from dialogflow_v2.proto.session_pb2 import QueryInput
    from dialogflow_v2.proto.session_pb2 import StreamingDetectIntentRequest
    from dialogflow_v2.proto.session_pb2 import InputAudioConfig

    session_client = dialogflow.SessionsClient()

    # Note: hard coding audio_encoding and sample_rate_hertz for simplicity.
    audio_encoding = dialogflow.enums.AudioEncoding.AUDIO_ENCODING_LINEAR_16
    sample_rate_hertz = 16000

    session_path = session_client.session_path(project_id, session_id)
    #print('Session path: {}\n'.format(session_path))

    def request_generator(audio_config, audio_file_path):
        query_input = QueryInput(audio_config=audio_config)

        # The first request contains the configuration.
        yield StreamingDetectIntentRequest(
            session=session_path, query_input=query_input)

        # Here we are reading small chunks of audio data from a local
        # audio file.  In practice these chunks should come from
        # an audio input device.
        #with open(audio_file_path, 'rb') as audio_file:
        while True:
            chunk = audio_file_path.read(4096)
            if not chunk:
                break
            # The later requests contains audio data.
            yield StreamingDetectIntentRequest(
                input_audio=chunk)

    audio_config = InputAudioConfig(
        audio_encoding=audio_encoding, language_code=language_code,
        sample_rate_hertz=sample_rate_hertz)

    requests = request_generator(audio_config, audio_file_path)
    responses = session_client.streaming_detect_intent(requests)

    print('=' * 20)
    if responses is not None:
        print(str(responses))
    else:
        print("responses is None")
    for response in responses:
        print('Intermediate transcript: "{}".'.format(
                response.recognition_result.transcript))

    # Note: The result from the last response is the final transcript along
    # with the detected content.
    query_result = response.query_result
    
    print('=' * 20)
    print('Query text: {}'.format(query_result.query_text))
    print('Detected intent: {} (confidence: {}) action code: {}\n'.format(
        query_result.intent.display_name,
        query_result.intent_detection_confidence,
        query_result.action))
    print('Fulfillment text: {}\n'.format(
        query_result.fulfillment_text))
    
    if query_result.intent_detection_confidence > 0.5:
        session = qi.Session()
        try:
            session.connect("tcp://{}:{}".format(ip, 9559))
            
            if query_result.action.lower() == "say":
                #print 'get ALTextToSpeech'
                tts = session.service("ALTextToSpeech")
                #print 'say text'
                tts.say(query_result.fulfillment_text)
                #tts.close()
            elif query_result.action.lower() == "dialog":
                do_dialog(query_result, session)
            elif query_result.action.lower() == "behavior":
                behaviorName = query_result.fulfillment_text
                bm = session.service("ALBehaviorManager")
                try:
                    bm.stopBehavior(behaviorName)
                except:
                    pass
                bm.runBehavior(behaviorName)
            elif query_result.action.lower() == "url":
                do_tablet(query_result, session)
            else:
                #print 'get ALTextToSpeech'
                tts = session.service("ALTextToSpeech")
                #print 'say text'
                tts.say(query_result.fulfillment_text)
        except:
            traceback.print_exc()
            raise "session.connect failed."
        finally:
            session.close()
        
# [END dialogflow_detect_intent_streaming]

def do_dialog(query_result, session):
    #print "attempting to send ALDialog to Pepper"
    baseDialog = ("topic: ~pepperChat_topic()\n"
                  "language: enu\n"
                  "proposal: {}\n")
    
    #unload toppic if it exists
    dialog = session.service("ALDialog")
    try:
        dialog.unloadTopic("pepperChat_topic")
    except:
        pass
    
    dialog.setLanguage("English")
    
    topicContent = baseDialog.format(query_result.fulfillment_text)
    #print topicContent
    try:
        topicName = dialog.loadTopicContent(topicContent)
    except:
        traceback.print_exc()
        raise "loadTopicContent failed."
    #print 'topic name: ' + topicName
    #print 'activate topic'
    dialog.activateTopic(topicName)
    #print 'subscribe'
    dialog.subscribe('my_dialog_example')
    #print 'setting focus'
    dialog.setFocus('pepperChat_topic')
    #print 'forcing output'
    dialog.forceOutput()

def do_tablet(query_result, session):
    try:
        tabletService = session.service("ALTabletService")
    except Exception as e:
        logging.error(e)
        
    # We create TabletService here in order to avoid
    # problems with connections and disconnections of the tablet during the life of the application
    tabletService = session.service("ALTabletService")
    if tabletService:
        try:
            url = query_result.fulfillment_text
            if url == '':
                logging.error("URL of the image is empty")
            tabletService.showImage(url)
        except Exception as err:
            logging.error("Error during ShowImage : %s " % err)
    else:
        logging.warning("No ALTabletService, can't display the web object.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        '--project-id',
        help='Project/agent id.  Required.',
        required=True)
    parser.add_argument(
        '--session-id',
        help='Identifier of the DetectIntent session. '
        'Defaults to a random UUID.',
        default=str(uuid.uuid4()))
    parser.add_argument(
        '--language-code',
        help='Language code of the query. Defaults to "en-US".',
        default='en-US')
    parser.add_argument(
        '--audio-file-path',
        help='Path to the audio file.',
        required=True)

    args = parser.parse_args()

    detect_intent_stream(
        args.project_id, args.session_id, args.audio_file_path,
        args.language_code)
