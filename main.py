# A simulation by Lucca Limongi

import random as rd
import time
import pygame as pg
from core import *

pg.init()
pg.display.init()

pg.display.gl_set_attribute(pg.GL_MULTISAMPLEBUFFERS, 0)
screen = pg.display.set_mode((1200, 600))

pg.display.set_caption("gfx/Race Works")
icon = pg.image.load("gfx/RaceWorksIcon.png")
pg.display.set_icon(icon)

font = pg.font.SysFont('century', 18)
CLOCK = pg.time.Clock()

render_all = True
track_name = "FlashPoint Raceway Short L"
gen_counter = 0
cp_list = [(-585, 480), (-450, 480), (-230, 480), (150, -465), (175, -455), (270, -415), (410, -370), (1200, -600)]

n_cars = 0

grid = []
for x in range(n_cars):
    grid.append(Car())
    
#best_car = grid[0]

screen.fill((96, 96, 96))
track = pg.image.load(f"gfx/{track_name} Mask.png")
track_mask = pg.mask.from_surface(track)
Car.set_track_mask(track_mask)
screen.blit(track, (0, 0))
pg.display.update()

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
        pg.draw.circle(screen, (0, 0, 0), (int(x), int(y)), 1, 1)
        if mask.get_at((int(x), int(y))) == 1:
            break
        x += cos_angle
        y -= sin_angle
    
    pg.draw.circle(screen, (0, 0, 0), (604, 486)), 1, 1)
    return math.sqrt((int(x) - start_x) ** 2 + (int(y) - start_y) ** 2)

running = True
while running:
    start_3 = time.time()

    running_cars = n_cars
    game_tick = 0
    
    while running_cars > 0 and game_tick < 1000 and running:
        #CLOCK.tick(60)
        game_tick += 1

        for event in pg.event.get():
            if event.type == pg.quit:
                running = False


        screen.fill((96, 96, 96))
        track = pg.image.load(f"gfx/{track_name} Mask.png")
        track_mask = pg.mask.from_surface(track)
        screen.blit(track, (0, 0))
        screen.blit(font.render(f"{game_tick} / {gen_counter}", False, (0, 0, 0)), (550, 410))
        screen.blit(font.render(str(len(grid)), False, (0, 0, 0)), (550, 440))

        line_tracer(0, 604, 486, track_mask)

        for car in grid:
            if not car.crash:
                car.update_car()
                if car.crash:
                    running_cars -= 1
                if render_all:
                    screen.blit(car.image, (int(car.pos_x), int(car.pos_y)))

        if not render_all:
            screen.blit(best_car.image, (int(best_car.pos_x), int(best_car.pos_y)))

        pg.display.update()

        keys = pg.key.get_pressed()
        if keys[pg.K_ESCAPE]:
            running = False

    total_distance = 0
    for car in grid:
        car.gap_to_cp = distance_two_points(cp_list[car.points], (car.x, car.y))

    grid.sort(key=lambda car: (car.distance), reverse=True)
    #Car.set_max_distance(grid[0].distance)
    #print(f"Gen {gen_counter}: Best car ran {grid[0].distance} metres")

    grid.sort(key=lambda car: (car.fitness()), reverse=True)

    for car in grid:
        total_distance += car.distance

    new_grid = []
    while len(new_grid) < n_cars:
        new_grid.append(Car())
    
    grid = new_grid[:n_cars]
    end_3 = time.time()
    #print(f"Gen {gen_counter}: Average of {total_distance/ n_cars} metres")# in {end_3 - start_3} seconds for {n_cars} cars")
    gen_counter += 1
    best_car = None
    print("")
    time.sleep(3)