import pygame

class Button():
    def __init__(self, id, x, y, minW, font, size, text, color):
        self.id = id
        self.color = color
        self.colorBg = (0, 0, 0)
        self.x = x
        self.y = y
        self.minW = minW
        self.text = text
        self.font = font
        self.size = size
        self.borderSize = 4
        self.padding = 10

    def draw(self,win):
        #text
        font = pygame.font.Font(self.font, self.size)
        textSurface = font.render(self.text, True, self.color)
        textRect = textSurface.get_rect()
        textRect.center = (self.x, self.y)
        #background pos
        bgX = textRect.x - self.padding 
        bgY = textRect.y - self.padding
        bgW = max(self.minW, textRect.width + (2 * self.padding))
        bgH = textRect.height + (2 * self.padding)

        #border pos
        bX = bgX - self.borderSize 
        bY = bgY - self.borderSize
        bW = bgW + (2 * self.borderSize)
        bH = bgH + (2 * self.borderSize)

        self.area = (bX, bY, bW, bH)
        #draw
        pygame.draw.rect(win, self.color, (bX, bY, bW, bH),0)
        pygame.draw.rect(win, self.colorBg, (bgX, bgY, bgW, bgH),0)

        win.blit(textSurface, textRect)

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.width:
            if pos[1] > self.y and pos[1] < self.y + self.height:
                return True
            
        return False