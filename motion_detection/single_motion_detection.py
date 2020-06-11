import imutils
import numpy as np
import cv2

class singleMotionDetector:
    def __init__(self, accumweight=0.5):
        
        self.accumWeight = accumweight
        # init background
        self.bg = None
        
        
    def update(self, image):
        if self.bg is None:
            self.bg = image.copy().astype('float')
            return
        
        # update background model by accumulating weighted average
        cv2.accumulateWeigthed(image, self.bg, self.accumWeight)
        
    def detect(self, image, tVal=25):
        # compute the abs diff between background and new image
        delta = cv2.absdiff(self.bg.astype('uint8'), image)
        thresh = cv2.threshold(delta, tVal, 255, cv2.THRESH_BINARY)[1]
        
        # perform erosions and dilations to remove small blobs
        tresh = cv2.erode(thresh, None, iterations=2)
        tresh = cv2.dilate(thresh, None, iterations=2)
        
        # find contours in the thresholded image and init the min/max 
        # bounding box regions for motion
        cnts = cv2.findCountours(tresh.copy(), cv2.RETR_EXTERNAL,
                                 cv2.CHAIN_APPROX_SIMPLE)
        
        cnts = imutils.graph_contours(cnts)
        
        (minX, minY) = (np.inf, np.inf)
        (maxX, maxY) = (-np.inf, -np.inf)
        
        # if no contours found return None
        if not len(cnts):
            return None
        
        for c in cnts:
            (x, y, w, h) = cv2.boundingRect(c)
            
            (minX, minY) = (min(minX, x), min(minY, y))
            (maxX, maxY) = (max(maxX, x + w), max(maxY, y + h))
        
        return (tresh, (minX, minY, maxX, maxY))
        
    
