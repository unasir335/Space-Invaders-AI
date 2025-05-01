import pygame as pg
from vector import Vector
from pygame.sprite import Sprite, Group
from timer import Timer
from laser import Laser
from sound import Sound
from random import randint, choice, random


class AlienFleet:
    alien_exploding_images = [pg.image.load(f'images/rainbow_explode{n}.png') for n in range(8)]
    alien_images0 = [pg.transform.rotozoom(pg.image.load(f'images/AlienOne{n}.png'), 0, 1.1) for n in range(3)]
    alien_images1 = [pg.transform.rotozoom(pg.image.load(f'images/AlienTwo{n}.png'), 0, 1) for n in range(2)]
    alien_images2 = [pg.transform.rotozoom(pg.image.load(f'images/AlienThree{n}.png'), 0, 1) for n in range(3)]

    alien_images = [alien_images0, alien_images1, alien_images2]
    
    ufo_imgs = [pg.transform.rotozoom(pg.image.load(f'images/alienBoss{n}.png'), 0, 1.3) for n in range(2)]
    alien_images.append(ufo_imgs)
    alien_points = [40, 20, 10, 100]

    def __init__(self, game, v=Vector(1, 0)):
        self.game = game
        self.ship = self.game.ship
        self.settings = game.settings
        self.screen = self.game.screen
        self.sound = game.sound
        self.screen_rect = self.screen.get_rect()
        self.v = v
        self.aliens_killed = 0            # Track killed aliens
        self.boss_spawned = False         # Track if boss is spawned
        alien = Alien(self.game, sound=self.sound, alien_index=0, image_list=AlienFleet.alien_images)
        self.alien_h, self.alien_w = alien.rect.height, alien.rect.width
        self.fleet = Group()
        self.create_fleet()

    def create_fleet(self):
        n_cols = self.get_number_cols(alien_width=self.alien_w)
        n_rows = self.get_number_rows(ship_height=self.ship.rect.height,
                                      alien_height=self.alien_h)
        for row in range(n_rows):
            for col in range(n_cols):
                self.create_alien(row=row, col=col)

    def set_lasers(self, lasers):
        self.lasers = lasers

    def toggle_firing(self): 
        self.firing = not self.firing

    def set_ship(self, ship): 
        self.ship = ship
        
    def create_alien(self, row, col):
        x = self.alien_w * (1.2 * col + 1)
        y = self.alien_h * (0.4 * row + 1)
        images = AlienFleet.alien_images
        
        # Only create regular aliens (types 0-2) in the initial fleet
        # Never spawn boss (type 3) in the initial fleet
        alien_index = min(row // 2, 2)  # Cap at 2 to avoid boss (type 3)
        
        # Last row gets slightly different movement
        if row == 0:
            # Make the back row move at a slightly different rate
            movement_vector = Vector(self.v.x * 1.2, self.v.y)
            is_back_row = True
        else:
            # All other aliens use the standard fleet movement
            movement_vector = Vector(self.v.x, self.v.y)
            is_back_row = False
            
        alien = Alien(game=self.game, sound=self.sound, alien_index=alien_index, 
                     ul=(x, y), v=movement_vector, image_list=images, is_back_row=is_back_row)
        self.fleet.add(alien)

    def empty(self): 
        self.fleet.empty()
        self.aliens_killed = 0
        self.boss_spawned = False
        
    def get_number_cols(self, alien_width):
        spacex = self.settings.screen_width - 2 * alien_width
        return int(spacex / (1 * alien_width))

    def get_number_rows(self, ship_height, alien_height):
        spacey = self.settings.screen_height - 2 * alien_height - ship_height
        return int(spacey / (0.5 * alien_height))

    def length(self): 
        return len(self.fleet.sprites())

    def change_v(self, v):
        for alien in self.fleet.sprites():
            # Preserve the relative speed of each alien - regular aliens
            # If back row alien (special case), maintain the higher speed
            if alien.is_back_row:
                alien.change_v(Vector(v.x * 1.2, v.y))
            # If boss alien, it has its own unique speed
            elif alien.alien_index == 3:
                alien.change_v(Vector(v.x * 2.5, v.y))  # Boss moves faster
            else:
                alien.change_v(v)

    def check_bottom(self): 
        for alien in self.fleet.sprites():
            if alien.check_bottom():
                self.ship.hit()
                break
      
    def check_edges(self): 
        for alien in self.fleet.sprites():
            if alien.check_edges(): 
                return True
        return False
    
    def alien_killed(self):
        """Track alien kills and spawn boss if threshold reached"""
        self.aliens_killed += 1
        
        # Spawn boss after 15 kills if not already spawned
        if self.aliens_killed >= 15 and not self.boss_spawned:
            self.spawn_boss()
    
    def spawn_boss(self):
        """Spawn a single fast boss alien at the top of the screen"""
        self.boss_spawned = True
        
        # Play a sound to signal boss arrival
        self.sound.play_ufo()
        
        # boss spawn position
        x = self.screen_rect.centerx
        y = self.alien_h * 0.5
        
        # Boss move base movemenmt - different from regular aliens
        boss_v = Vector(self.v.x * 2.5, 0)
        
        boss = Alien(game=self.game, sound=self.sound, alien_index=3, 
                    ul=(x, y), v=boss_v, image_list=AlienFleet.alien_images,
                    is_boss=True)
        self.fleet.add(boss)

    def update(self):
        delta_s = Vector(0, 0)    # don't change y position in general
        if self.check_edges():
            self.v.x *= -1
            self.change_v(self.v)
            delta_s = Vector(0, self.settings.fleet_drop_speed)
        if pg.sprite.spritecollideany(self.ship, self.fleet) or self.check_bottom():
            if not self.ship.is_dying(): 
                self.ship.hit() 
        for alien in self.fleet.sprites():
            alien.update(delta_s=delta_s)

    def draw(self):
        for alien in self.fleet.sprites():
            alien.draw()


class Alien(Sprite):
    def __init__(self, game, image_list, alien_index, sound, start_index=0, ul=(0, 100), v=Vector(1, 0),
                 points=1211, is_boss=False, is_back_row=False):
        super().__init__()
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.sound = sound
        self.points = AlienFleet.alien_points[alien_index]
        self.stats = game.stats

        self.lasers = None
        self.firing = True

        self.alien_index = alien_index
        self.is_boss = is_boss
        self.is_back_row = is_back_row

        self.image = pg.image.load('images/alienOne0.png')
        self.screen_rect = self.screen.get_rect()
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = ul
        self.ul = Vector(ul[0], ul[1])   # position
        self.v = v                       # velocity
        self.image_list = image_list
        self.exploding_timer = Timer(image_list=AlienFleet.alien_exploding_images, delay=200, 
                                     start_index=start_index, is_loop=False)

        self.normal_timer = Timer(image_list=AlienFleet.alien_images[alien_index], delay=1000, is_loop=True)
        self.timer = self.normal_timer
        self.dying = False

    def change_v(self, v): 
        self.v = v
        
    def check_bottom(self): 
        return self.rect.bottom >= self.screen_rect.bottom
        
    def check_edges(self):
        r = self.rect
        return r.right >= self.screen_rect.right or r.left <= 0

    def hit(self): 
        self.stats.alien_hit(alien=self)
        self.timer = self.exploding_timer
        self.sound.play_alien_explosion()
        self.dying = True
        
        # Notify on screen that alien feet has been killed
        self.game.alien_fleet.alien_killed()

    def update(self, delta_s=Vector(0, 0)):
        if self.dying and self.timer.is_expired():
            self.kill()
        self.ul += delta_s
        self.ul += self.v * self.settings.alien_speed_factor
        self.rect.x, self.rect.y = self.ul.x, self.ul.y

    def draw(self):  
        image = self.timer.image()
        rect = image.get_rect()
        rect.x, rect.y = self.rect.x, self.rect.y
        self.screen.blit(image, rect)