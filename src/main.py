from game import Game

g = Game()

while g.running:
    g.currMenu.displayMenu()
    g.gameLoop()