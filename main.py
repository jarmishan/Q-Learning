import sys
import json

import pygame
import numpy

from agent import Agent
from spritesheet import Spritesheet

pygame.init()

WIDTH, HEIGHT = 640, 704
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()



images = Spritesheet("assets/Q-learning spritesheet.png")

class Game:
    def __init__(self):
        self.crate = pygame.transform.scale(images.load_sprite("crate.png"), (32, 32))
        self.wall = pygame.transform.scale(images.load_sprite("wall.png"), (32, 32))
        self.robot = pygame.transform.scale(images.load_sprite("robot.png"), (32, 32))
        self.drop_zone  = pygame.transform.scale(images.load_sprite("drop off.png"), (32, 32))
        self.slider_ball = images.load_sprite("slider ball.png")
        self.slider_bar = images.load_sprite("slider bar.png")

        self.button = [
            images.load_sprite("button 1.png"), 
            images.load_sprite("button 2.png")
        ]

        self.displays = [
            images.load_sprite("display.png"), 
            images.load_sprite("display 2.png"), 
            images.load_sprite("display 3.png")
         ]

        self.objects = [
            pygame.transform.scale(self.crate, (16, 16)), 
            pygame.transform.scale(self.wall, (16, 16)), 
            pygame.transform.scale(images.load_sprite("robot 1.png"), (16, 16)), 
            pygame.transform.scale(self.drop_zone, (16, 16))
        ]

        self.display = self.displays[0]

        self.crate_x, self.crate_y = 800, 800
        self.robot_x, self.robot_y = 800, 800
        self.drop_x, self.drop_y = 800, 800
        self.ball_x = 20

        self.map = numpy.full((20, 20), -1)
        self.walls = []
        
        self.training = False
        self.trained = False
        self.picked_up = False

        self.draw_index = 0
        self.path_index = 0
        self.square_index = 0
        self.counter = 0


    def get_index(self, x, y):
        return int(y / 32), int(x / 32)


    def get_square(self):
        square = self.get_index(self.mx, self.my)[::-1]
        return square[0] * 32 + 1 ,square[1] * 32 + 1


    def is_empty(self, pos):
        return pos not in ((self.drop_x, self.drop_y), (self.robot_x, self.robot_y), (self.crate_x, self.crate_y)) and (self.wall, pos) not in self.walls


    def is_valid_map(self):
        try:
            self.end, self.start
            return all([True  if condition in self.map else False for condition in [100, -1]])
        except AttributeError:
            return False
        
     
    def draw_grid(self):
        for length in range(21):
            pygame.draw.line(screen, (0, 0, 0), (0, length * 32), (WIDTH, length * 32))
            pygame.draw.line(screen, (0, 0, 0), (length * 32, 0), (length * 32, WIDTH))

  
    def train_agent(self):
        self.agent = Agent(self.map, self.start, self.end)
        self.agent.train()
        self.final_path = self.agent.get_final_path()
        
        if self.final_path:
            self.final_path.pop()

        else:
            self.__init__()
            self.display = self.displays[1]
            
              
    def set_direction(self, square_x, square_y, robot):
        if self.robot_x > square_x:
            self.robot = pygame.transform.rotate(robot, 270)
            
        elif self.robot_x < square_x:
            self.robot = pygame.transform.rotate(robot, 90)

        elif self.robot_y > square_y:
            self.robot = pygame.transform.rotate(robot, -180)

        elif self.robot_y < square_y:
            self.robot = pygame.transform.rotate(robot, 0)


    def get_speed(self):
        screen.blit(self.slider_bar, (20, 656))
        if self.mx > 20 and self.mx < 600 and self.my > 640 and pygame.mouse.get_pressed(5)[0]:
            self.ball_x = self.mx
        
        screen.blit(self.slider_ball, (self.ball_x, 656))
        return 1 + (self.ball_x - 19) // 20


    def show_final_path(self):
        square = self.final_path[self.square_index]
        square_x, square_y = square[1] * 32, square[0] * 32

        if self.get_index(self.robot_x, self.robot_y) == square and self.final_path.index(square) < len(self.final_path) - 1:
            self.square_index += 1
        
        if self.final_path.index(square) >= self.final_path.index(self.goal):
            self.crate_x, self.crate_y = 800, 800
            self.picked_up = True
        
        if self.picked_up:
            self.set_direction(square_x, square_y, pygame.transform.scale(images.load_sprite("robot box.png"), (32, 54)))
        else:
            self.set_direction(square_x, square_y, pygame.transform.scale(images.load_sprite("robot.png"), (32, 32))) 

        pygame.time.delay(300)
        self.robot_x, self.robot_y = square_x, square_y

    def show_path(self):
        if self.counter % self.get_speed() == 0:
            square = self.agent.paths[self.path_index][self.square_index]
            square_x, square_y = square[1] * 32, square[0] * 32

            self.set_direction(square_x, square_y, pygame.transform.scale(images.load_sprite("robot.png"), (32, 32))) 
            self.robot_x, self.robot_y = square_x, square_y

            if not self.agent.paths[self.path_index] == self.agent.paths[-1]:
                if square == self.agent.paths[self.path_index][-1]:
                    self.path_index += 1
                    self.square_index = 0
                
                elif self.get_index(self.robot_x, self.robot_y) == square and self.agent.paths[self.path_index].index(square) < len(self.agent.paths[self.path_index]) - 1:
                    self.square_index += 1  
            else:
                self.trained = True
                self.square_index = 0
                self.show_final_path()
                
    def draw_map(self):
        for wall in self.walls:
            screen.blit(wall[0], wall[1])

        screen.blit(self.crate, (self.crate_x, self.crate_y))
        screen.blit(self.drop_zone, (self.drop_x, self.drop_y))
        screen.blit(self.robot, (self.robot_x, self.robot_y))

        if not self.training:
            screen.blit(self.button[0], (10, 640))
            screen.blit(self.display, (220, 640))


    def button_pressed(self):
        button_rect = pygame.Rect(10, 640, 180, 64)
        if button_rect.collidepoint(self.mx, self.my) and pygame.mouse.get_pressed(5)[0]:

            pygame.draw.rect(screen, (45, 45, 45), (0, 640, 200, 160))
            screen.blit(self.button[1], (10, 640))
            pygame.display.update()

            if self.is_valid_map():
                pygame.time.delay(100)
                screen.fill((255, 255, 255))
                pygame.draw.rect(screen, (45, 45, 45), (0, 640, WIDTH, 160))

                self.display = self.displays[2]
                self.draw_map()
                self.draw_grid()

                pygame.display.update()

                self.training = True
                self.train_agent()
                
            else:
                self.display = self.displays[1]


    def create_map(self):
        self.draw_grid()
        if not self.training:
            screen.blit(self.objects[self.draw_index % len(self.objects)], (self.mx + 8, self.my - 12))

        if pygame.mouse.get_pressed(5)[2]:
            object = (self.wall, self.get_square())
            if object in self.walls:
                
                self.walls.remove(object)
                self.map[self.get_index(object[1][0], object[1][1])] = -1
      
        if self.my < 640 and  self.is_empty(self.get_square()) and pygame.mouse.get_pressed(5)[0]:
            if self.draw_index % len(self.objects) == 0:
                self.crate_x, self.crate_y = self.get_square()

                self.map[self.map == 100] = -1
                self.goal = self.get_index(self.crate_x, self.crate_y)
                self.map[self.goal] = 100
                

            if self.draw_index % len(self.objects) == 1:
                object = (self.wall, self.get_square())

                self.walls.append(object)
                self.map[self.get_index(self.get_square()[0], self.get_square()[1])] = -100
            
        
            if self.draw_index % len(self.objects) == 2:
                self.robot_x, self.robot_y = self.get_square()
                self.start = self.get_index(self.robot_x, self.robot_y)


            if self.draw_index % len(self.objects) == 3:
                self.drop_x, self.drop_y = self.get_square()
                self.end = self.get_index(self.drop_x, self.drop_y)

        self.draw_map()
        self.button_pressed()
  
        screen.blit(self.objects[self.draw_index % len(self.objects)], (self.mx + 8, self.my - 12))
        
        
    def run(self):
        while True:
            self.mx, self.my = pygame.mouse.get_pos()

            screen.fill((255, 255, 255))
            pygame.draw.rect(screen, (45, 45, 45), (0, 640, WIDTH, 160))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    
                    pygame.quit()
                    sys.exit(0)
                    
                if event.type == pygame.MOUSEWHEEL:
                    if event.y < 0:
                        self.draw_index += 1
                    elif event.y > 0:
                        self.draw_index -= 1

            self.draw_map()
            if not self.training:
                self.create_map()

            elif not self.trained:
                self.counter += 1
                self.show_path()

            else:
                self.show_final_path()
            
            pygame.display.flip()
            clock.tick(60)

game = Game()
game.run()