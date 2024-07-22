import math
import pygame as pg
import numpy as np
import torch
from .network import AlphaNet
import random as rd

NETWORK = AlphaNet

def line_tracer_2(angle, start_x, start_y, mask):
    x = int(start_x)
    y = int(start_y)

    if angle >= 360:
        angle -= 360

    angle = math.radians(angle)
    angle = round(angle, 1)

    if (45 > angle > 0 or 225 > angle > 135 or 360 > angle > 315) and angle != 180:
        if angle > 270 or angle < 90:
            n = 1
        else:
            n = -1
        dx = math.tan(angle)
        while True:
            if mask.get_at((int(x), int(y))) == 1:
                break
            y -= n
            x += dx * n

    elif (135 > angle > 45 or 315 > angle > 225) and angle != 90 and angle != 270:
        if angle < 180:
            n = 1
        else:
            n = -1
        dy = math.tan(angle) ** -1
        while True:
            if mask.get_at((int(x), int(y))) == 1:
                break
            x += n
            y -= dy * n
            # pg.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 1, 1)

    elif angle == 0 or angle == 180:
        if angle == 0:
            n = 1
        else:
            n = -1
        while True:
            if mask.get_at((int(x), int(y))) == 1:
                break
            y -= n
            # pg.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 1, 1)

    elif angle == 90 or angle == 270:
        if angle == 90:
            n = 1
        else:
            n = -1
        while True:
            if mask.get_at((int(x), int(y))) == 1:
                break
            x += n
            # pg.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 1, 1)
    return distance_two_points((int(x), int(y)), (int(start_x), int(start_y)))

def line_tracer(angle, start_x, start_y, mask):
    x = int(start_x)
    y = int(start_y)

    angle %= 360
    angle_rad = math.radians(angle)
    cos_angle = math.cos(angle_rad)
    sin_angle = math.sin(angle_rad)

    step_size = max(abs(cos_angle), abs(sin_angle))
    cos_angle /= step_size
    sin_angle /= step_size

    while True:
        print(f"Checking square: ({int(x)}, {int(y)})")
        if mask.get_at((int(x), int(y))) == 1:
            break
        x += cos_angle
        y -= sin_angle

    return math.sqrt((int(x) - start_x) ** 2 + (int(y) - start_y) ** 2)


def distance_two_points(p1, p2):
    return math.sqrt((p1[0] - p2[0]) ** 2 + (p1[1] - p2[1]) ** 2)


class Car(pg.sprite.Sprite):
    id = 0
    distance = 0

    def set_track_mask(mask):
        Car.track_mask = mask

    def set_max_distance(distance):
        Car.max_distance = distance

    def __init__(self, network=NETWORK()):
        global gen_counter

        self.id = Car.id
        self.network = network
        self.throttle = 0
        self.turning = 0

        self.top_speed = 8
        self.acceleration = 0.7
        self.brake = 2
        self.turning_angle = 10

        self.crash = False
        self.angle = self.original_angle = 90
        self.rad_angle = math.radians(self.angle)
        self.x = self.x_coord = 604
        self.y = self.y_coord = 486
        self.speed = 0
        self.age = 0

        self.original_image = pg.image.load("gfx/Formula Rossa Car.png")
        self.image = pg.transform.rotate(self.original_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.mask = pg.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.width, self.height = self.rect.center

        self.distance = 0
        self.gap_to_cp = 0
        self.points = 0

    def get_data(self):
        return self.network.get_data()

    def update_car(self):
        if self.crash:
            return
        
        else:
            self.age += 1
            if 0.2*self.age - self.distance > 20:
                self.crash = True
                return


            self.image = pg.transform.rotate(self.original_image, -self.angle)

            self.mask = pg.mask.from_surface(self.image)
            self.rect = self.image.get_rect()
            dump, dump, self.width, self.height = self.rect
            "%.3f" % self.angle

            
            input_data = [
            self.speed,
            math.log2(line_tracer_2(self.angle, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 15, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 45, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 90, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 270, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 315, self.x, self.y, Car.track_mask)),
            math.log2(line_tracer_2(self.angle + 345, self.x, self.y, Car.track_mask))
            ]

            print(input_data)
            #[0, 3.169925001442312, 3.2459265481648374, 3.669925001442312, 8.7714894695006, 8.499845887083206, 3.669925001442312, 3.204695468068851]
            raise Exception
            self.throttle, self.turning = self.network.forward(input_data)


            self.angle = self.angle % 360

            if self.throttle > 1:
                self.throttle = 1
            elif self.throttle < -1:
                self.throttle = -1

            if self.throttle > 0:
                self.speed += self.acceleration * self.throttle
            else:
                self.speed += self.brake * self.throttle

            if self.turning > 1:
                self.turning = 1
            elif self.turning < -1:
                self.turning = -1

            if self.speed > self.top_speed:
                self.speed = self.top_speed
            elif self.speed < 0:
                self.speed = 0

            if self.speed > 1:
                self.angle += (self.turning_angle / self.speed) * self.turning
            elif self.speed > 0.5:
                self.angle += self.turning_angle * self.turning
            else:
                pass

            if self.angle >= 360:
                self.angle -= 360
            elif self.angle < 0:
                self.angle += 360
            else:
                pass

            self.distance += self.speed

            self.rad_angle = math.radians(self.angle)
            self.x += math.sin(self.rad_angle) * self.speed
            self.y -= math.cos(self.rad_angle) * self.speed

            self.pos_x = self.x - self.width / 2
            self.pos_y = self.y - self.height / 2
            #screen.blit(self.image, (int(self.pos_x), int(self.pos_y)))


            if Car.track_mask.overlap(self.mask, ((int(self.pos_x), int(self.pos_y)))):
                self.crash = True

    def fitness(self):
        return self.distance

                            
    def reset_car(self): # Deprecated
        self.x = self.x_coord
        self.y = self.y_coord
        self.speed = 0
        self.crash = False
        self.angle = self.original_angle
        self.points = 0
        self.distance = 0

