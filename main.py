"""
This is where the application logic is supposed to run
"""
import pygame
from pygame.locals import *
from components import Spinner, SpinnerButton, Colors, GameStatus, GuessGrid

# THIS IS TO BE REMOVED/MODIFIED WHEN MOVING PROJECT TO KIVY/PHONES
DISPLAYSURF = pygame.display.set_mode((300,600))


for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
    pygame.display.update()