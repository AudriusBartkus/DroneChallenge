import pygame
import cv2
import numpy as np

from menu.menu import Menu
from helpers.colorHelper import ColorHelper

# TODO: manual edit for HSV range, values for target area, thresholds
class ColorCalibrationMenu(Menu, ColorHelper):
    
    def __init__(self, game, colorCalibrationSettings):
        Menu.__init__(self, game)
        self.game = game
        self.ccSettings = colorCalibrationSettings
        self.options = [
            self.Option(0, "Select", self.game.DISPLAY_W/2, self.game.DISPLAY_H/2 + 100, "button", ""),
            
            self.Option(1, "hue_min", self.game.DISPLAY_W/2 - 150, self.game.DISPLAY_H/2  + 200, "input", self.ccSettings.trackingColorH.as_list()[0]), #TODO: imutable - how to update value?
            self.Option(2, "hue_max", self.game.DISPLAY_W/2 , self.game.DISPLAY_H/2 + 200, "input", self.ccSettings.trackingColorH.as_list()[1]),
            self.Option(3, "sat_min", self.game.DISPLAY_W/2 - 150, self.game.DISPLAY_H/2  + 250, "input", self.ccSettings.trackingColorS.as_list()[0]),
            self.Option(4, "sat_max", self.game.DISPLAY_W/2 , self.game.DISPLAY_H/2 + 250, "input", self.ccSettings.trackingColorS.as_list()[1]),
            self.Option(5, "val_min", self.game.DISPLAY_W/2 - 150, self.game.DISPLAY_H/2  + 300, "input", self.ccSettings.trackingColorV.as_list()[0]),
            self.Option(6, "val_max", self.game.DISPLAY_W/2 , self.game.DISPLAY_H/2 + 300, "input", self.ccSettings.trackingColorV.as_list()[1]),

            self.Option(7, "Save", self.game.DISPLAY_W - 75, self.game.DISPLAY_H - 50, "button", ""),
            self.Option(8, "Back", 75, self.game.DISPLAY_H - 50, "button", "")
        ]
        self.state = self.options[0]

        col = self.ccSettings.trackingColorRgb.as_list()
        self.currColor =  (int(col[0]), int(col[1]), int(col[2]))
        self.newColor =  [0, 0, 0]

        self.currColorHSV = self.game.getTackingColorHsvRange()

        self.minTrackingArea = self.ccSettings.minTrackingArea.as_int()
        self.threshold1 = self.ccSettings.threshold1.as_int()
        self.threshold2 = self.ccSettings.threshold2.as_int()



    def loadColorCalibrationMenu(self):
        if self.game.drone.connected == False:
            self.game.connectToDrone()

    def displayMenu(self):
        self.runDisplay = True
        while self.runDisplay:
            # self.checkEvents()
            self.game.checkEvents(self.game.inputMode)

            self.checkInput()
            self.game.display.fill(self.game.BLACK)

            videoInputFrame = self.game.videoInput.getFrame()
            frameCenter = (int(videoInputFrame.shape[1]/2), int(videoInputFrame.shape[0]/2))
            

            #colors:
            self.game.drawText('Current', self.headerSize, self.game.WHITE, 100 , 50)
            pygame.draw.rect(self.game.display, self.currColor, (30, 75, 130, 100), 0)
            self.game.drawText('New', self.headerSize, self.game.WHITE, 100 , 200)
            self.newColor = videoInputFrame[frameCenter[1], frameCenter[0]]
            
            newColorRGB = self.newColor[::-1]
            pygame.draw.rect(self.game.display, newColorRGB, (30, 220, 130, 100), 0)

            
            contours, _, _ = self.getContours(videoInputFrame, self.currColorHSV, self.minTrackingArea, self.threshold1, self.threshold2)
            self.addContours(videoInputFrame, contours)
            
            cv2.circle(videoInputFrame,frameCenter,7,self.currColor[::-1],2)
            self.game.drawVideoFrame(videoInputFrame)

            self.game.drawText('HUE', self.headerSize, self.game.WHITE, self.game.DISPLAY_W/2 -270 , self.game.DISPLAY_H /2 + 200)
            self.game.drawText('SAT', self.headerSize, self.game.WHITE, self.game.DISPLAY_W/2 -270 , self.game.DISPLAY_H /2 + 250)
            self.game.drawText('VAL', self.headerSize, self.game.WHITE, self.game.DISPLAY_W/2 -270 , self.game.DISPLAY_H /2 + 300)

            for option in self.options:
                color = self.game.WHITE
                size = self.optionSize
                if self.state.id == option.id:
                    color = self.game.YELLOW
                    size = self.activeSize
                if option.type == "button":
                    self.game.drawButton(option.id, option.posX, option.posY, 50, self.game.fontName, size, option.name, color)
                elif option.type == "text":
                    self.game.drawTextCenteredAt(option.name, size, color, option.posX, option.posY, self.menuW)
                elif option.type == "input":
                    size = self.optionSize
                    self.game.drawInputBox(option.id, option.posX, option.posY, 110, option.value, size, color)

            self.blitScreen()

    # def checkEvents(self):
    #     for event in pygame.event.get():
    #         pos = pygame.mouse.get_pos()

    #         if event.type == pygame.MOUSEBUTTONDOWN:
    #             if self.buttonBack.isOver(pos):
    #                 self.game.currMenu = self.game.optionsMenu
    #                 self.runDisplay = False
    
    def checkInput(self):
        if self.game.BACK_KEY:
            self.goBack()
        elif self.game.DOWN_KEY:
            if self.state.id < len(self.options) - 1:
                self.state = self.options[self.state.id + 1]
            else:
                self.state = self.options[0]

        elif self.game.UP_KEY:
            if self.state.id > 0:
                self.state = self.options[self.state.id - 1]
            else:
                self.state = self.options[len(self.options) - 1]
        
        elif self.game.START_KEY:
            if self.state.name == "Select":
                self.saveNewColorValue()
            elif self.state.name == "Save":
                self.saveSettings()
                self.goBack()
            elif self.state.name == "Back":
                self.goBack()


    def goBack(self):
        self.game.currMenu = self.game.optionsMenu
        self.runDisplay = False

    def loadColorHSV(self):
        col = self.ccSettings.trackingColorRgb.as_list()
        self.currColor =  (int(col[0]), int(col[1]), int(col[2]))
        self.currColorHSV = self.game.getTackingColorHsvRange()


    def saveNewColorValue(self):
  
        bgrImg = np.uint8([[self.newColor]])  
        hsvImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2HSV) 
        hsvColor = hsvImg[0][0]
        newMinH = self.getColorBoundary(hsvColor[0], 40, 179, 0)
        newMaxH = self.getColorBoundary(hsvColor[0], 40, 179, 1)
        newMinS = self.getColorBoundary(hsvColor[1], 40, 255, 0)
        newMaxS = self.getColorBoundary(hsvColor[1], 40, 255, 1)
        newMinV = self.getColorBoundary(hsvColor[2], 40, 255, 0)
        newMaxV = self.getColorBoundary(hsvColor[2], 40, 255, 1)
        newColorRGB = bgrImg[0][0][::-1]

        self.currColor = (int(newColorRGB[0]), int(newColorRGB[1]), int(newColorRGB[2]))
        self.currColorHSV = [(newMinH, newMaxH),(newMinS,newMaxS),(newMinV, newMaxV)]

        
        self.updateInputFields()

    def updateInputFields(self):
        for option in self.options:
            if option.type == "input":
                if option.name == "hue_min":
                    option.value = self.ccSettings.trackingColorH.as_list()[0]
                elif option.name == "hue_max":
                    option.value = self.ccSettings.trackingColorH.as_list()[1]
                elif option.name == "sat_min":
                    option.value = self.ccSettings.trackingColorS.as_list()[0]
                elif option.name == "sat_max":
                    option.value = self.ccSettings.trackingColorS.as_list()[1]
                elif option.name == "val_min":
                    option.value = self.ccSettings.trackingColorV.as_list()[0]
                elif option.name == "val_max":
                    option.value = self.ccSettings.trackingColorV.as_list()[1]

    def saveSettings(self):
        self.ccSettings.trackingColorRgb = f"{self.currColor[0]} {self.currColor[1]} {self.currColor[2]}"

        self.ccSettings.trackingColorH = f"{self.currColorHSV[0][0]} {self.currColorHSV[0][1]}"
        self.ccSettings.trackingColorS = f"{self.currColorHSV[1][0]} {self.currColorHSV[1][1]}"
        self.ccSettings.trackingColorV = f"{self.currColorHSV[2][0]} {self.currColorHSV[2][1]}"

        self.game.config.write()


