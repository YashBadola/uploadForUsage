from picamera import PiCamera
import cv2
import threading
from picamera.array import PiRGBArray

class ScopeStream:
    stopped = False
    capureImage = False
    saveImage = False
    resolution = (320, 240)
    #class variables for checks as can be varied from outside or instance variable if defined in a function
    def __init__(self):
        self.camera = picamera.PiCamera(sensor_mode=2)
        self.camera.resolution = (2592, 1944)
        self.set_fps = 32
        self.rawCaptureHiRes = PiRGBArray(camera, size=(2592, 1944))
        self.rawCaptureVideo = PiRGBArray(camera, size=(640, 480))
        t = Thread(target=self.initStream, args=())
		t.daemon = True
		t.start()

    def start_stream_object(self):
		# start the thread to read frames from the video stream
		t = Thread(target=self.startStream, args=())
		t.daemon = True
		t.start()

    def initStream(self):
        '''capture stream and images in a loop'''
        while True:
            self.camera.capture(self.rawCaptureVideo, splitter_port=0, resize=(640, 480), format="bgr", use_video_port=True)
            # if self.rawCaptureVideo.array is not None:
            #     img = cv2.cvtColor(self.rawCaptureVideo.array, cv2.COLOR_BGR2GRAY)

            if ScopeStream.capureImage: # once in a while, not very often, i need a high res frame
                self.rawCaptureHiRes.truncate(0)
                self.camera.capture(self.rawCaptureHiRes, splitter_port=1,resize = ScopeStream.resolution format="bgr", use_video_port=True)
                self.img = self.rawCaptureHiRes.array
                
                ScopeStream.capureImage = False
            
            self.rawCaptureVideo.truncate(0)
            if ScopeStream.stopped:
				self.stream.close()
				self.rawCapture.close()
				self.camera.close()
				return

    def startStream(self):
        '''streaming'''
        for f in self.rawCaptureVideo:
			# grab the frame from the stream and clear the stream in
			# preparation for the next frame
			frame = f.array
			self.rawCapture.truncate(0)			
            img=self.func(frame)
            # self.img=img
            ret, jpeg = cv2.imencode('.jpg', img)
            img=jpeg.tobytes()
            time.sleep((1/self.set_fps)  -0.0047)
            if ScopeStream.capureImage==True:
                self.snap()
                ScopeStream.capureImage=False

            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

    def wait(self):
        self.thread.join()
        
    def capture_still(self,filename=None):
        if filename is not None:
            ScopeStream.stillfilename=filename
        else:
            ScopeStream.stillfilename= 'snap_'+str(int(time.time()))+'.jpg'
        print("Still Capture")
        ScopeStream.still_cap=True

    def snap(self,res = None,save = False):
        '''returns and saves images with any resolution'''
        if res is not None:
            ScopeStream.resolution = res
        ScopeStream.capureImage = True
        if save:
            cv2.imwrite("testhrs.jpg", img2)
        return self.img

             