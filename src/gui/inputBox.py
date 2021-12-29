import pygame

# COLOR_INACTIVE = pygame.Color('lightskyblue3')
# COLOR_ACTIVE = pygame.Color('dodgerblue2')
# FONT = pygame.font.Font(None, 32)


class InputBox:

    def __init__(self, id, x, y, minW, font, size, text, colorText, colorBg, colorBorder):
        self.id = id
        self.colorBg = colorBg
        self.colorBorder = colorBorder
        self.colorText = colorText
        self.x = x
        self.y = y
        self.minW = minW
        self.text = text
        self.font = font
        self.size = size
        self.borderSize = 2
        self.padding = 10


    def draw(self,win):
        #text
        font = pygame.font.Font(self.font, self.size)
        textSurface = font.render(self.text, True, self.colorText)
        textRect = textSurface.get_rect()
        textRect.w = max(self.minW, textRect.w)
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
        pygame.draw.rect(win, self.colorBorder, (bX, bY, bW, bH),self.borderSize)
        pygame.draw.rect(win, self.colorBg, (bgX, bgY, bgW, bgH),0)

        win.blit(textSurface, textRect)

    def isOver(self, pos):
        #Pos is the mouse position or a tuple of (x,y) coordinates
        if pos[0] > self.x and pos[0] < self.x + self.area[2]:
            if pos[1] > self.y and pos[1] < self.y + self.area[3]:
                return True
            
        return False

    # def __init__(self,id, x, y, text, size, font, color, colorActive):
    #     # self.rect = pygame.Rect(x, y, w, h)
    #     self.id = id
    #     self.minW = 100
    #     self.x = x
    #     self.y = y
    #     self.color = color
    #     self.colorInactive = color
    #     self.colorActive = colorActive
    #     self.font = pygame.font.Font(font, size)
       
    #     self.text = text
    #     # self.txt_surface = FONT.render(text, True, self.color)
    #     self.active = False

    # def handle_event(self, event):
    #     if event.type == pygame.MOUSEBUTTONDOWN:
    #         # If the user clicked on the input_box rect.
    #         if self.rect.collidepoint(event.pos):
    #             # Toggle the active variable.
    #             self.active = not self.active
    #         else:
    #             self.active = False
    #         # Change the current color of the input box.
    #         self.color = self.colorActive if self.active else self.colorInactive
    #     if event.type == pygame.KEYDOWN:
    #         if self.active:
    #             if event.key == pygame.K_RETURN:
    #                 print(self.text)
    #                 self.text = ''
    #             elif event.key == pygame.K_BACKSPACE:
    #                 self.text = self.text[:-1]
    #             else:
    #                 self.text += event.unicode
    #             # Re-render the text.
    #             self.txtSurface = self.font.render(self.text, True, self.color)

    # def update(self):
    #     # Resize the box if the text is too long.
    #     width = max(self.minW, self.txtSurface.get_width()+10)
    #     self.textRect.w = width

    # def draw(self, screen):
    #     # font = pygame.font.Font(self.font, self.size)
    #     textSurface = self.font.render(self.text, True, self.color)
    #     textRect = textSurface.get_rect()
    #     textRect.w = max(self.minW, textRect.w)
    #     textRect.h += 10
    #     textRect.center = (self.x, self.y)
    #     # Blit the text.
    #     screen.blit(textSurface, textRect)
    #     # Blit the rect.
    #     pygame.draw.rect(screen, self.color, textRect, 2)



# def main():
#     clock = pygame.time.Clock()
#     input_box1 = InputBox(100, 100, 140, 32)
#     input_box2 = InputBox(100, 300, 140, 32)
#     input_boxes = [input_box1, input_box2]
#     done = False

#     while not done:
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 done = True
#             for box in input_boxes:
#                 box.handle_event(event)

#         for box in input_boxes:
#             box.update()

#         screen.fill((30, 30, 30))
#         for box in input_boxes:
#             box.draw(screen)

#         pygame.display.flip()
#         clock.tick(30)


# if __name__ == '__main__':
#     main()
#     pygame.quit()