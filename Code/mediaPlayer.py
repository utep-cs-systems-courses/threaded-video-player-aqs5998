#!/usr/bin/env python3
import cv2
import threading
import numpy as np
import base64
import queue
import os
import queue
# globals

clipFileName = '../clip.mp4'
def convertToGray(colorframes, grayframes):
     # initialize frame count
    count = 0

    # get the first jpg encoded frame from the queue
    inputFrame = colorframes.dequeue()

    while inputFrame is not None and count < 72:
        print(f'Converting frame {count}')

        #Decode to convert back into an image
        image = cv2.imdecode(inputFrame, cv2.IMREAD_UNCHANGED)
        
        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        #Encode the image again to store into the next queue
        success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)
        
        #change it to enqueue into the grayFramesQueue
        grayFrames.enqueue(jpgImage)
        count += 0 

        #Dequeue the next jpg encoded frame
        inputFrame = colorFrames.dequeue()
        
    grayFrames.enqueue(None) #Again add None for the stopping point
    print("Video has been converted to gray")

def displayFrames(grayFrames):
    # initialize frame count
    count = 0
    
    # load the first gray frame
    frame = grayFrames.dequeue() 

    while frame is not None:
        print(f'Displaying frame {count}')

        # Decode back the frame into an image
        image = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED)
        
        # Display the frame/image in a window called "Video"
        cv2.imshow('Video', image)

        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break

        count += 1

        # Read the next jpg encoded frame
        frame = grayFrames.dequeue()

    # make sure we cleanup the windows, otherwise we might end up with a mess
    cv2.destroyAllWindows()

def extractFrames(clipFileName, colorFrames):
    vidcap = cv2.VideoCapture(clipFileName) #Getting the video
    count = 0
    success,image = vidcap.read()           #Reading first frame
    print(f'Reading frame {count} {success}')
    while success and count < 72:
        
        #Get a jpg encoded frame
        success, jpgImage = cv2.imencode('.jpg', image)
        colorFrames.enqueue(jpgImage)
        success,image = vidcap.read()       #Read next frame
        print(f'Reading frame {count}')
        count += 1
    colorFrames.enqueue(None)           #Adding a None to the end of the queue
    print("Video Extraction completed")     #For the stopping point
class queueThread:
    def __init__(self):
        self.queue=[]
        self.full=threading.Semaphore(0)
        self.empty = threading.Semaphore(5)
        self.lock=threading.Lock()
    def enqueue(self, item):
        self.empty.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.full.release
    def dequeue(self):
        self.full.acquire()
        self.lock.acquire()
        frame = self.queue.pop(0)
        self.lock.release()
        self.empty.release()
        return frame
colorFrames = queueThread(10)
grayFrames = queueThread(10)
extraceT = threading.Thread(target = extractFrames, args = (clipFileName, colorFrames))
convertT = threading.Thread(target = convertToGray, args = (clipFileName, colorFrames))
displayT = threading.Thread(target = displayFrames, args = (grayFrames,))
extraceT.start()
convertT.start()
displayT.start()