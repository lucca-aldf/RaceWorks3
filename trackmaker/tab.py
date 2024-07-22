from typing import *
import pygame as pg
from utils import *


class Tab:

    def __init__(self, screen:pg.display, width:int, height:int, forced_perspective=False, starting_position:Tuple[float, float]=None, starting_zoom:float=0.0) -> None:
        self.screen = screen
        self.window_resolution = tuple(screen.get_rect())[2:]
        self.sprites:pg.sprite.Group = pg.sprite.Group()
        self.width = width
        self.height = height
        self.resolution = (width, height)
        self.forced_perspective = forced_perspective
        if starting_position:
            self.position = starting_position
        else:
            self.position = (self.width / 2, self.height / 2)
            self.position = (self.screen.get_window_size()[0], self.screen.get_window_size()[1])
        self.zoom = starting_zoom
        self.font = pg.font.SysFont('century', 18)
        
        #self.canvas = pg.Surface(screen.get_size())
        self.pre_processing:List[Tuple[function, list]] = list()
        self.post_processing:List[Tuple[function, list]] = list()

    @property
    def x(self):
        return self.position[0]
    
    @x.setter
    def x(self, value:int):
        self.position = (value, self.y)

    @property
    def y(self):
        return self.position[1]

    @y.setter
    def y(self, value:int):
        self.position = (self.x, value)

    @property
    def rect(self):
        return pg.Rect(self.x, self.y, self.width, self.height)

    def append(self, sprite:pg.sprite.Sprite):
        self.sprites.add(sprite)

    def get_mouse_pos(self):
        mouse_pos = pg.mouse.get_pos()
        mouse_pos = subtract_tuples(mouse_pos, multiply_tuple(self.window_resolution, 0.5))
        mouse_pos = (mouse_pos[0] / (2 ** self.zoom), mouse_pos[1] / (2 ** self.zoom))
        mouse_pos = add_tuples(mouse_pos, self.position)
        return tuple(map(int, mouse_pos))

    def add_pre_processing(self, method, parameters):
        self.pre_processing.append((method, parameters))
    
    def add_post_processing(self, method, parameters):
        self.post_processing.append((method, parameters))

    def render(self, sprites:list[pg.sprite.Sprite] | None=None):
        canvas =  pg.Surface(self.screen.get_size())
        canvas.fill(COLOR_BACKGROUND)
        
        for method, parameters in self.pre_processing:
            method(*parameters)

        if not sprites:
            sprites = self.sprites

        rects = [sprite.rect.copy() for sprite in sprites]

        sprites = [pg.transform.scale(sprite.img, 
                                    (int(sprite.img.get_width() * (2 ** self.zoom)), 
                                     int(sprite.img.get_height() * (2 ** self.zoom)))) for sprite in sprites]

        '''y = 130

        for rect in rects:
            canvas.blit(self.font.render(str(rect) + " " + str(self.window_resolution[0] / 2 + (rect.x - self.x) * (2 ** self.zoom)), False, (255, 255, 255)), (10, y))
            y+=30'''

        for rect in rects:
            rect.x = int(self.window_resolution[0] / 2 + ((rect.x - self.x) * (2 ** self.zoom)))
            rect.y = int(self.window_resolution[1] / 2 + ((rect.y - self.y) * (2 ** self.zoom)))
            rect.width = int(rect.width * self.zoom)
            rect.height = int(rect.height * self.zoom)

        for sprite, rect in zip(sprites, rects):
            canvas.blit(sprite, rect)

        '''canvas.blit(self.font.render(str(self.position), False, (255, 255, 255)), (10, 40))
        canvas.blit(self.font.render(str(self.window_resolution), False, (255, 255, 255)), (10, 70))
        canvas.blit(self.font.render(str(self.zoom), False, (255, 255, 255)), (10, 100))'''

        for method, parameters in self.post_processing:
            method(*parameters)

        return canvas, self.rect