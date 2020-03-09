from flask import Flask, Request, Response, render_template
from imutils.video import FileVideoStream
import cv2
import time

app = Flask(__name__)
app.debug = True

@app.route('/')
def index():
    return render_template('index.html')

def read_feed():    
    cap = FileVideoStream('sample/fish3.mp4').start()
    time.sleep(2.0)
    while cap.more():
        frame = cap.read()        
        jpeg_frame = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])[1]
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + jpeg_frame.tostring() + b'\r\n')

@app.route('/video_feed')
def video_feed():    
    return Response(read_feed(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()