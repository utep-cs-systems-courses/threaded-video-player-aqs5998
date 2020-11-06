#!/usr/bin/env python3

import cv2
import threading
import numpy as np
import base64
import os
import queue

# globals
outputDir    = 'frames'
clipFileName = '../clip.mp4'



def convertToGray(colorFrames, grayFrames):
    outputDir    = 'frames'
    # initialize frame count
    count = 0
    # get the next frame file name
    inFileName = f'{outputDir}/frame_{count:04d}.bmp'
    # load the next file
    inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
    while True:
        print(f'Converting frame {count}') # convert the image to grayscale
        getFrame = colorFrames.dequeue()
        if getFrame == '!':
            break
        colorFrames.enqueue('!')
        grayscaleFrame = cv2.cvtColor(inputFrame, cv2.COLOR_BGR2GRAY)  # generate output file name
        outFileName = f'{outputDir}/grayscale_{count:04d}.bmp' # write output file
        cv2.imwrite(outFileName, grayscaleFrame)
        grayFrames.enqueue(grayscaleFrame)
        count += 1
        # generate input file name for the next frame
        inFileName = f'{outputDir}/frame_{count:04d}.bmp'
        # load the next frame
        inputFrame = cv2.imread(inFileName, cv2.IMREAD_COLOR)
    grayFrames.enqueue('!')

def displayFrames(grayFrames):
    # globals
    outputDir    = 'frames'
    frameDelay   = 42       # the answer to everything
    # initialize frame count
    count = 0
    # Generate the filename for the first frame 
    # load the frame
    while True:
        
        print(f'Displaying frame {count}')
        #get next frame
        frame = grayFrames.dequeue()
        if frame == '!':
            break
        # Display the frame in a window called "Video"
        cv2.imshow('Video', frame)
        # Wait for 42 ms and check if the user wants to quit
        if cv2.waitKey(frameDelay) and 0xFF == ord("q"):
            break    
        # get the next frame filename
        count += 1

        # Read the next frame file
    # make sure we cleanup the windows, otherwise we might end up with a mess
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
    colorFrames.enqueue('!')


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
convertT = threading.Thread(target = extractFrames, args = (clipFileName, colorFrames))
displayT = threading.Thread(target = displayFrames, args = (grayFrames,))

extraceT.start()
convertT.start()
displayT.start()