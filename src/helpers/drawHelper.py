import pygame
import cv2
import numpy as np

from gui.button import Button
from gui.inputBox import InputBox

class DrawHelper:

    def drawText(self, text, size, color, x, y):
        font = pygame.font.Font(self.fontName, size)
        textSurface =  font.render(text, True, color)
        textRect = textSurface.get_rect()
        textRect.center = (x, y)
        self.display.blit(textSurface, textRect)

    def drawDebug(self):
        if self.debug:
            self.drawTextCenteredAt('DEBUG', 20, self.YELLOW, 100, 40, 180)

    def drawBattery(self, batteryLevel):

        batteryH = int((self.videoInputSize[1] * batteryLevel) / 100)
        batteryY = int(self.videoInputSize[1] - batteryH)
        pygame.draw.rect(self.display, self.YELLOW, ( 50, 42 + batteryY, 40, self.videoInputSize[1] - batteryY), 0)
        pygame.draw.rect(self.display, self.WHITE, ( 50, 44, 40, self.videoInputSize[1]), 5)


    def drawVideoFrame(self, frame):
        # y, x, _  = frame.shape
        # frameRect = frame.get_rect()

        frame = np.rot90(frame)
        frame= cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        pyframe = pygame.surfarray.make_surface(frame)
        pyframe = pygame.transform.flip(pyframe, True, False)
        frameRect = pyframe.get_rect()
        frameRect.center = (self.DISPLAY_W/2, self.DISPLAY_H/2 - 100)
        self.display.blit(pyframe, frameRect)

        rect = pygame.Rect(frameRect)
        pygame.draw.rect(self.display, self.WHITE, rect, 5)

    def drawDroneModes(self):
        self.drawTextCenteredAt('Mode', 20, self.WHITE, self.DISPLAY_W - 95, 40, 180)
        for dm in self.droneModes:
            color = self.WHITE
            size = 15
            if dm.id == self.droneMode.value:
                color = self.YELLOW
                size = 16
            # if len(dm.name) < 10: numOffset = 0 
            # else: numOffset = 8
            # self.drawTextCenteredAt(str(dm.id), size, color, dm.posX - 85, dm.posY + numOffset, 10)
            self.drawTextCenteredAt(dm.name, size, color, dm.posX, dm.posY, 160)


    def drawTextCenteredAt(self, text, size, color,  x, y, allowed_width):
        font = pygame.font.Font(self.fontName, size)
        words = text.split()
        lines = []
        while len(words) > 0:
            # get as many words as will fit within allowed_width
            line_words = []
            while len(words) > 0:
                line_words.append(words.pop(0))
                fw, fh = font.size(' '.join(line_words + words[:1]))
                if fw > allowed_width:
                    break

            line = ' '.join(line_words)
            lines.append(line)
        y_offset = 0
        for line in lines:
            fw, fh = font.size(line)
            tx = x - fw / 2
            ty = y + y_offset

            font_surface = font.render(line, True, color)
            self.display.blit(font_surface, (tx, ty))

            y_offset += fh

    def drawButton(self, id, x, y, minW, font, size, text='', textColor = (255, 255, 255)):
        button = Button(id, x, y, minW, font, size, text, textColor)
        button.draw(self.display)

    def drawInputBox(self, id, x, y, minW, text, size, color):
        # inputBox = InputBox(id, x, y, text, size, self.fontName, color, self.YELLOW)
        # inputBox.draw(self.display)

        ib = InputBox(id, x, y, minW, self.fontName, size, text, color, self.BLACK, self.WHITE)
        ib.draw(self.display)

    def drawOnOff(self, size, color, x, y, value):
        if value == True:
            onColor = color
            offColor = self.WHITE
        else:
            onColor = self.WHITE
            offColor = color

        self.drawButton(1, x, y, 60, self.fontName, size, 'ON', onColor)
        self.drawButton(2, x + 90, y, 60, self.fontName, size, 'OFF', offColor)
        

    def drawGrid(self):
        blockSize = 20 #Set the size of the grid block
        for x in range(self.DISPLAY_W):
            for y in range(self.DISPLAY_H):
                rect = pygame.Rect(x*blockSize, y*blockSize,
                                blockSize, blockSize)
                pygame.draw.rect(self.display, self.WHITE, rect, 1)


    def drawProgressBar(self, val, max, colorComplete, x, y, w):
        complete = False
        color = self.WHITE
        if val >= max:
            val = max
            color = colorComplete
            complete = True
        progress = int((val / max) * w)
        pygame.draw.rect(self.display, color, ( x, y, progress, 23), 0)
        pygame.draw.rect(self.display, self.WHITE, ( x, y, w, 23), 5)
        return complete

    def drawLoading(self):
        x, y = self.DISPLAY_W/2, self.DISPLAY_H/2
        self.display.fill(self.BLACK)
        self.drawText("LOADING...", 20, self.WHITE, x, y)
        self.window.blit(self.display, (0, 0))
        pygame.display.update()