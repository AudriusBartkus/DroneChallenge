import cv2
import numpy as np

class ColorHelper:

    def getColorBoundary(self, value, tolerance, boundary, upperOrLower):
        #upperOrLower: 1 = upper,0 = lower
        if upperOrLower == 1: #upper
            if value + tolerance > boundary:
                value = boundary
            else:
                value = value + tolerance
        elif upperOrLower == 0: #lower
            if value - tolerance < 0:
                value = 0
            else:
                value = value - tolerance

        return value

    def getHsvRangeForRgb(self, rgb, tolerance):
        rgbImg = np.uint8([[rgb]])  
        hsvImg = cv2.cvtColor(rgbImg, cv2.COLOR_RGB2HSV) 
        hsvColor = hsvImg[0][0]

        newMinH = self.getColorBoundary(hsvColor[0], tolerance, 179, 0)
        newMaxH = self.getColorBoundary(hsvColor[0], tolerance, 179, 1)
        newMinS = self.getColorBoundary(hsvColor[1], tolerance, 255, 0)
        newMaxS = self.getColorBoundary(hsvColor[1], tolerance, 255, 1)
        newMinV = self.getColorBoundary(hsvColor[2], tolerance, 255, 0)
        newMaxV = self.getColorBoundary(hsvColor[2], tolerance, 255, 1)
        return [(newMinH, newMaxH),(newMinS,newMaxS),(newMinV, newMaxV)]

    def getContours(self, img, hsvRange, minArea, threshold1, threshold2):
        imgHsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

        lower = np.array([hsvRange[0][0],hsvRange[1][0],hsvRange[2][0]])
        upper = np.array([hsvRange[0][1],hsvRange[1][1],hsvRange[2][1]])
        mask = cv2.inRange(imgHsv,lower,upper)
        maskResult = cv2.bitwise_and(img,img, mask = mask)
        mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)

        imgBlur = cv2.GaussianBlur(maskResult, (7, 7), 1)
        imgGray = cv2.cvtColor(imgBlur, cv2.COLOR_BGR2GRAY)
        imgCanny = cv2.Canny(imgGray, threshold1, threshold2)
        kernel = np.ones((5, 5))
        imgDil = cv2.dilate(imgCanny, kernel, iterations=1)


        contours, hierarchy = cv2.findContours(imgDil, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        validContours = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > minArea:
                validContours.append([cnt, area])
        return validContours, imgHsv, maskResult

    def getContourCenter(self, contour):
        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        x , y , w, h = cv2.boundingRect(approx)
        cx = int(x + (w / 2))  # CENTER X OF THE OBJECT
        cy = int(y + (h / 2))  # CENTER X OF THE OBJECT

        return (cx, cy), x, y, w, h
        
    def addContours(self, img, contours):
        for cnt in contours:
            cv2.drawContours(img, cnt[0], -1, (255, 0, 255), 2)
            center, x, y, w, h = self.getContourCenter(cnt[0])
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(img,center,2,(0,0,255),3)