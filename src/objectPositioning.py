import cv2
import numpy as np

myColor = [140,30,65,179,255,255]
myColorValue = [51,153,255]


def findColor(img,imgResult,myColor = myColor,myColorValue = myColorValue):
    imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    newPoint=[]

    lower = np.array(myColor[0:3])
    upper = np.array(myColor[3:6])
    mask = cv2.inRange(imgHSV,lower,upper)
    x,y=getContours(mask)
    # cv2.circle(imgResult,(x,y),15,myColorValue,cv2.FILLED)
    if x!=0 and y!=0:
        newPoint = [x,y]

    return newPoint

def getContours(img):
    contours,hierarchy = cv2.findContours(img,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE)
    x,y,w,h = 0,0,0,0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area>1000:
            #cv2.drawContours(imgResult, cnt, -1, (255, 0, 0), 3)
            peri = cv2.arcLength(cnt,True)
            approx = cv2.approxPolyDP(cnt,0.02*peri,True)
            x, y, w, h = cv2.boundingRect(approx)
    return x+w//2,y+h//2

def drawOnCanvas(imgResult,myPoints,myColorValue = myColorValue):
    for point in myPoints[-5:]:
        cv2.circle(imgResult, (point[0], point[1]), 10, myColorValue, cv2.FILLED)

def getOffsetFromLastPosition(myPoints):
    if len(myPoints)<2:
        return []
    currentPoint = myPoints[-1]
    previousPoint = myPoints[-2]

    offset = [abs(currentPoint[0]-previousPoint[0]), abs(currentPoint[1]-previousPoint[1])]
    return offset

def getOffsetFromCenter(center, newPoint):
    if newPoint == [] or center == []:
        return []
    offset = [center[0]-newPoint[0], center[1]-newPoint[1]]
    return offset 