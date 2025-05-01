import pygame as pg

import alien
from vector import Vector
from pygame.sprite import Sprite, Group
from copy import copy
from random import randint
from sound import Sound


class Lasers:
    def __init__(self, game, owner):
        self.game = game
        self.stats = game.stats
        self.sound = game.sound
        self.owner = owner
        self.alien_fleet = game.alien_fleet
        self.lasers = Group()
        print('owner is ', self.owner, 'type is: ', type(self.owner))
        print('type is alien.AlienFleet is: ', type(owner) is alien.AlienFleet)

    def add(self, laser): self.lasers.add(laser)
    def empty(self): self.lasers.empty()
    def fire(self): 
        new_laser = Laser(self.game)
        self.lasers.add(new_laser)
        snd = self.sound
        snd.play_fire_phaser() if type(self.owner) is alien.AlienFleet else snd.play_fire_photon()

    def update(self):
        for laser in self.lasers.copy():
            if laser.rect.bottom <= 0 or laser.rect.top >= self.game.screen.get_rect().bottom: 
                self.lasers.remove(laser)

        collisions = pg.sprite.groupcollide(self.alien_fleet.fleet, self.lasers, False, True)
        for alien in collisions: 
          if not alien.dying: alien.hit()

        if self.alien_fleet.length() == 0:  
            self.stats.level_up()
            self.game.restart()
            
        for laser in self.lasers:
            laser.update()

    def draw(self):
        for laser in self.lasers:
            laser.draw()


class Laser(Sprite):
    def __init__(self, game):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.w, self.h = self.settings.laser_width, self.settings.laser_height
        self.ship = game.ship

        self.rect = pg.Rect(0, 0, self.w, self.h)
        self.center = copy(self.ship.center)
        tu = 50, 255
        self.color = randint(*tu), randint(*tu), randint(*tu)
        self.v = Vector(0, -1) * self.settings.laser_speed_factor

    def update(self):
        self.center += self.v
        self.rect.x, self.rect.y = self.center.x, self.center.y

    def draw(self): pg.draw.rect(self.screen, color=self.color, rect=self.rect)


class BossLaser(Sprite):
    def __init__(self, game, boss):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        
        # Much larger laser for the boss - 5x regular width, 3x height
        self.w, self.h = self.settings.laser_width * 5, self.settings.laser_height * 3
        
        # Create the rect and position it at the bottom center of the boss
        self.rect = pg.Rect(0, 0, self.w, self.h)
        boss_center_x = boss.rect.centerx
        boss_bottom = boss.rect.bottom
        self.center = Vector(boss_center_x, boss_bottom)
        
        # Boss laser is bright red-orange for high visibility
        self.color = (255, 50, 0)
        
        # Boss laser moves downward but at only 70% of player laser speed
        self.v = Vector(0, 1) * self.settings.laser_speed_factor * 0.7

    def update(self):
        self.center += self.v
        self.rect.x, self.rect.y = self.center.x, self.center.y

        # Check for collision with player ship
        if self.rect.colliderect(self.game.ship.rect) and not self.game.ship.is_dying():
            self.game.ship.hit()
            self.kill()  # Remove the laser after hit

    def draw(self): 
        # Draw the main laser beam
        pg.draw.rect(self.screen, color=self.color, rect=self.rect)
        
        # Draw a stronger, more visible glowing effect
        glow_rect1 = self.rect.inflate(6, 6)
        pg.draw.rect(self.screen, color=(255, 150, 0), rect=glow_rect1, width=3)
        
        # Add a second outer glow for even more visibility
        glow_rect2 = self.rect.inflate(12, 12)
        pg.draw.rect(self.screen, color=(255, 200, 0), rect=glow_rect2, width=2)