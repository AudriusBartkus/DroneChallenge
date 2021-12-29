import cv2
import numpy as np

class DisplayHelper:

    def stackImages(self, scale, imgArray):
        rows = len(imgArray)
        cols = len(imgArray[0])
        rowsAvailable = isinstance(imgArray[0], list)
        width = imgArray[0][0].shape[1]
        height = imgArray[0][0].shape[0]
        if rowsAvailable:
            for x in range ( 0, rows):
                for y in range(0, cols):
                    if imgArray[x][y].shape[:2] == imgArray[0][0].shape [:2]:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                    else:
                        imgArray[x][y] = cv2.resize(imgArray[x][y], (imgArray[0][0].shape[1], imgArray[0][0].shape[0]), None, scale, scale)
                    if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
            imageBlank = np.zeros((height, width, 3), np.uint8)
            hor = [imageBlank]*rows
            hor_con = [imageBlank]*rows
            for x in range(0, rows):
                hor[x] = np.hstack(imgArray[x])
            ver = np.vstack(hor)
        else:
            for x in range(0, rows):
                if imgArray[x].shape[:2] == imgArray[0].shape[:2]:
                    imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
                else:
                    imgArray[x] = cv2.resize(imgArray[x], (imgArray[0].shape[1], imgArray[0].shape[0]), None,scale, scale)
                if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
            hor= np.hstack(imgArray)
            ver = hor
        return ver

    def addGrid(self, img, deadZone, color):
        frameHeight, frameWidth, _ = img.shape
        bgrColor = color[::-1]
        cv2.line(img,(int(frameWidth/2)-deadZone,0),(int(frameWidth/2)-deadZone,frameHeight),bgrColor,1)
        cv2.line(img,(int(frameWidth/2)+deadZone,0),(int(frameWidth/2)+deadZone,frameHeight),bgrColor,1)
        cv2.circle(img,(int(frameWidth/2),int(frameHeight/2)),2,(0,0,255),3)
        cv2.line(img, (0,int(frameHeight / 2) - deadZone), (frameWidth,int(frameHeight / 2) - deadZone), bgrColor, 1)
        cv2.line(img, (0, int(frameHeight / 2) + deadZone), (frameWidth, int(frameHeight / 2) + deadZone), bgrColor, 1)

    def addDroneDetails(self, img, drone, debug):
        if debug == False:
            battery = drone.get_battery()
            cv2.putText(img, "Battery: {}".format(battery), (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (45,45,45), 1)
        else: 
            cv2.putText(img, "Debug: True", (10,20), cv2.FONT_HERSHEY_PLAIN, 1, (45,45,45), 1)

    def addFindColorDetails(self, img, colorNumber, color, elapsedTime):
        cv2.putText(img, "Looking for color {}: ".format(colorNumber), (10, 40), cv2.FONT_HERSHEY_PLAIN, 1, (45, 45, 45), 1)
        cv2.rectangle(img, (180, 27), (200, 42), color, cv2.FILLED)
        cv2.putText(img, "Elapsed time: {}".format(elapsedTime), (10, 60), cv2.FONT_HERSHEY_PLAIN, 1, (45, 45, 45), 1)

    def isInCenterZone(self, point, centerPos, centerZone):
        if (point[0] > centerPos[0] - centerZone) and (point[0] < centerPos[0] + centerZone) and (point[1] > centerPos[1] - centerZone) and (point[1] < centerPos[1] + centerZone):
           return True
        
        return False