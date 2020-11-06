#!/usr/bin/env python3
import cv2
import threading
import numpy as np
import base64
import queue
import os
import queue

# globals
outputDir    = 'frames'
clipFileName = '../clip.mp4'
def convertToGray(colorframes, grayframes):
    count = 0 #Initialize frame count

    #going through color frames
    while True:
        print('Converting frame {count}')

        #get frames
        getFrame = colorframes.dequeue()
        if getFrame == '!':
            break
        
        #convert to grayscale
        grayscaleFrame = cv2.cvtColor(getFrame, cv2.COLOR_BGR2GRAY)

        #put gray frames in queue
        grayframes.enqueue(grayscaleFrame)
        
        count += 1

    print('Converting to gray done!')
    grayframes.enqueue('!')


def displayFrames(grayFrames):
    count = 0 #Initialize frame count

    #going through gray frames
    while True:
        print(f'Displaying Frame{count}')

        #get next frame
        frame = grayFrames.dequeue()
        if frame == '!':
            break
        
        #display image called Video
        cv2.imshow('Video', frame)
        #wait for 42ms before next frame
        if(cv2.waitKey(42) and 0xFF == ord("q")):
           break

        count += 1

    print('Finished with display!')
    #make sure we cleanup the windows!
    cv2.destroyAllWindows()

def extractFrames(clipFileName, colorFrames):
    # initialize frame count
    count = 0
    # open the video clip
    vidcap = cv2.VideoCapture(clipFileName)
    # create the output directory if it doesn't exist
    if not os.path.exists(outputDir):
        print(f"Output directory {outputDir} didn't exist, creating")
        os.makedirs(outputDir)
    
    # read one frame
    success,image = vidcap.read()
    print(f'Reading frame {count} {success}')
    while success:
        colorFrames.enqueue(image)
        # write the current frame out as a jpeg image
        cv2.imwrite(f"{outputDir}/frame_{count:04d}.bmp", image)   
        success,image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1
        
class queueThread:
    def __init__(self):
        self.queue=[]
        self.full=threading.Semaphore(0)
        self.empty = threading.Semaphore(24)
        self.empty = threading.Semaphore(15)
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
convertT = threading.Thread(target = convertToGray, args = (grayFrames, colorFrames))
displayT = threading.Thread(target = displayFrames, args = (grayFrames,))
extraceT.start()
convertT.start()
displayT.start()