import json

import pygame


class Spritesheet:
    def __init__(self, filename):
        self.filename = filename
        self.sprite_sheet = pygame.image.load(filename).convert()
        self.meta_data = self.filename.replace("png", "json")
        with open(self.meta_data) as file:
            self.data = json.load(file)

    def get_sprite(self, x, y, width, height):
        sprite  = pygame.Surface((width, height))
        sprite.set_colorkey((0, 0, 0))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, width, height))
        return sprite
    
    def load_sprite(self, name):
        sprite = self.data["frames"][name]["frame"]
        
        return self.get_sprite(sprite["x"], sprite["y"], sprite["w"],sprite["h"])  