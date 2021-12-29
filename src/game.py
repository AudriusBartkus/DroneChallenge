from os import altsep
import pygame
from PIL import Image
import time
from ConfigObject import ConfigObject
from recordtype import recordtype
from wireless import Wireless

from helpers.displayHelper import DisplayHelper
from helpers.controlsHelper import ControlsHelper
from helpers.colorHelper import ColorHelper
from helpers.drawHelper import DrawHelper


from drone import Drone
from droneModes import DroneModes
from camera import Camera
from interfaces.videoInputInterface import VideoInputInterface
from menu.menu import *
from menu.colorCalibrationMenu import ColorCalibrationMenu
# from customVisionDetectionTensorflow import CustomVisionDetectionTensorflow
# from gestureRecognition import GestureRecognition
# from characterDetection import CharacterDetection
from arUcoRecognition import ArUcoRecognition


class Game(DisplayHelper, ControlsHelper, ColorHelper, DrawHelper):
    def __init__(self):
        pygame.init()
        self.config = ConfigObject(filename='settings.config')
        

        # self.config.read('settings.config')
        self.os = self.config.game.os
        self.debug = self.config.game.debug.as_bool()
        self.initModesOnStart = self.config.game.initModesOnStart.as_bool()
        self.useTensorflow = self.config.game.useTensorFlow.as_bool()

        if self.useTensorflow:
            from customVisionDetectionTensorflow import CustomVisionDetectionTensorflow
            from gestureRecognition import GestureRecognition
            from characterDetection import CharacterDetection

        self.clock = pygame.time.Clock()
        self.fps = 10
        self.inputMode = self.config.game.inputMode
        self.running, self.playing = True, False
        self.UP_KEY, self.DOWN_KEY, self.LEFT_KEY, self.RIGHT_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False, False, False
        self.D_FW_KEY, self.D_BW_KEY, self.D_LEFT_KEY, self.D_RIGHT_KEY, self.D_UP_KEY, self.D_DOWN_KEY, self.D_ROTATEC_KEY, self.D_ROTATECC_KEY = False, False, False, False, False, False, False, False
        self.D_TAKEOFF_KEY, self.D_LAND_KEY, self.D_BACK_TO_START = False, False, False
        self.D_NONE_KEY, self.D_FREE_FLY_KEY, self.D_TRACK_OBJ_KEY, self.D_FIND_COLORS_KEY, self.D_TRACK_FACE_KEY, self.D_FIND_NUMBER_KEY = False, False, False, False, False, False
        self.D_GESTURE_KEY, self.D_ARUCO_KEY = False, False
        self.DISPLAY_W, self.DISPLAY_H = 1024, 768
        self.display = pygame.Surface((self.DISPLAY_W, self.DISPLAY_H))
        self.window = pygame.display.set_mode((self.DISPLAY_W, self.DISPLAY_H))
        self.fontName = 'resources/fonts/smb2.ttf'
        # self.fontName = 'resources\\fonts\\8-BIT WONDER.TTF'
        self.BLACK, self.WHITE, self.YELLOW, self.GREEN = (0,0,0), (255,255,255), (240, 175, 10), (38, 115, 38)

        #Wifi
        self.networkName = self.config.drone.networkName
        self.networkPwd = self.config.drone.networkPwd

        #Drone
        self.droneSpeed = self.config.drone.speed.as_int()
        self.drone = Drone()
        self.droneMode = DroneModes.NONE
        self.DM = recordtype("DM", ["id", "name", "posX", "posY"])
        self.droneModes = [
            self.DM(DroneModes.NONE.value, "None", self.DISPLAY_W - 90, 90),
            self.DM(DroneModes.FREE_FLY.value, "Free Fly", self.DISPLAY_W - 90, 120),
            self.DM(DroneModes.OBJECT_TRACKING.value, "Object Tracking",  self.DISPLAY_W - 90, 150),
            self.DM(DroneModes.FIND_COLORS.value, "Find Colors",  self.DISPLAY_W - 90, 200),
            self.DM(DroneModes.FACE_TRACKING.value, "Face Tracking",  self.DISPLAY_W - 90, 250),
            self.DM(DroneModes.GESTURE_RECOGNITION.value, "Gesture Recognition",  self.DISPLAY_W - 90, 300),
            self.DM(DroneModes.FIND_NUMBER.value, "Find Number",  self.DISPLAY_W - 90, 350),
            self.DM(DroneModes.ARUCO_RECOGNITION.value, "ArUco Markers",  self.DISPLAY_W - 90, 400)

        ]

        #Menu
        self.mainMenu = MainMenu(self)
        self.optionsMenu = OptionsMenu(self)
        self.colorCalibrationMenu = ColorCalibrationMenu(self, self.config.objectTracking)
        self.currMenu = self.mainMenu

        #VideoInput
        self.videoInput = VideoInputInterface
        self.videoInputSize = (640, 480) 
        if self.debug:
            self.videoInput = Camera(self.videoInputSize)
        else:
            self.videoInputSize = (640, 480)  #original frame size: 960x720
            self.videoInput = self.drone #todo: size
            pass

        #Object Tracking
        self.trackingColorRgb = self.getTackingColorRgb()
        self.trackingColorHsvRange = self.getTackingColorHsvRange()
        self.minTrackingArea = self.config.objectTracking.minTrackingArea.as_int()
        self.threshold1 = self.config.objectTracking.threshold1.as_int()
        self.threshold2 = self.config.objectTracking.threshold2.as_int()
        self.objectTrackingCenterZone = int(self.config.objectTracking.centerZone)

        #Find Colors
        self.FC = recordtype("FC", ["id", "name", "rgb", "hsvRange", "state", "posX", "posY"])
        self.findColorsList = None
        self.findColorStart = None
        self.findCOlorEnd = None

        #Face Tracking
        self.faceTracking = None
        self.faceTrackingModel = self.config.faceTracking.model
        self.faceTrackingLabels = self.config.faceTracking.labels
        self.faceTrackingMinScore = self.config.faceTracking.minScore.as_float()
        self.faceTrackingMaxSize = self.config.faceTracking.maxSize.as_int()

        #Gesture Recognition
        self.gestureRecognition = None
        self.gestureRecognitionModelDir = self.config.gestureRecognition.modelDir
        self.gestureRecognitionMinScore = self.config.gestureRecognition.minScore
        self.gestureRecognitionValue = ""
        self.gestureRecognitionTimeout = 10
        self.gestureRecognitionTimeoutIndex = 0
        self.gestureRecognitionValueCount = 0

        #Find Number
        self.characterDetection = None
        self.characterDetectionTimeout = 5
        self.characterDetectionTimeoutIndex = 0
        self.numberToFind = None
        self.numberFound = False

        #ArUco Recognition
        self.arUcoRecognition = None
        self.arUcoDictName = "DICT_7X7_1000"
        self.arUcoCurrMarkerId = None
        self.arUcoTotalMarkers = 6
        self.arUcoCenterZone = 50

        if self.initModesOnStart:
            self.initLongLoadingModules()

        # if self.debug == False and self.os == 'picade':
        #     self.connectToWifi(self.networkName, self.networkPwd)

    def gameLoop(self):
        while self.playing:
            self.clock.tick(self.fps)
            self.frame = self.videoInput.getFrame()

            self.display.fill(self.BLACK)

            #controls
            self.checkEvents(self.inputMode)
            if self.BACK_KEY:
                if self.droneMode == DroneModes.NONE:
                    self.playing = False
                    self.currMenu = self.mainMenu
                elif self.drone.isFlying:
                    self.drone.land()
                self.droneMode = DroneModes.NONE
                #TODO: disconnect from drone
                

            if self.D_TAKEOFF_KEY:
                self.drone.takeoff()
                self.droneMode = DroneModes.FREE_FLY

            if self.D_LAND_KEY:
                self.drone.land()
                self.droneMode = DroneModes.NONE

            if self.D_BACK_TO_START and self.drone.isFlying:
                if self.drone.isFlyingToStart:
                    self.drone.isFlyingToStart = False
                else:
                    self.drone.isFlyingToStart = True

            self.checkDroneMode()

            if self.drone.isFlying and self.droneMode == DroneModes.FREE_FLY: 
                moved = False
                #if no key pressed
                if self.D_FW_KEY == self.D_BW_KEY == self.D_LEFT_KEY == self.D_RIGHT_KEY == self.D_UP_KEY == self.D_DOWN_KEY == self.D_ROTATEC_KEY == self.D_ROTATECC_KEY == False:
                    #and flying to start
                    if self.drone.isFlyingToStart:
                        #move drone
                        returned = self.drone.moveTowardsStartingPoint()
                        moved = True
                        if returned: self.drone.isFlyingToStart = False
                #otherwise send key inputs
                if moved == False:
                    self.drone.sendControls(self.D_FW_KEY, self.D_BW_KEY, self.D_LEFT_KEY, self.D_RIGHT_KEY, self.D_UP_KEY, self.D_DOWN_KEY, self.D_ROTATEC_KEY, self.D_ROTATECC_KEY)

            elif self.droneMode == DroneModes.OBJECT_TRACKING:
                self.trackObject()
            elif self.droneMode == DroneModes.FIND_COLORS:
                self.findColors()
            elif self.droneMode == DroneModes.FACE_TRACKING:
                self.trackFace()
            elif self.droneMode == DroneModes.GESTURE_RECOGNITION:
                self.recognizeGesture()
            elif self.droneMode == DroneModes.FIND_NUMBER:
                self.findNumber()
            elif self.droneMode == DroneModes.ARUCO_RECOGNITION:
                self.findArucoMarkers()

            #screen
            self.drawVideoFrame(self.frame)
            self.drawDroneModes()
            
            if self.debug:
                self.drawDebug()
            else:
                battery = self.drone.getBattery()
                self.drawBattery(battery)

            self.window.blit(self.display, (0, 0))
            pygame.display.update()
            self.resetKeys()

    def startGame(self):
        if self.debug == False:
            self.connectToDrone()
        if self.debug or self.drone.connected:
            self.playing = True
            self.currMenu = None
        else:
           self.runDisplay = True 

    def endGame(self):
        self.running, self.playing = False, False
        if self.currMenu:
            self.currMenu.runDisplay = False
        if self.debug == False:
            if self.drone.isFlying:
                self.drone.land()
            self.drone.end()

    def applyDebugModeChange(self, debugValue):
        self.debug = debugValue
        self.config.game.debug = debugValue
        self.config.write()
        self.configureVideoInput()

    def configureVideoInput(self):
        if self.debug:
            self.videoInput = Camera(self.videoInputSize)
        else:
            self.videoInput = self.drone

    def resetKeys(self):
        self.UP_KEY, self.DOWN_KEY, self.LEFT_KEY, self.RIGHT_KEY, self.START_KEY, self.BACK_KEY = False, False, False, False, False, False
        self.D_FW_KEY, self.D_BW_KEY, self.D_LEFT_KEY, self.D_RIGHT_KEY, self.D_UP_KEY, self.D_DOWN_KEY, self.D_ROTATEC_KEY, self.D_ROTATECC_KEY = False, False, False, False, False, False, False, False
        self.D_TAKEOFF_KEY, self.D_LAND_KEY, self.D_BACK_TO_START = False, False, False
        self.D_NONE_KEY, self.D_FREE_FLY_KEY, self.D_TRACK_OBJ_KEY, self.D_FIND_COLORS_KEY, self.D_TRACK_FACE_KEY, self.D_FIND_NUMBER_KEY = False, False, False, False, False, False
        self.D_GESTURE_KEY, self.D_ARUCO_KEY = False, False


    def connectToDrone(self):
        self.drone.connectToDrone(self.videoInputSize, self.droneSpeed)

    def connectToWifi(self, networkName, networkPwd):
        wire = Wireless()
        wire.connect(ssid=networkName,password=networkPwd)

    def checkDroneMode(self):
        if self.D_NONE_KEY:
            if self.drone.isFlying:
                self.drone.land()
            self.droneMode = DroneModes.NONE

        elif self.D_FREE_FLY_KEY:
            if self.debug == False:
                if self.drone.isFlying == False:
                    self.drone.takeoff()
                self.droneMode = DroneModes.FREE_FLY

        elif self.D_TRACK_OBJ_KEY:
            if self.droneMode == DroneModes.FREE_FLY:
                self.initTrackObject()
                self.droneMode = DroneModes.OBJECT_TRACKING
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.initTrackObject()
                self.droneMode = DroneModes.OBJECT_TRACKING
            elif self.droneMode == DroneModes.OBJECT_TRACKING:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

        elif self.D_FIND_COLORS_KEY:
            if self.droneMode == DroneModes.FREE_FLY:
                self.droneMode = DroneModes.FIND_COLORS
                self.initFindColors()
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.droneMode = DroneModes.FIND_COLORS
                self.initFindColors()
            elif self.droneMode == DroneModes.FIND_COLORS:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

        elif self.D_TRACK_FACE_KEY:
            if self.useTensorflow == False:
                return
            if self.droneMode == DroneModes.FREE_FLY:
                self.droneMode = DroneModes.FACE_TRACKING
                self.initTrackFace()
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.droneMode = DroneModes.FACE_TRACKING
                self.initTrackFace()
            elif self.droneMode == DroneModes.FACE_TRACKING:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

        elif self.D_GESTURE_KEY:
            if self.useTensorflow == False:
                return
            if self.droneMode == DroneModes.FREE_FLY:
                self.droneMode = DroneModes.GESTURE_RECOGNITION
                self.initRecognizeGesture()
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.droneMode = DroneModes.GESTURE_RECOGNITION
                self.initRecognizeGesture()
            elif self.droneMode == DroneModes.GESTURE_RECOGNITION:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

        elif self.D_FIND_NUMBER_KEY:
            if self.droneMode == DroneModes.FREE_FLY:
                self.droneMode = DroneModes.FIND_NUMBER
                self.initFindNumber()
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.droneMode = DroneModes.FIND_NUMBER
                self.initFindNumber()
            elif self.droneMode == DroneModes.FIND_NUMBER:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

        elif self.D_ARUCO_KEY:
            if self.droneMode == DroneModes.FREE_FLY:
                self.droneMode = DroneModes.ARUCO_RECOGNITION
                self.initFindArucoMarkers()
            elif self.droneMode == DroneModes.NONE and self.debug:
                self.droneMode = DroneModes.ARUCO_RECOGNITION
                self.initFindArucoMarkers()
            elif self.droneMode == DroneModes.ARUCO_RECOGNITION:
                if self.debug:
                    self.droneMode = DroneModes.NONE
                else: 
                    self.droneMode = DroneModes.FREE_FLY

    def trackHsvColorRange(self, trackingColorHsvRange):
        contours, _, _ = self.getContours(self.frame, trackingColorHsvRange, self.minTrackingArea, self.threshold1, self.threshold2)
        self.addGrid(self.frame, self.objectTrackingCenterZone, self.YELLOW)
        contourFound, colorFound = False, False
        mainContour = []
        for cnt in contours:
            contourFound = True
            if mainContour == [] or cnt[1] > mainContour[1]:
                mainContour = cnt

        if mainContour!=[]:
            # colorFound = cv2.pointPolygonTest(mainContour[0], (self.videoInput.centerPos[0],self.videoInput.centerPos[1]), False)

            self.addContours(self.frame, [mainContour])
            objectCenterPos, _, _, _, _ = self.getContourCenter(mainContour[0])

            colorFound = self.isInCenterZone(objectCenterPos, self.drone.centerPos, self.objectTrackingCenterZone)
            
            # if colorFound > 0: colorFound = True
            # else: colorFound = False

            fb = 0
            # if mainContour[1] < self.minTrackingArea * 2:
            #     fb = 1

            if self.drone.isFlying:
                if colorFound:
                    self.drone.standStill()
                else:
                    self.drone.moveTowardsPoint(objectCenterPos, self.objectTrackingCenterZone, fb)


        return contourFound, colorFound

    #Track Object
    def initTrackObject(self):
        self.trackingColorRgb = self.getTackingColorRgb()
        self.trackingColorHsvRange = self.getTackingColorHsvRange()

    def trackObject(self):
        self.trackHsvColorRange(self.trackingColorHsvRange)
        self.drawText("Color", 20, self.WHITE, 100, self.DISPLAY_H/2 + 210)

        pygame.draw.rect(self.display, self.trackingColorRgb, ( 191, self.DISPLAY_H/2 +175, 75, 75), 0)
        pygame.draw.rect(self.display, self.WHITE, ( 191, self.DISPLAY_H/2 +175, 75, 75), 5)


    #Find Colors
    def initFindColors(self):
        self.drone.resetStartingPoint()
        self.findColorsList = [
            self.FC(0, "", (118, 80, 112), self.getHsvRangeForRgb((118, 80, 112), 40), "Active", 191, self.DISPLAY_H/2 +175),
            self.FC(1, "", (147, 121, 10), self.getHsvRangeForRgb((147, 121, 10), 40), "None", 291, self.DISPLAY_H/2 +175),
            # self.FC(2, "", (158, 5, 78), self.getHsvRangeForRgb((158, 5, 78), 40), "None", 391, self.DISPLAY_H/2 +175)
        ]
        self.findColorStart = time.perf_counter()
        self.findCOlorEnd = time.perf_counter()

    def findColors(self):
        self.drawText("Colors", 20, self.WHITE, 100, self.DISPLAY_H/2 + 210)
        allColorsFound = False
        searchActive = False
        if self.drone.isFlying and self.drone.isFlyingToStart:
            self.drone.moveTowardsStartingPoint()
        else: searchActive = True

        for color in self.findColorsList:
            borderColor = self.WHITE
            pygame.draw.rect(self.display, color.rgb, (color.posX, color.posY, 75, 75), 0)
            if color.state == "Found":
                borderColor = self.GREEN
                if color.id + 1 == len(self.findColorsList):
                    allColorsFound = True
            elif color.state == "Active":
                borderColor = self.YELLOW
                if searchActive:
                    contourFound, colorFound = self.trackHsvColorRange(color.hsvRange)
                    if contourFound == False:
                        if self.drone.isFlying:
                            self.drone.sendControls(False, False, False, False, False, False, True, False) #rotate clockwise
                    elif colorFound:
                        color.state = "Found"
                        if self.drone.isFlying:
                            self.drone.isFlyingToStart = True
                            searchActive = False
                        if color.id + 1 < len(self.findColorsList):
                            self.findColorsList[color.id + 1].state = "Active"
                        else:
                            allColorsFound = True
            elif color.state == "None":
                pass
            pygame.draw.rect(self.display, borderColor, (color.posX, color.posY, 75, 75), 5)

        if allColorsFound:
            if self.drone.isFlying and self.drone.isFlyingToStart == False:
                self.drone.standStill()
            self.drawText("All Colors Found", 20, self.WHITE, self.DISPLAY_W/2, self.DISPLAY_H/2 + 300)
        else:
            self.findColorEnd = time.perf_counter()
            if self.drone.isFlyingToStart:
                self.drawText("Moving to Start Position", 20, self.WHITE, self.DISPLAY_W/2, self.DISPLAY_H/2 + 300)
        findColorElapsed = f"{self.findColorEnd - self.findColorStart:0.2f}"
        self.drawText(findColorElapsed, 20, self.WHITE, 100, self.DISPLAY_H/2 + 300)

    #Track Face
    def initTrackFace(self):
        if self.faceTracking == None:
            self.drawLoading()
            self.faceTracking = CustomVisionDetectionTensorflow(self.faceTrackingModel, self.faceTrackingLabels)


    def trackFace(self):
        imgFT = Image.fromarray(self.frame)
        self.addGrid(self.frame, self.objectTrackingCenterZone, self.YELLOW)
        predictions = self.faceTracking.predict_image(imgFT)

        mainPrediction = []
        for pr in predictions:
            # print("{}: {}".format(pr['tagName'], pr['probability']))
            if pr['tagName'] == 'face':
                if mainPrediction == [] or pr['probability'] > mainPrediction['probability']:
                    # print(pr['probability'])
                    mainPrediction = pr

        if mainPrediction!=[]:
            objectSize = self.faceTracking.get_prediction_size(self.frame, mainPrediction)
            if objectSize < self.faceTrackingMaxSize:
                self.frame = self.faceTracking.show_predictions(self.frame, [mainPrediction], self.faceTrackingMinScore)
                objectCenterPos = self.faceTracking.get_prediction_center(self.frame, mainPrediction)

                if self.drone.isFlying:
                    self.drone.moveTowardsPoint(objectCenterPos, self.objectTrackingCenterZone)
        else:
            if self.drone.isFlying:
                self.drone.standStill()


    #Gesture Recognition
    def initRecognizeGesture(self):
        if self.gestureRecognition == None:
            self.drawLoading()
            self.gestureRecognition = GestureRecognition(self.gestureRecognitionModelDir)
            self.gestureRecognition.load()

    def recognizeGesture(self):
        self.clock.tick(self.fps)
        self.drawText("Prediction", 16, self.WHITE, 100, self.DISPLAY_H/2 + 209)
        if self.gestureRecognitionValue == "None":
            self.gestureRecognitionTimeoutIndex = (self.gestureRecognitionTimeoutIndex + 1) % self.gestureRecognitionTimeout
            if self.gestureRecognitionTimeoutIndex != 0:
                self.drawText(self.gestureRecognitionValue, 20, self.WHITE, 300, self.DISPLAY_H/2 + 210)
                return
        img = Image.fromarray(self.frame)
        prediction = self.gestureRecognition.predict(img)
        if prediction['Prediction'] == self.gestureRecognitionValue:
            self.gestureRecognitionValueCount += 1
        else:
            self.gestureRecognitionValueCount = 0
            self.gestureRecognitionValue = prediction['Prediction']
        predictionIndex = self.gestureRecognition.labels.index(prediction["Prediction"])
        if self.gestureRecognitionValue == "None":
            self.drawText(self.gestureRecognitionValue, 20, self.WHITE, 300, self.DISPLAY_H/2 + 210)
        else:
            complete = self.drawProgressBar(self.gestureRecognitionValueCount, 5, self.YELLOW, 400, self.DISPLAY_H/2 + 200, 50)
            valueColor = self.WHITE
            if complete: 
                self.gestureRecognized = True
                valueColor = self.YELLOW
                if self.gestureRecognitionValue.isnumeric():
                    self.numberToFind = int(self.gestureRecognitionValue)
            else: 
                self.gestureRecognized = False
            predictionText = "{0} : {1:.0%}".format(prediction['Prediction'], prediction["Confidences"][predictionIndex])
            self.drawText(predictionText, 20, valueColor, 300, self.DISPLAY_H/2 + 210)

    #Find Number
    def initFindNumber(self):
        if self.characterDetection == None:
            if self.gestureRecognition == None:
                self.initRecognizeGesture()
            self.characterDetection = CharacterDetection()
        self.numberToFind = None
        self.numberFound = False

    def findNumber(self):
        contourFound = False
        if self.numberFound:
            self.drawText("Found number: {}. Flying back to start".format(self.numberToFind), 20, self.YELLOW, self.DISPLAY_W/2, self.DISPLAY_H/2 + 210)
            if self.debug:
                self.numberToFind = None
                self.numberFound = False
                return
            else:
                if self.drone.isFlying and self.drone.isFlyingToStart:
                    self.drone.moveTowardsStartingPoint()
                else:
                    self.numberToFind = None
                    self.numberFound = False
                return

        if self.numberToFind == None:
            self.recognizeGesture()
        elif self.numberFound == False:
            self.drawText("Searching for number: {}".format(self.numberToFind), 20, self.WHITE, self.DISPLAY_W/2, self.DISPLAY_H/2 + 210)
           
            self.frame, contourFound, self.numberFound = self.characterDetection.findNumber(self.frame, self.numberToFind)
            #Delay rotation if contour found
            if contourFound:
                self.characterDetectionTimeoutIndex = (self.characterDetectionTimeoutIndex + 1) % self.characterDetectionTimeout
                if self.characterDetectionTimeoutIndex == 0:
                    if self.debug == False and self.drone.isFlying:
                        self.drone.sendControls(False, False, False, False, False, False, True, False) #rotate clockwise
            else:
                self.characterDetectionTimeoutIndex = 0
                self.drone.sendControls(False, False, False, False, False, False, True, False) #rotate clockwise

            if self.numberFound:
                if self.debug == False:
                    if self.drone.isFlying:
                        self.drone.isFlyingToStart = True

    #ArUco recognition
    def initFindArucoMarkers(self):
        if self.arUcoRecognition == None:
            self.arUcoRecognition = ArUcoRecognition(self.arUcoDictName, self.GREEN, self.YELLOW)
        self.arUcoCurrMarkerId = 1

    def findArucoMarkers(self):
        markerFound, centerPos = self.arUcoRecognition.findMarker(self.frame, self.arUcoCurrMarkerId)
        self.addGrid(self.frame, self.arUcoCenterZone, self.YELLOW)
        self.drawText("Moving towards marker: {}".format(self.arUcoCurrMarkerId), 20, self.WHITE, self.DISPLAY_W/2, self.DISPLAY_H/2 + 210)
        
        if markerFound:
            if self.debug == False and self.drone.isFlying:
                self.drone.moveTowardsPoint(centerPos, self.arUcoCenterZone, rotate = False)

            isCentered = self.isInCenterZone(centerPos, self.drone.centerPos, self.arUcoCenterZone)
            if isCentered:
                self.arUcoCurrMarkerId = (self.arUcoCurrMarkerId % self.arUcoTotalMarkers) + 1
            

    def initLongLoadingModules(self):
        if self.useTensorflow == False:
            return
        self.initTrackFace()
        self.initRecognizeGesture()
        self.initFindNumber()

    #Settings
    def getTackingColorRgb(self):
        col = self.config.objectTracking.trackingColorRgb.as_list()
        return (int(col[0]), int(col[1]), int(col[2]))

    def getTackingColorHsvRange(self):
        t = self.config.objectTracking.trackingColorH.as_list()
        h  = (int(t[0]), int(t[1]))
        t = self.config.objectTracking.trackingColorS.as_list()
        s  = (int(t[0]), int(t[1]))
        t = self.config.objectTracking.trackingColorV.as_list()
        v  = (int(t[0]), int(t[1]))
        return [h, s, v]



