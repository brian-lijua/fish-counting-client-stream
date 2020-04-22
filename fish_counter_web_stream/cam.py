from multiprocessing import Process
from threading import Thread
import cv2

from imutils.video import WebcamVideoStream

class Cam:
    frames = []
    frame = None
    process = None
    cap = None

    def __gstreamer_pipeline(
        self,
        capture_width=1280,
        capture_height=720,
        display_width=1280,
        display_height=720,
        framerate=60,
        flip_method=0
    ):
        return (
            "nvarguscamerasrc ! "
            "video/x-raw(memory:NVMM), "
            "width=(int)%d, height=(int)%d, "
            "format=(string)NV12, framerate=(fraction)%d/1 ! "
            "nvvidconv flip-method=%d ! "
            "video/x-raw, width=(int)%d, height=(int)%d, format=(string)BGRx ! "
            "videoconvert ! "
            "video/x-raw, format=(string)BGR ! appsink"
            % (
                capture_width,
                capture_height,
                framerate,
                flip_method,
                display_width,
                display_height,
            )
        )

    def __init__(self, name='VideoCamReader'):
        print(self.__gstreamer_pipeline(framerate=60 ,flip_method=0))
        self.stream = cv2.VideoCapture(self.__gstreamer_pipeline(flip_method=0), cv2.CAP_GSTREAMER)
        self.pname = name
        self.stopped = False

    def update(self):
        while True:
            if self.stopped == True:
                return
            self.ok, self.frame = self.stream.read()      
                
    def start(self):
        self.process = Thread(target=self.update, name=self.pname)
        self.process.daemon = True
        self.process.start()
        return self

    def stop(self):
        self.stopped = True
        self.stream.release()
    
    def read(self):
        return self.frame
