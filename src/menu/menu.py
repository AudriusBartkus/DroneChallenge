import pygame
import time
from recordtype import recordtype
from random import randint

from gui.button import Button
from gui.spritesheet import Spritesheet


class Menu():
    
    def __init__(self, game):
        self.game = game
        self.midW, self.midH = self.game.DISPLAY_W/2, self.game.DISPLAY_H/2
        self.runDisplay = True
        self.cursor = pygame.Rect(0, 0, 20, 20)
        self.offset = -100
        self.headerSize = 20
        self.optionSize = 15
        self.activeSize = 16
        self.Option = recordtype("Option", ["id", "name", "posX", "posY", "type", "value"])
        self.clock = pygame.time.Clock()
        self.fps = 10


    # def drawCursor(self):
    #     self.game.drawText('*', 15, self.game.WHITE, self.cursor.x, self.cursor.y) 

    def blitScreen(self):
        self.clock.tick(self.fps)
        self.game.window.blit(self.game.display, (0,0))
        pygame.display.update()
        self.game.resetKeys()

class MainMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)

        # self.state = "Start"
        # self.startX, self.startY = self.midW, self.midH + 30
        # self.optionsX, self.optionsY = self.midW, self.midH + 50
        # self.cursor.midtop = (self.startX + self.offset, self.startY)
        self.bg = pygame.image.load('resources/img/bg01.png').convert()
        self.droneSpritesheet = Spritesheet('resources/sprites/drone5.png')
        self.droneSpFrames = [self.droneSpritesheet.parse_sprite('drone0'), self.droneSpritesheet.parse_sprite('drone1'), self.droneSpritesheet.parse_sprite('drone2'), self.droneSpritesheet.parse_sprite('drone3')]
        self.droneFrameIndex = 0
        self.droneFrameDir = 0
        self.droneFrameH = 0
        self.droneFrameMinMaxH = 25
        self.droneFrameSpeed = 5

        self.options = [
            self.Option(0, "Start", self.midW, self.midH + 0, "text", ""),
            self.Option(1, "Options",  self.midW, self.midH + 50, "text", ""),
            self.Option(2, "Exit",  self.midW, self.midH + 100, "text", "")
        ]
        self.state = self.options[0]

    def displayMenu(self):
        self.runDisplay = True
        it = 0
        while self.runDisplay:
            self.game.checkEvents(self.game.inputMode)
            self.checkInput()
            self.game.display.fill(self.game.BLACK)
            self.game.display.blit(self.bg, (0,0))

            #Draw drone
            # it = (it +1) % 50
            # self.droneFrameIndex = (self.droneFrameIndex + 1) % len(self.droneSpFrames)
            # if self.droneFrameDir == 0:
            #     if it % self.droneFrameSpeed == 0: self.droneFrameH += 1
            #     if self.droneFrameH == self.droneFrameMinMaxH: 
            #         self.droneFrameMinMaxH = randint(0, 10)
            #         self.droneFrameSpeed = randint(6,9)
            #         self.droneFrameDir = 1
            # elif self.droneFrameDir == 1:
            #     if it % self.droneFrameSpeed == 0: self.droneFrameH -= 1
            #     if self.droneFrameH == 0: 
            #         self.droneFrameMinMaxH = randint(20, 30)
            #         self.droneFrameSpeed = randint(6,9)
            #         self.droneFrameDir = 0

            # self.game.display.blit(self.droneSpFrames[self.droneFrameIndex], (self.game.DISPLAY_W/2 - 200, self.game.DISPLAY_H /2 - 300 - self.droneFrameH))

            # self.game.drawText('Main Menu', self.headerSize, self.game.WHITE, self.game.DISPLAY_W/2, self.game.DISPLAY_H /2 - 30)
            for option in self.options:
                color = self.game.WHITE
                size = self.optionSize
                if self.state.id == option.id:
                    color = self.game.YELLOW
                    size = self.activeSize
                self.game.drawText(option.name, size + 10, color, option.posX, option.posY)

            # self.drawCursor()
            self.blitScreen()

    def moveCursor(self):
        if self.game.DOWN_KEY:
            if self.state.id < len(self.options) - 1:
                self.state = self.options[self.state.id + 1]
            else:
                self.state = self.options[0]

        elif self.game.UP_KEY:
            if self.state.id > 0:
                self.state = self.options[self.state.id - 1]
            else:
                self.state = self.options[len(self.options) - 1]

    def checkInput(self):
        self.moveCursor()
        if self.game.START_KEY:
            if self.state.name == 'Start':
                self.game.startGame()
            elif self.state.name == 'Options':
                self.game.currMenu = self.game.optionsMenu
            elif self.state.name == 'Exit':
                self.game.endGame()
            self.runDisplay = False

class OptionsMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        # self.state = 'Color Calibration'
        # self.colCalibrationX, self.colCalibrationY = self.midW, self.midH + 30
        # self.volX, self.volY = self.midW, self.midH + 60
        # self.controlsX, self.controlsY = self.midW, self.midH + 90

        # self.cursor.midtop = (self.colCalibrationX + self.offset, self.colCalibrationY)

        self.options = [
            self.Option(0, "Color Calibration", self.midW, self.midH + 30, "text", ""),
            self.Option(1, "Debug Mode", self.midW, self.midH + 60, "onoff", self.game.debug),
            self.Option(2, "Volume",  self.midW, self.midH + 140, "text", ""),
            self.Option(3, "Controls",  self.midW, self.midH + 170, "text", "")
        ]
        self.state = self.options[0]

    def displayMenu(self):
        self.runDisplay = True
        while self.runDisplay:
            self.game.checkEvents(self.game.inputMode)
            self.checkInput()
            self.game.display.fill(self.game.BLACK)

            self.game.drawText('Options', self.headerSize, self.game.WHITE, self.game.DISPLAY_W/2, self.game.DISPLAY_H /2 - 30)
            for option in self.options:
                color = self.game.WHITE
                size = self.optionSize
                if self.state.id == option.id:
                    color = self.game.YELLOW
                    size = self.activeSize
                self.game.drawText(option.name, size, color, option.posX, option.posY)
                if option.type == 'onoff':
                    self.game.drawOnOff(size, self.game.YELLOW, option.posX - 50, option.posY + 40, option.value)

            # self.drawCursor()
            self.blitScreen()

    def checkInput(self):
        if self.game.BACK_KEY:
            self.game.currMenu = self.game.mainMenu
            self.runDisplay = False

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

        elif self.game.LEFT_KEY:     
            if self.state.name == 'Debug Mode':
                if self.state.value == False:
                    self.options[self.state.id].value = True
                    self.saveDebugModeSetting(self.options[self.state.id].value)

        elif self.game.RIGHT_KEY:     
            if self.state.name == 'Debug Mode':
                if self.state.value == True:
                    self.options[self.state.id].value = False
                    self.saveDebugModeSetting(self.options[self.state.id].value)


        elif self.game.START_KEY:
            if self.state.name == 'Color Calibration':
                if self.game.debug == False:
                    self.game.colorCalibrationMenu.loadColorCalibrationMenu()
                if self.game.debug or self.game.drone.connected:
                    self.game.colorCalibrationMenu.loadColorHSV()
                    self.game.currMenu = self.game.colorCalibrationMenu
                else: #if failed to connect
                    return
            self.runDisplay = False

    def saveDebugModeSetting(self, value):
        self.game.applyDebugModeChange(value)


class DroneModeMenu(Menu):
    def __init__(self, game):
        Menu.__init__(self, game)
        self.posY = 40
        self.posX = self.game.DISPLAY_W - 100
        self.menuW = 180
        # Option = collections.namedtuple("Option", ["id", "name", "posX", "posY"])
        self.options = [
            self.Option(0, "Free Fly", self.posX, self.posY + 40, "text", ""),
            self.Option(1, "Object Tracking", self.posX, self.posY + 70, "text", ""),
            self.Option(2, "Face Tracking", self.posX, self.posY + 120, "text", ""),
            self.Option(3, "Find Colors", self.posX, self.posY + 170, "text", "")
        ]
        self.state = self.options[0]


    def displayMenu(self):
            self.game.checkEvents(self.game.inputMode)
            self.checkInput()

            self.game.drawTextCenteredAt('Mode', self.headerSize, self.game.WHITE, self.posX, self.posY, self.menuW)
            for option in self.options:
                color = self.game.WHITE
                size = self.optionSize
                if self.state.id == option.id:
                    color = self.game.YELLOW
                    size = self.activeSize
                self.game.drawTextCenteredAt(option.name, size, color, option.posX, option.posY, self.menuW)


    def checkInput(self):
        if self.game.BACK_KEY:
            self.game.currMenu = self.game.mainMenu
            self.runDisplay = False

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
            pass


