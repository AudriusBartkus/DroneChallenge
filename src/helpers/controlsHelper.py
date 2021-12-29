import pygame

class ControlsHelper:

    def checkKeyboardInput(self):
            if self.getKey("LEFT"):
                pass


    def getKey(self, keyName):
        ans = False
        for eve in pygame.event.get(): pass
        keyInput = pygame.key.get_pressed()
        myKey = getattr(pygame, 'K_{}'.format(keyName))
        if keyInput[myKey]:
            ans = True
        # pygame.display.update() #TODO: needed?
        return ans

    def checkEvents(self, mode = "keyboard"):
        if mode == "keyboard":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.endGame()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.START_KEY = True
                    if event.key == pygame.K_ESCAPE:
                        self.BACK_KEY = True
                    if event.key == pygame.K_DOWN:
                        self.DOWN_KEY = True
                    if event.key == pygame.K_UP:
                        self.UP_KEY = True
                    if event.key == pygame.K_LEFT:
                        self.LEFT_KEY = True
                    if event.key == pygame.K_RIGHT:
                        self.RIGHT_KEY = True
                    if event.key == pygame.K_t:
                        self.D_TAKEOFF_KEY = True
                    if event.key == pygame.K_l:
                        self.D_LAND_KEY = True
                    if event.key == pygame.K_b:
                        self.D_BACK_TO_START = True
                    if event.key == pygame.K_1:
                        self.D_NONE_KEY = True
                    if event.key == pygame.K_2:
                        self.D_FREE_FLY_KEY = True
                    if event.key == pygame.K_3:
                        self.D_TRACK_OBJ_KEY = True
                    if event.key == pygame.K_4:
                        self.D_FIND_COLORS_KEY = True
                    if event.key == pygame.K_5:
                        self.D_TRACK_FACE_KEY = True
                    if event.key == pygame.K_6:
                        self.D_GESTURE_KEY = True
                    if event.key == pygame.K_7:
                        self.D_FIND_NUMBER_KEY = True
                    if event.key == pygame.K_8:
                        self.D_ARUCO_KEY = True
            
            #Check pressed (hold) keys / for continuous input
            keyInput = pygame.key.get_pressed()
            if keyInput[pygame.K_w]:
                self.D_FW_KEY = True
            if keyInput[pygame.K_s]:
                self.D_BW_KEY = True
            if keyInput[pygame.K_a]:
                self.D_LEFT_KEY = True
            if keyInput[pygame.K_d]:
                self.D_RIGHT_KEY = True
            if keyInput[pygame.K_r]:
                self.D_UP_KEY = True
            if keyInput[pygame.K_f]:
                self.D_DOWN_KEY = True
            if keyInput[pygame.K_e]:
                self.D_ROTATEC_KEY = True
            if keyInput[pygame.K_q]:
                self.D_ROTATECC_KEY = True
        elif mode == "picade":
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.endGame()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.START_KEY = True
                    if event.key == pygame.K_ESCAPE:
                        self.BACK_KEY = True
                    if event.key == pygame.K_DOWN:
                        self.DOWN_KEY = True
                    if event.key == pygame.K_UP:
                        self.UP_KEY = True
                    if event.key == pygame.K_LEFT:
                        self.LEFT_KEY = True
                    if event.key == pygame.K_RIGHT:
                        self.RIGHT_KEY = True
                    if event.key == pygame.K_i:
                        self.D_TAKEOFF_KEY = True
                    if event.key == pygame.K_o:
                        self.D_LAND_KEY = True
                    if event.key == pygame.K_b:
                        self.D_BACK_TO_START = True
                    if event.key == pygame.K_1:
                        self.D_NONE_KEY = True
                    if event.key == pygame.K_2:
                        self.D_FREE_FLY_KEY = True
                    if event.key == pygame.K_3:
                        self.D_TRACK_OBJ_KEY = True
                    if event.key == pygame.K_4:
                        self.D_FIND_COLORS_KEY = True
                    if event.key == pygame.K_5:
                        self.D_TRACK_FACE_KEY = True
                    if event.key == pygame.K_6:
                        self.D_GESTURE_KEY = True
                    if event.key == pygame.K_7:
                        self.D_FIND_NUMBER_KEY = True
                    if event.key == pygame.K_8:
                        self.D_ARUCO_KEY = True
            
            #Check pressed (hold) keys / for continuous input
            keyInput = pygame.key.get_pressed()
            if keyInput[pygame.K_UP]:
                self.D_FW_KEY = True
            if keyInput[pygame.K_DOWN]:
                self.D_BW_KEY = True
            if keyInput[pygame.K_LEFT]:
                self.D_LEFT_KEY = True
            if keyInput[pygame.K_RIGHT]:
                self.D_RIGHT_KEY = True
            if keyInput[pygame.K_LALT]:
                self.D_UP_KEY = True
            if keyInput[pygame.K_z]:
                self.D_DOWN_KEY = True
            if keyInput[pygame.K_LSHIFT]:
                self.D_ROTATEC_KEY = True
            if keyInput[pygame.K_x]:
                self.D_ROTATECC_KEY = True