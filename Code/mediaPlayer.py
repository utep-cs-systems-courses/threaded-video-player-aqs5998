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

    # get the next frame file name
    inputFrame = colorFrames.dequeue()

    while inputFrame is not None and count < 72:
        print(f'Converting frame {count}')
        inputFrame = np.asarray(bytearray(inputFrame), dtype = np.uint8)
        image = cv2.imdecode(inputFrame, cv2.IMREAD_UNCHANGED)
        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        success, jpgImage = cv2.imencode('.jpg', grayscaleFrame)
        #change it to enqueue into the grayFramesQueue
        grayFrames.enqueue(jpgImage)
        count += 1
        # generate input file name for the next frame
        #TODO change it to dequeue from readFramesQueue
        inputFrame = colorFrames.dequeue() ###
    grayFrames.enqueue(None)
def displayFrames(grayFrames):
    # initialize frame count
    count = 0
    # Generate the filename for the first frame
    #TODO change to read/dequeue from the grayFramesBuffer
    
    # load the frame
    frame = grayFrames.dequeue() 

    while frame is not None:
        print(f'Displaying frame {count}')
        # convert the raw frame to a numpy array
        frame = np.asarray(bytearray(frame), dtype = np.uint8)
        # get a jpg encoded frame
        image = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED)
        # Display the frame in a window called "Video"
        cv2.imshow('Video', image)
        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(42) and 0xFF == ord("q"):
            break
        # get the next frame filename
        count += 1
        #TODO dequeue from grayFramesBuffer the next frame
        # Read the next frame file
        frame = grayFrames.dequeue()
    # make sure we cleanup the windows, otherwise we might end up with a mess
    cv2.destroyAllWindows()

def extractFrames(clipFileName, colorFrames):
    count = 0
    vidcap = cv2.VideoCapture(clipFileName)
    # read one frame
    success,image = vidcap.read()
    print(f'Reading frame {count} {success}')
    while success and count < 72:
        # write the current frame out as a jpeg image
        #Transform into a jpg image
        success, jpgImage = cv2.imencode('.jpg', image)
        colorFrames.enqueue(jpgImage)
        success,image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1
    colorFrames.enqueue(None)
        
class queueThread:
    def __init__(self):
        self.queue=[]
        self.full=threading.Semaphore(0)
        self.empty = threading.Semaphore(24)
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
colorFrames = queueThread()
grayFrames = queueThread()
extraceT = threading.Thread(target = extractFrames, args = (clipFileName, colorFrames))
convertT = threading.Thread(target = convertToGray, args = (clipFileName, colorFrames))
displayT = threading.Thread(target = displayFrames, args = (grayFrames,))
extraceT.start()
convertT.start()
displayT.start()