from __future__ import annotations
from typing import *
import pygame as pg
import pygame.gfxdraw as gfxdraw # EXPERIMENTAL !!!
import random as rd
import numpy as np
import math
from scipy.interpolate import splprep, splev

class Element(pg.sprite.Sprite):

    def __init__(self) -> None:
        super().__init__()


class  Point(Element):
    
    def __init__(self, position:Tuple[float, float], radius:int=1, color:Tuple[int, int, int]=(-1, -1, -1), spline_parents:List[Spline]=list()) -> None:
        super().__init__()
        self.position = position
        self.display_radius = radius
        self.color = color
        self.spline_parents:List[Spline] = spline_parents

        self.img = pg.Surface((self.display_radius * 2 + 1, self.display_radius * 2 + 1), pg.SRCALPHA)
        self.img.set_colorkey((0, 0, 0))
        gfxdraw.filled_circle(self.img, self.display_radius, self.display_radius, self.display_radius, self.color)


    def add_parent_spline(self, new_parent:Spline):
        self.spline_parents.append(new_parent)

    def update_parent_spline(self):
        for spline in self.spline_parents:
            spline.update()

    def get_color(self):
        return self.color

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
        return pg.Rect((self.x - self.display_radius, self.y - self.display_radius), (self.display_radius * 2, self.display_radius * 2))
    
    def move(self, movement:Tuple[float, float] | List[float]):
        self.x += movement[0]
        self.y += movement[1]

        for spline in self.spline_parents:
            spline.update()

class BezierPoint(Point):
    C0 = 'C0'
    C1 = 'C1'
    G1 = 'G1'

    def __init__(self, position: Tuple[float, float], radius: int = 1, color: Tuple[int, int, int] = (-1, -1, -1)) -> None:
        super().__init__(position, radius, color)
        self.children:List[ChildPoint] = list()
        
        self.state = BezierPoint.C0
        
    def adopt(self, new_child):
        self.children.append(new_child)
        
    def toggle_C1(self):
        if len(self.children) < 2:
            return False
        
        if self.state == BezierPoint.C1:
            self.state = BezierPoint.C0
        else:
            self.state = BezierPoint.C1
        
        self.update_children(self.children[0])
    
    def update_children(self, locked_child:ChildPoint):
        if self.state == BezierPoint.C0:
            return False
        
        if self.children[0] is locked_child:
            update_child = self.children[1]
        else:
            update_child = self.children[0]
        
        if self.state == BezierPoint.C1:
            update_child.x = 2 * self.x - locked_child.x
            update_child.y = 2 * self.y - locked_child.y
        
        self.update_parent_spline()
    
    def move(self, movement:Tuple[float, float] | List[float]):
        super().update()
        super().move(movement)
        self.children[0].move(movement, update=False)
        if len(self.children) > 1:
            self.children[1].move(movement, update=False)
            


class ChildPoint(Point):
    # Possible states of existence

    def __init__(self, parent:BezierPoint, position: Tuple[float, float], radius: int = 1, color: Tuple[int, int, int] = (-1, -1, -1)) -> None:
        super().__init__(position, radius, color)

        self.parent = parent
        self.parent.adopt(self)
    
    def move(self, movement:Tuple[float, float] | List[float], update:bool=True):
        super().update()
        super().move(movement)
        if update:
            self.parent.update_children(self)
        
        

class LineBetweenPoints(Element):

    def __init__(self, this_point, the_other_point, color:Tuple[int, int, int] = (0, 0, 0)) -> None:
        super().__init__()
        self.points = [this_point, the_other_point]
        self.color = color
    @property
    def img(self):
        width = abs(self.points[0].x - self.points[1].x)
        height = abs(self.points[0].y - self.points[1].y)
        img = pg.Surface((width + 2, height + 2), pg.SRCALPHA)
        leftmost_point, rightmost_point = self.points

        if leftmost_point.x > rightmost_point.x:
            rightmost_point, leftmost_point = leftmost_point, rightmost_point


        gfxdraw.line(img, 
                     0, 
                     int(max(0,leftmost_point.y - rightmost_point.y)), 
                     int(rightmost_point.x - leftmost_point.x), 
                     int(max(0,rightmost_point.y - leftmost_point.y)), 
                     self.color)
        return img
    
    @property
    def rect(self):
        return pg.Rect(
            (min(self.points[0].x, self.points[1].x)),
            min(self.points[0].y, self.points[1].y),
            abs(self.points[0].x - self.points[1].x),
            abs(self.points[0].y - self.points[1].y))


class Spline(Element):

    def __init__(self, points:Tuple[Point, Point, Point, Point], color:Tuple[int, int, int]=(0,0,0)) -> None:
        super().__init__()
        self.points = points
        self.bezier_points = list()
        self.start_point = points[0]
        self.end_point = points[3]
        self.color = color
        self.width = 10
        self.update()

        self.lines = (LineBetweenPoints(self.points[0], self.points[1], (255,255,255)),
                      LineBetweenPoints(self.points[2], self.points[3], (255,255,255)))

        for point in self.points:
            point.add_parent_spline(self)

    @classmethod
    def from_nothing(cls, spline_color:Tuple[int,int,int], start_pos:Tuple[int,int], point_radius:int, first_color:Tuple[int,int,int], second_color:Tuple[int,int,int]):
        points_pos = [(start_pos[0] + 30*i, start_pos[1]) for i in range(4)]

        start_point = BezierPoint(points_pos[0], point_radius, first_color)
        end_point = BezierPoint(points_pos[3], point_radius, second_color)
        return cls(
            (start_point,
            ChildPoint(start_point, points_pos[1], point_radius, first_color),
            ChildPoint(end_point, points_pos[2], point_radius, second_color),
            end_point),
            spline_color)


    @classmethod
    def from_spline(cls, spline_color:Tuple[int,int,int], previous_spline:Spline, second_color:Tuple[int,int,int]):
        x_diff = min(previous_spline.points[3].x - previous_spline.points[2].x, 60)
        y_diff = min(previous_spline.points[3].y - previous_spline.points[2].y, 60)
        
        start_pos = previous_spline.end_point.position
        point_radius = previous_spline.end_point.display_radius
        first_color = previous_spline.end_point.color

        points_pos = [(start_pos[0] + x_diff * i, start_pos[1] + y_diff * i) for i in range(1,4)]

        end_point = BezierPoint(points_pos[2], point_radius, second_color)
        return cls(
            (previous_spline.end_point,
            ChildPoint(previous_spline.end_point, points_pos[0], point_radius, first_color),
            ChildPoint(end_point, points_pos[1], point_radius, second_color),
            end_point),
            spline_color)

    @classmethod
    def to_spline(cls, spline_color:Tuple[int,int,int], previous_spline:Spline, next_spline:Spline):
        x_diff = min(previous_spline.points[3].x - previous_spline.points[2].x, 60)
        y_diff = min(previous_spline.points[3].y - previous_spline.points[2].y, 60)
        
        start_x = previous_spline.end_point.x
        start_y = previous_spline.end_point.y
        point_1_pos = (start_x + x_diff, start_y + y_diff)
        point_2_pos = (start_x + 2 * x_diff, start_y + 2 * y_diff)
        
        
        point_radius = previous_spline.end_point.display_radius
        first_color = previous_spline.end_point.color
        second_color = next_spline.start_point.color

        new_spline = cls(
            (previous_spline.end_point,
            ChildPoint(previous_spline.end_point, point_1_pos, point_radius, first_color),
            ChildPoint(next_spline.start_point, point_2_pos, point_radius, second_color),
            next_spline.start_point),
            spline_color)

        for point in new_spline.points:
            point.add_parent_spline(new_spline)

        return new_spline

    def bezier(self, t):
        n = len(self.points) - 1
        return sum(
            self.binomial_coeff(n, i) * (1 - t)**(n - i) * t**i * np.array([self.points[i].x, self.points[i].y])
            for i in range(n + 1)
        )

    def binomial_coeff(self, n, k):
        return math.factorial(n) // (math.factorial(k) * math.factorial(n - k))


    def update(self):
        padding = self.width + 2
        max_x = max(point.x for point in self.points)
        min_x = min(point.x for point in self.points)
        max_y = max(point.y for point in self.points)
        min_y = min(point.y for point in self.points)

        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        
        self.bezier_points = [self.bezier(t) for t in np.linspace(0, 1, (width + height))]
        self.bezier_points = [(int(x - min_x + padding), int(y - min_y + padding)) for x, y in self.bezier_points]
        

    @property
    def img(self):
        padding = self.width + 2
        max_x = max(point.x for point in self.points)
        min_x = min(point.x for point in self.points)
        max_y = max(point.y for point in self.points)
        min_y = min(point.y for point in self.points)

        width = max_x - min_x + 2 * padding
        height = max_y - min_y + 2 * padding
        
        img = pg.Surface((width, height), pg.SRCALPHA)
        
        for i in range(width+height):
            pg.draw.circle(img, self.color, self.bezier_points[i], self.width//2)

        return img

    @property
    def rect(self):
        padding = self.width + 2  # Ensure rect property has the same padding
        max_x = max(point.x for point in self.points)
        min_x = min(point.x for point in self.points)
        max_y = max(point.y for point in self.points)
        min_y = min(point.y for point in self.points)
        return pg.Rect(
            min_x - padding,
            min_y - padding,
            max_x - min_x + 2 * padding,
            max_y - min_y + 2 * padding)