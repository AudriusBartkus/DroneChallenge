import cv2
import imutils
import numpy as np
import pytesseract
from PIL import Image

class CharacterDetection(object):
    def __init__(self):
        pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
        self.minContourArea = 5000

    def findNumber(self, frame, numberToFind):
        contourFound = False
        numberFound = False
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray = cv2.bilateralFilter(gray, 13, 10, 10)
        edged = cv2.Canny(gray, 30, 200) #Perform Edge detection

        contours=cv2.findContours(edged.copy(),cv2.RETR_TREE,
                                                    cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        contours = sorted(contours,key=cv2.contourArea, reverse = True)[:10]
        screenCnt = None

        for c in contours:
            if cv2.contourArea(c) < self.minContourArea:
                break
            contourFound = True
            # approximate the contour
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.018 * peri, True)
            # if our approximated contour has four points, then
            # we can assume that we have found our screen
            if len(approx) == 4:
                screenCnt = approx
                contourColor = (0, 0, 255)

                mask = np.zeros(gray.shape,np.uint8)
                new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
                new_image = cv2.bitwise_and(frame,frame,mask=mask)

                (x, y) = np.where(mask == 255)
                (topx, topy) = (np.min(x), np.min(y))
                (bottomx, bottomy) = (np.max(x), np.max(y))
                Cropped = gray[topx:bottomx+1, topy:bottomy+1]

                text = pytesseract.image_to_string(Cropped,config='--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789')
                text = text.strip()
                if text.isnumeric():
                    if int(text) == numberToFind:
                        numberFound = True
                        contourColor = (38, 115, 38)

                cv2.drawContours(frame, [screenCnt], -1, contourColor, 3)

        return frame, contourFound, numberFound
