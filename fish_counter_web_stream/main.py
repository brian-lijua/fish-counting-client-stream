from flask import Flask, request, Response, render_template, stream_with_context
from imutils.video import FileVideoStream
import os
import cv2
import time
import datetime
from threading import Thread
from queue import Queue

app = Flask(__name__)
app.debug = True

VIDEO_HEIGHT = None
VIDEO_WIDTH = None

VIDEO_IS_RECORDING = False
VIDEO_WRITER_THREAD = None
VIDEO_WRITER_QUEUE = None

@app.route('/')
def index():
    return render_template('index.html')

def read_feed():    
    cap = FileVideoStream('sample/fish3.mp4').start()
    frame = cap.read()

    global VIDEO_HEIGHT, VIDEO_WIDTH
    VIDEO_HEIGHT, VIDEO_WIDTH = frame.shape[:2]

    time.sleep(2.0)
    try:
        while cap.more():
            frame = cap.read()
            jpeg_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])[1]

            if VIDEO_IS_RECORDING:
                VIDEO_WRITER_QUEUE.put(frame)

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame.tostring() + b'\r\n')
    finally:
        cap.stop()        

@app.route('/video_feed')
def video_feed():    
    return Response(stream_with_context(read_feed()), mimetype='multipart/x-mixed-replace; boundary=frame')

def writeToVide(q):
    filename =  '{}.avi'.format(datetime.datetime.now().strftime("%Y%m%d_%H%M%S"))
    filepath = os.path.join('temp', filename)    
    fourcc = cv2.VideoWriter_fourcc('M', 'J', 'P', 'G')
    writer = cv2.VideoWriter(filepath, fourcc, 30.0, (int(VIDEO_WIDTH), int(VIDEO_HEIGHT)))
    # global VIDEO_IS_RECORDING
    while True:
        frame = q.get()
        writer.write(frame)

        q.task_done()

        if VIDEO_IS_RECORDING == False:
            break

    print('Ending write to video')

@app.route('/start_recording', methods=['POST'])
def start_recording():
    t = request.values['type']    
    global VIDEO_WRITER_QUEUE, VIDEO_WRITER_THREAD, VIDEO_IS_RECORDING
    if t == 'start':
        VIDEO_IS_RECORDING = True
        VIDEO_WRITER_QUEUE = Queue()
        VIDEO_WRITER_THREAD = Thread(target=writeToVide, args=(VIDEO_WRITER_QUEUE, ))
        # VIDEO_WRITER_THREAD.daemon = True
        VIDEO_WRITER_THREAD.start()
        return Response('started')
    elif t == 'stop':
        VIDEO_IS_RECORDING = False
        with VIDEO_WRITER_QUEUE.mutex:
            VIDEO_WRITER_QUEUE.queue.clear()
        VIDEO_WRITER_QUEUE = None
        VIDEO_WRITER_THREAD.join()
        VIDEO_WRITER_THREAD = None

        return Response('stopped')
    else:
        return Response('Invalid resposned')
    
if __name__ == '__main__':
    app.run()