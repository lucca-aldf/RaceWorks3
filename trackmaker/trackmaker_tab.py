from typing import *
from typing import Iterable
from pygame.sprite import AbstractGroup
from tab import *
from geometry import *
import pygame as pg
from random import randint
from utils import *

def get_point_under_mouse(points:List[Point], mouse_position:Tuple[int, int]):
    for point in points:
        if point.rect.collidepoint(mouse_position):
            return point
        
    return None

def generate_random_color(lower_bounds:Tuple[int,int,int]=(0,0,0), upper_bounds:Tuple[int,int,int]=(255,255,255)) -> Tuple[int,int,int]:
        return (randint(lower_bounds[0], upper_bounds[0]), randint(lower_bounds[1], upper_bounds[1]), randint(lower_bounds[2], upper_bounds[2]))


class TrackMakerTab(Tab):

    class SubGroup(pg.sprite.Group):

        def __init__(self, *sprites: Any | AbstractGroup | Iterable) -> None:
            super().__init__(*sprites)
    
    def __init__(self,
                 screen:pg.display,
                 width: int, 
                 height: int, 
                 forced_perspective=False, 
                 starting_position: Tuple[float, float] = None, 
                 starting_zoom: float = 1,
                 default_point_radius = 10) -> None:
        super().__init__(screen, width, height, forced_perspective, starting_position, starting_zoom)

        self.points = pg.sprite.Group()
        self.lines = pg.sprite.Group()
        self.splines = pg.sprite.Group()
        self.loops = pg.sprite.Group()

        self.points_visibility = True
        self.lines_visibility = True
        self.splines_visibility = True

        self.point_radius = default_point_radius
    
        self.to_connect_spline: Spline | None = None
        self.start_loop_spline: Spline | None = None
        self.dragged_point: Point | None = None

    def actions(self, event):
        this_spline: Spline | None = None
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and not pg.key.get_pressed()[pg.K_z]:
            self.dragged_point = get_point_under_mouse(self.points, self.get_mouse_pos())
            
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            self.dragged_point = None

        elif event.type == pg.MOUSEMOTION and self.dragged_point:
            self.dragged_point.move(tuple(map(int, multiply_tuple(event.rel, (2 ** -self.zoom)))))

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:# and pg.key.get_pressed()[pg.K_LSHIFT]:
            this_point = get_point_under_mouse(self.points, self.get_mouse_pos())
            mouse_pos = self.get_mouse_pos()

            if not self.to_connect_spline:
                first_color = generate_random_color(lower_bounds=(51,51,51))
                second_color = generate_random_color(lower_bounds=(51,51,51))
                
                this_spline = Spline.from_nothing(COLOR_TRACK,
                                     mouse_pos, self.point_radius, first_color, second_color)
                
                self.points.add(this_spline.points)
                self.lines.add(this_spline.lines)
                self.splines.add(this_spline)

                self.start_loop_spline = this_spline
                self.to_connect_spline = this_spline

            elif not this_point:
                second_color = generate_random_color(lower_bounds=(51,51,51))

                this_spline = Spline.from_spline(COLOR_TRACK,
                                                 self.to_connect_spline,
                                                 second_color)
                                      
                self.points.add(this_spline.points[1:])
                self.lines.add(this_spline.lines)
                self.splines.add(this_spline)

                self.to_connect_spline = this_spline
            
            elif this_point is self.start_loop_spline.start_point:
                
                this_spline = Spline.to_spline(COLOR_TRACK,
                                                 self.to_connect_spline,
                                                 self.start_loop_spline)
                                      
                self.points.add(this_spline.points[1:3])
                self.lines.add(this_spline.lines)
                self.splines.add(this_spline)

                self.start_loop_spline = None
                self.to_connect_spline = None
        
        elif event.type == pg.MOUSEMOTION and pg.mouse.get_pressed()[1]:
            self.x -= event.rel[0] * (2 ** -self.zoom)
            self.y -= event.rel[1] * (2 ** -self.zoom)

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 4:
                self.zoom += 0.1

        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 5:
            self.zoom -= 0.1
                
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1 and pg.key.get_pressed()[pg.K_z]:
            this_point = get_point_under_mouse(self.points, self.get_mouse_pos())
            if type(this_point) is BezierPoint:
                this_point.toggle_C1()
            
        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_w]:
            self.y -= 100

        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_s]:
            self.y += 100
        
        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_a]:
            self.x -= 100

        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_d]:
            self.x += 100

        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_F1]:
            self.points_visibility = not self.points_visibility

        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_F2]:
            self.lines_visibility = not self.lines_visibility
        
        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_F3]:
            self.splines_visibility = not self.splines_visibility
        
        elif event.type == pg.KEYDOWN and pg.key.get_pressed()[pg.K_RETURN]:
            if len(self.splines) == 0:
                return

            save_list: List = []

            splines = list(self.splines.sprites())
            
            for point in splines[0].points:
                save_list.append(point.position)

            if len(self.splines) == 1:
                print(save_list)
                return

            for i in range(1, len(splines)):
                for j in range(1, 4):
                    save_list.append(splines[i].points[j].position)

            if save_list[0] == save_list[-1]:
                save_list.pop()

            print(save_list)

        
        self.x = max(0, min(self.width, self.x))
        self.y = max(0, min(self.height, self.y))
    
    def render(self):
        sprites = pg.sprite.Group()

        if self.points_visibility:
            sprites.add(self.points)
            
        if self.lines_visibility:
            sprites.add(self.lines)

        if self.splines_visibility:
            sprites.add(self.splines)

        #self.sprites.add(self.loops)
        return super().render(sprites)

    
    """def save_splines(self):
        for spline in self.splines.sprites():"""