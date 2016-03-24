import logging

logger = logging.getLogger(__name__)

# This is the object graph as described at http://www.kurento.org/docs/5.0.3/mastering/kurento_API.html
# We dont mimic it precisely yet as its still being built out, not all abstractions are necessary
#                   MediaObject
# Hub               MediaElement                MediaPipeline
#          HubPort    Endpoint    Filter


class MediaType(object):
    AUDIO = "AUDIO"
    VIDEO = "VIDEO"
    DATA = "DATA"


class MediaObject(object):
    def __init__(self, parent, **args):
        self.parent = parent
        self.options = args
        if 'id' in args:
            logger.debug("Creating existing %s with id=%s", self.__class__.__name__, args['id'])
            self.id = args['id']
        else:
            logger.debug("Creating new %s", self.__class__.__name__)
            self.id = self.get_transport().create(self.__class__.__name__, **args)

    def get_transport(self):
        return self.parent.get_transport()

    def get_pipeline(self):
        return self.parent.get_pipeline()

    # todo: remove arguments that have a value of None to let optional params work seamlessly
    def invoke(self, method, **args):
        return self.get_transport().invoke(self.id, method, **args)

    def subscribe(self, event, fn, kwargs):
        def _callback(value):
            fn(self, value, kwargs)
        return self.get_transport().subscribe(self.id, event, _callback)

    def release(self):
        return self.get_transport().release(self.id)


class MediaPipeline(MediaObject):
    def get_pipeline(self):
        return self


class MediaElement(MediaObject):
    def __init__(self, parent, **args):
        args["mediaPipeline"] = parent.get_pipeline().id
        super(MediaElement, self).__init__(parent, **args)

    def connect(self, sink):
        return self.invoke("connect", sink=sink.id)

    def disconnect(self, sink):
        return self.invoke("disconnect", sink=sink.id)

    def set_audio_format(self, caps):
        return self.invoke("setAudioFormat", caps=caps)

    def set_video_format(self, caps):
        return self.invoke("setVideoFormat", caps=caps)

    def get_source_connections(self, media_type):
        return self.invoke("getSourceConnections", mediaType=media_type)

    def get_sink_connections(self, media_type):
        return self.invoke("getSinkConnections", mediaType=media_type)


# ENDPOINTS
class UriEndpoint(MediaElement):
    def get_uri(self):
        return self.invoke("getUri")

    def pause(self):
        return self.invoke("pause")

    def stop(self):
        return self.invoke("stop")


class PlayerEndpoint(UriEndpoint):
    def play(self):
        return self.invoke("play")

    def on_end_of_stream_event(self, fn):
        return self.subscribe("EndOfStream", fn)


class RecorderEndpoint(UriEndpoint):
    def record(self):
        return self.invoke("record")


class SessionEndpoint(MediaElement):
    def on_media_session_started_event(self, fn, **kwargs):
        return self.subscribe("MediaSessionStarted", fn, kwargs)

    def on_media_session_terminated_event(self, fn, **kwargs):
        return self.subscribe("MediaSessionTerminated", fn, kwargs)


class HttpEndpoint(SessionEndpoint):
    def get_url(self):
        return self.invoke("getUrl")


class HttpGetEndpoint(HttpEndpoint):
    pass


class HttpPostEndpoint(HttpEndpoint):
    def on_end_of_stream_event(self, fn):
        return self.subscribe("EndOfStream", fn)


class SdpEndpoint(SessionEndpoint):
    def generate_offer(self):
        return self.invoke("generateOffer")

    def process_offer(self, offer):
        return self.invoke("processOffer", offer=offer)

    def process_answer(self, answer):
        return self.invoke("processAnswer", answer=answer)

    def get_local_session_descriptor(self):
        return self.invoke("getLocalSessionDescriptor")

    def get_remote_session_descriptor(self):
        return self.invoke("getRemoteSessionDescriptor")


class RtpEndpoint(SdpEndpoint):
    pass


class WebRtcEndpoint(SdpEndpoint):
    def add_ice_candidate(self, candidate):
        return self.invoke('addIceCandidate', candidate=candidate)

    def gather_candidates(self):
        return self.invoke('gatherCandidates')

    def on_ice_candidate(self, fn, **kwargs):
        return self.subscribe("OnIceCandidate", fn, kwargs)


# FILTERS

class GStreamerFilter(MediaElement):
    pass


class FaceOverlayFilter(MediaElement):
    def set_overlayed_image(self, uri, offset_x, offset_y, width, height):
        return self.invoke("setOverlayedImage", uri=uri, offsetXPercent=offset_x, offsetYPercent=offset_y, widthPercent=width, heightPercent=height)


class ZBarFilter(MediaElement):
    def on_code_found_event(self, fn):
        return self.subscribe("CodeFound", fn)


# VTT AR Thing

class OverlayType(object):
    TYPE2D = 'TYPE2D'
    TYPE3D = 'TYPE3D'


class ArKvpString(dict):
    def __init__(self, key=None, value=None):
        self['__module__'] = "armarkerdetector"
        self['__type__'] = "ArKvpString"
        if not isinstance(value, basestring):
            raise TypeError
        self['key'] = key
        self['value'] = value

    def __getattr__(self, attr):
        if attr is not self['key']:
            raise KeyError
        return self['value']

    def __setattr__(self, attr, value):
        if not isinstance(value, basestring):
            raise TypeError
        self['key'] = attr
        self['value'] = value


class ArKvpFloat(dict):
    def __init__(self, key=None, value=None):
        self['__module__'] = "armarkerdetector"
        self['__type__'] = "ArKvpFloat"
        if not isinstance(value, float):
            raise TypeError
        self['key'] = key
        self['value'] = value

    def __getattr__(self, attr):
        if attr is not self['key']:
            raise KeyError
        return self['value']

    def __setattr__(self, attr, value):
        if not isinstance(value, float):
            raise TypeError
        self['key'] = attr
        self['value'] = value


class ArKvpInteger(dict):
    def __init__(self, key=None, value=None):
        self['__module__'] = "armarkerdetector"
        self['__type__'] = "ArKvpInteger"
        if not isinstance(value, int):
            raise TypeError
        self['key'] = key
        self['value'] = value

    def __getattr__(self, attr):
        if attr is not self['key']:
            raise KeyError
        return self['value']

    def __setattr__(self, attr, value):
        if not isinstance(value, int):
            raise TypeError
        self['key'] = attr
        self['value'] = value


class ARThing(dict):
    def __init__(self, markerId, overlayType):
        self['__module__'] = "armarkerdetector"
        self['__type__'] = "ArThing"
        self['integers'] = []
        self['floats'] = []
        self['strings'] = []
        self['markerId'] = markerId
        self['overlayType'] = overlayType

    def __getattr__(self, attr):
        if attr is not 'strings' and attr is not 'integers' and attr is not 'floats' and attr is not 'overLayType' and attr is not 'markerId':
            return KeyError
        return self[attr]

    def __setattr__(self, attr, value):
        if attr is not 'strings' and attr is not 'integers' and attr is not 'floats' and attr is not 'overLayType' and attr is not 'markerId':
            raise KeyError
        self[attr] = value

    def setMarkerId(self, id):
        self['markerid'] = id

    def setOverlayType(self, type):
        self['overlayType'] = type

    def addString(self, key, value):
        self['strings'].append(ArKvpString(key, value))

    def addFloat(self, key, value):
        self['floats'].append(ArKvpFloat(key, value))

    def addInteger(self, key, value):
        self['integers'].append(ArKvpInteger(key, value))


class ArMarkerdetector(MediaElement):
    def setShowDebugLevel(self, level):
        return self.invoke("setShowDebugLevel", showDebugLevel=level)

    def setArThing(self, arThingsList):
        return self.invoke("setArThing", arThing=arThingsList)

    def enableAugmentation(self, enable):
        return self.invoke("enableAugmentation", enable=enable)

    def enableAugmentationSet(self, arset):
        return self.invoke("enableAugmentationSet", arset=arset)

    def disableAugmentationSet(self, arset):
        return self.invoke("disableAugmentationSet", arset=arset)

    def setMarkerPoseFrequency(self, enable, frequency):
        return self.invoke("setMarkerPoseFrequency", enable=enable, frequency=frequency)

    def setMarkerPoseFrameFrequency(self, enable, frequency):
        return self.invoke("setMarkerPoseFrameFrequency", enable=enable, frequency=frequency)

    def enableMarkerCountEvents(self, enable):
        return self.invoke("enableMarkerCountEvents", enable=enable)

    def setPose(self, _id, _type, value):
        return self.invoke("setPose", id=_id, type=_type, value=value)

    def onMarkerCount(self, fn):
        return self.subscribe("MarkerCount", fn)

    def onMarkerPose(self, fn):
        return self.subscribe("MarkerPose", fn)
'''

{
    "name": "ArMarkerPose",
    "doc": "Pose doc",
    "typeFormat": "REGISTER",
    "properties": [
        {
            "name": "markerId",
            "doc": "marker id",
            "type": "int"
        },
        {
            "name": "matrixModelview",
            "doc": "marker modelview matrix",
            "type": "float[]"
        }
    ]
},
],
  "events": [
    {
      "name": "MarkerCount",
      "extends": "Media",
      "doc": "An event that is sent when the number of visible markers is changed. Tracking coordinates for the markers is going to be sent with some other approach.",
      "properties": [
        {
          "name": "sequenceNumber",
          "doc": "sequence number",
          "type": "int"
        },
        {
          "name": "countTimestamp",
          "doc": "countTimestamp",
          "type": "int"
        },
        {
          "name": "markerId",
          "doc": "marker id",
          "type": "int"
        },
        {
          "name": "markerCount",
          "doc": "Number of visible markers with the specified id",
          "type": "int"
        },
        {
          "name": "markerCountDiff",
          "doc": "How much the markerCount was changed from the previous situation",
          "type": "int"
        }
      ]
    },
 {
      "name": "MarkerPose",
      "extends": "Media",
      "doc": "Matrices for marker pose",
      "properties": [
        {
          "name": "sequenceNumber",
          "doc": "sequence number",
          "type": "int"
        },
        {
          "name": "poseTimestamp",
          "doc": "poseTimestamp",
          "type": "int"
        },
        {
          "name": "width",
          "doc": "resolution width",
          "type": "int"
        },
        {
          "name": "height",
          "doc": "resolution height",
          "type": "int"
        },
        {
          "name": "matrixProjection",
          "doc": "marker projection matrix",
          "type": "float[]"
        },
        {
          "name": "markerPose",
          "doc": "markerPose",
          "type": "ArMarkerPose[]"
        }       
      ]
    }
  ]
}

'''


# HUBS

class Composite(MediaElement):
    pass


class Dispatcher(MediaElement):
    pass


class DispatcherOneToMany(MediaElement):
    pass
