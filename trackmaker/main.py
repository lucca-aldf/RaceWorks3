import pygame as pg
import random as rd
from typing import *
from geometry import *
from gui import *
from tab import *
from trackmaker_tab import *
from utils import *

SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800

POINT_RADIUS = 12

camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
race_tab = TrackMakerTab(camera.screen, 12000, 8000, default_point_radius=POINT_RADIUS, starting_position=(6000, 4000))

camera.append(race_tab)
get_new_point_color = lambda : (rd.randint(51, 204), rd.randint(51, 204), rd.randint(51, 204))
get_new_line_color = lambda : COLOR_WHITE

pg.display.set_caption("Trackmaker")

clock = pg.time.Clock()
running = True
while running:
    for event in pg.event.get():
        if event.type == pg.QUIT or (event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_ESCAPE]):
            running = False
            break
        
        else:
            camera.actions(event)


    camera.update()
    clock.tick(60)
    #print(clock.get_fps())
    
pg.quit()
