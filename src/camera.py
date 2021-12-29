import cv2
from interfaces.videoInputInterface import VideoInputInterface

class Camera(VideoInputInterface):
    def __init__(self, videoInputSize):
        self.webcam = cv2.VideoCapture(0)
        self.frameSize = videoInputSize
        self.centerPos = [int(self.frameSize[0]/2), int(self.frameSize[1]/2)]
        self.centerZone = int(self.frameSize[1]/6)

    def getFrame(self):
        _, self.frame = self.webcam.read()
        self.frame = cv2.resize(self.frame, self.frameSize)
        return self.frame

