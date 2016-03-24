from . import media
from .transport import KurentoTransport


class KurentoClient(object):
    def __init__(self, url, transport=None):
        self.url = url
        self.transport = transport or KurentoTransport(self.url)

    def get_transport(self):
        return self.transport

    def create_pipeline(self):
        return media.MediaPipeline(self)

    def get_pipeline(self, id):
        return media.MediaPipeline(self, id=id)
