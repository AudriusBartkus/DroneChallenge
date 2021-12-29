import cv2
from djitellopy import Tello
from collections import deque

from interfaces.videoInputInterface import VideoInputInterface

class Drone(VideoInputInterface, Tello):

    def __init__(self) :
        Tello.__init__(self)

        #Display
        self.frameSize = (640, 480) #(720, 480)
        self.centerPos = [int(self.frameSize[0]/2), int(self.frameSize[1]/2)]
        self.centerZone = int(self.frameSize[1]/6)

        self.isFlying = False
        self.isFlyingToStart = False
        self.speed = 30
        self.battery = 100
        self.controlCommands = deque()
        self.standStillIndex = 0
        self.connected = False


    def empty(self):
        pass

    def connectToDrone(self, videoInputSize, speed):
        self.speed = speed
        self.frameSize = videoInputSize
        self.centerPos = [self.frameSize[0]/2, self.frameSize[1]/2]
        self.centerZone = int(self.frameSize[1]/6)
        self.connect()
        #video
        # if self.connected:
        # self.battery = self.get_battery()
        # print(self.battery)
        self.streamoff()
        self.streamon()
        self.droneFrameRead = self.get_frame_read()
        self.frame = self.droneFrameRead.frame
        self.connected = self.droneFrameRead.grabbed

    def takeoff(self):
        if self.isFlying: return False

        self.isFlying = True
        self.resetStartingPoint()
        return super().takeoff()

    def land(self):
        if self.isFlying == False: return False
        
        self.isFlying = False
        self.resetStartingPoint()
        return super().land()

    def getFrame(self):
        self.frame = self.droneFrameRead.frame 
        #original frame size: 960x720
        #TODO: try catch if drone disconnected
        self.frame = cv2.resize(self.frame, self.frameSize)
        return self.frame

    def getBattery(self):
        battery = self.get_battery()
        battery, parsed = self.intTryParse(battery)
        if parsed == False: battery = 0
        if battery != 0 and battery < self.battery:
            self.battery = battery
        
        return self.battery

    def sendControls(self, fw, bw, left, right, up, down, rotC, rotCC):
        if self.isFlying == False: return

        lr, fb, ud, yv = 0, 0, 0, 0

        if left:
            lr = - self.speed
        elif right:
            lr = self.speed

        if fw:
            fb = self.speed
        elif bw:
            fb = - self.speed

        if up:
            ud = self.speed
        elif down:
            ud = - self.speed

        if rotCC:
            yv = - self.speed
        elif rotC:
            yv = self.speed

        if self.isFlyingToStart == False:
            if (lr == 0 and fb == 0 and ud == 0 and yv == 0):
                self.standStill()
            else:
                self.standStillIndex = 0
                self.controlCommands.append([lr, fb, ud, yv])


        self.send_rc_control(lr, fb, ud, yv)

    def moveTowardsPoint(self, point, centerZone, fb = 0, rotate = True):
        if self.isFlying == False: return

        lr, fb, ud, yv = 0, fb * self.speed, 0, 0

        if (point[0] < self.centerPos[0] - centerZone):
            if rotate:
                yv = - self.speed 
            else:
                lr = - self.speed
        elif (point[0] > self.centerPos[0] + centerZone):
            if rotate:
                yv = self.speed 
            else:
                lr = self.speed
        if (point[1] < self.centerPos[1] - centerZone):
                ud = self.speed 
        elif (point[1] > self.centerPos[1] + centerZone):
                ud = - self.speed 
        if (point[0] > self.centerPos[0] - centerZone) and (point[0] < self.centerPos[0] + centerZone) and (point[1] > self.centerPos[1] - centerZone) and (point[1] < self.centerPos[1] + centerZone): #point is in centerZone
            contourFound = True
        else:
            self.standStillIndex = 0
            self.controlCommands.append([lr, fb, ud, yv])
            
        self.send_rc_control(lr, fb, ud, yv)
        #TODO: if contour size too big - move backwards?

    def moveTowardsStartingPoint(self):
        if self.isFlying == False: return

        if len(self.controlCommands) == 0:
            self.isFlyingToStart = False
            return True
        else:
            command = self.controlCommands.pop()
            oppositeCommand = [i * -1 for i in command]
            self.send_rc_control(oppositeCommand[0], oppositeCommand[1], oppositeCommand[2], oppositeCommand[3])
            return False

    def standStill(self):
        if self.isFlying == False: return

        #add max n standStill commands
        if self.standStillIndex < 5:
            self.standStillIndex += 1
        self.controlCommands.append([0, 0, 0, 0]) 

        self.send_rc_control(0, 0, 0, 0) 

    def resetStartingPoint(self):
        self.controlCommands.clear()

    def intTryParse(self, value):
        try:
            return int(value), True
        except ValueError:
            return value, False
