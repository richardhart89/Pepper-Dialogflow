
"""Sample that streams audio to the Google Cloud Speech API via GRPC."""

from __future__ import division

import logging
import uuid

from detect_intent_stream import detect_intent_stream

class Dialogflow(object):
    pass

def thread_method(queue):
    df = Dialogflow()
    
    logging.debug("thread started")

    while True:
        if not queue.empty():
            chunck = queue.get()
            data = chunck
            if not data:
                raise StopIteration()

            # Subsequent requests can all just have the content
            yield detect_intent_stream("pepper-7c1d6", uuid.uuid4(), data)
