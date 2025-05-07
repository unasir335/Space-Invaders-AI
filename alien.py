import pygame as pg
from vector import Vector
from pygame.sprite import Sprite, Group
from timer import Timer
from laser import Laser, BossLaser
from sound import Sound
from random import randint, choice, random
import numpy as np


class AlienFleet:
    alien_exploding_images = [pg.image.load(f'images/rainbow_explode{n}.png') for n in range(8)]
    alien_images0 = [pg.transform.rotozoom(pg.image.load(f'images/AlienOne{n}.png'), 0, 1.1) for n in range(3)]
    alien_images1 = [pg.transform.rotozoom(pg.image.load(f'images/AlienTwo{n}.png'), 0, 1) for n in range(2)]
    alien_images2 = [pg.transform.rotozoom(pg.image.load(f'images/AlienThree{n}.png'), 0, 1) for n in range(3)]

    alien_images = [alien_images0, alien_images1, alien_images2]
    
    ufo_imgs = [pg.transform.rotozoom(pg.image.load(f'images/alienBoss{n}.png'), 0, 1.3) for n in range(2)]
    alien_images.append(ufo_imgs)
    alien_points = [20, 40, 10, 100]

    def __init__(self, game, v=Vector(1, 0)):
        self.game = game
        self.settings = game.settings
        self.screen = self.game.screen
        self.sound = game.sound
        self.screen_rect = self.screen.get_rect()
        self.v = v
        self.aliens_killed = 0            # Track killed aliens
        self.boss_spawned = False         # Track if boss is spawned
        self.lasers = None                # Will be set via set_lasers method
        
        # Create a temp alien to get dimensions, but don't add it to the fleet yet
        temp_alien = Alien(self.game, sound=self.sound, alien_index=0, image_list=AlienFleet.alien_images)
        self.alien_h, self.alien_w = temp_alien.rect.height, temp_alien.rect.width
        
        self.fleet = Group()
        
        # Set ship reference AFTER the ship is created
        if hasattr(self.game, 'ship'):
            self.ship = self.game.ship
        else:
            # Will be set later via set_ship method
            self.ship = None
            
        self.create_fleet()

    def create_fleet(self):
        """Create a fleet of aliens based on difficulty settings"""
        # Get difficulty parameters
        if hasattr(self.game, 'settings'):
            rows = self.game.settings.alien_rows if hasattr(self.game.settings, 'alien_rows') else 2
            cols = self.game.settings.alien_cols if hasattr(self.game.settings, 'alien_cols') else 6
        else:
            # Default fallback values
            rows = 2
            cols = 6
            
        # Use AI-based spawn pattern if difficulty manager is available
        if hasattr(self.game, 'difficulty_manager'):
            # Get spawn pattern from A* algorithm
            spawn_pattern = self.game.difficulty_manager.a_star_placement(rows, cols)
            
            # Create aliens based on the pattern
            for row in range(rows):
                for col in range(cols):
                    if spawn_pattern[row, col] > 0:  # If there should be an alien here
                        alien_type = spawn_pattern[row, col] - 1  # Convert from 1/2 to 0/1
                        self.create_alien(row=row, col=col, alien_type=min(alien_type, 2))
        else:
            # Fall back to original method if no difficulty manager
            for row in range(rows):
                for col in range(cols):
                    self.create_alien(row=row, col=col)

    def set_lasers(self, lasers):
        self.lasers = lasers

    def toggle_firing(self): 
        self.firing = not self.firing

    def set_ship(self, ship): 
        self.ship = ship
        
    def create_alien(self, row, col, alien_type=None):
        x = self.alien_w * (1.2 * col + 1)
        y = self.alien_h * (0.4 * row + 1)
        images = AlienFleet.alien_images
        
        # Only create regular aliens (types 0-2) in the initial fleet
        # Never spawn boss (type 3) in the initial fleet
        if alien_type is None:
            alien_index = min(row // 2, 2)  # Cap at 2 to avoid boss (type 3)
        else:
            # Use the alien type from the spawn pattern
            alien_index = min(alien_type, 2)  # Still cap at 2 to avoid boss
        
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
        # Get rows from settings if available
        if hasattr(self.settings, 'alien_rows'):
            return self.settings.alien_rows
        return 2  # Default to 2 rows

    def length(self): 
        return len(self.fleet.sprites())

    def change_v(self, v):
        for alien in self.fleet.sprites():
            # If boss, apply boss speed multiplier
            if hasattr(alien, 'is_boss') and alien.is_boss:
                # Get boss speed from settings if available
                boss_speed = 2.5
                if hasattr(self.game, 'settings') and hasattr(self.game.settings, 'boss_speed'):
                    boss_speed = self.game.settings.boss_speed
                alien.change_v(Vector(v.x * boss_speed, v.y))
            # If back row alien, maintain the higher speed
            elif hasattr(alien, 'is_back_row') and alien.is_back_row:
                alien.change_v(Vector(v.x * 1.2, v.y))
            else:
                # For regular aliens
                alien.change_v(v)

    def check_bottom(self): 
        for alien in self.fleet.sprites():
            if alien.check_bottom():
                if self.ship:
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
        
        # Update difficulty manager if available
        if hasattr(self.game, 'difficulty_manager'):
            self.game.difficulty_manager.update_performance_metrics(alien_killed=True)
            
        # Get boss spawn threshold from settings
        boss_threshold = 15
        boss_count = 1
        
        if hasattr(self.game, 'settings'):
            if hasattr(self.game.settings, 'boss_spawn_threshold'):
                boss_threshold = self.game.settings.boss_spawn_threshold
            if hasattr(self.game.settings, 'boss_count'):
                boss_count = self.game.settings.boss_count
        
        # Spawn boss after threshold kills if not already spawned
        if self.aliens_killed >= boss_threshold and not self.boss_spawned:
            self.boss_spawned = True  # Set this first to prevent multiple spawns
            
            # Spawn multiple bosses based on difficulty
            for i in range(boss_count):
                position_index = i % 3  # Use different positions for multiple bosses
                self.spawn_boss(position_index)
    
    def spawn_boss(self, position_index=0):
        """Spawn a single fast boss alien based on difficulty settings"""
        # Make sure we have lasers set before spawning boss
        if self.lasers is None:
            print("Warning: No lasers set for AlienFleet, boss won't be able to fire")
            return
            
        # Play a sound to signal boss arrival
        self.sound.play_ufo()
        
        # Get boss settings from difficulty manager if available
        boss_speed = 2.5
        boss_fire_rate = 120
        
        if hasattr(self.game, 'settings'):
            if hasattr(self.game.settings, 'boss_speed'):
                boss_speed = self.game.settings.boss_speed
            if hasattr(self.game.settings, 'boss_fire_rate'):
                boss_fire_rate = self.game.settings.boss_fire_rate
        
        # Position the boss based on how many we're spawning
        # If multiple bosses, space them out
        width = self.screen_rect.width
        positions = [
            (width * 0.25, self.alien_h * 0.5),  # Left
            (width * 0.5, self.alien_h * 0.5),   # Center
            (width * 0.75, self.alien_h * 0.5)   # Right
        ]
        
        # Use the provided position index or default to center
        pos_idx = min(position_index, len(positions)-1)
        x, y = positions[pos_idx]
        
        # Boss moves faster than regular aliens based on difficulty
        boss_v = Vector(self.v.x * boss_speed, 0)
        
        boss = Alien(game=self.game, sound=self.sound, alien_index=3, 
                    ul=(x, y), v=boss_v, image_list=AlienFleet.alien_images,
                    is_boss=True)
                    
        # Set up the boss laser capabilities
        boss.can_shoot = True
        boss.fire_cooldown = boss_fire_rate  # Frames between boss shots
        boss.cooldown_timer = boss_fire_rate // 2  # Start with a short delay before first shot
        
        self.fleet.add(boss)

    def update(self):
        delta_s = Vector(0, 0)    # don't change y position in general
        if self.check_edges():
            self.v.x *= -1
            self.change_v(self.v)
            delta_s = Vector(0, self.settings.fleet_drop_speed)
        
        if self.ship and (pg.sprite.spritecollideany(self.ship, self.fleet) or self.check_bottom()):
            if not self.ship.is_dying(): 
                self.ship.hit()
                
                # Update difficulty manager when ship is hit
                if hasattr(self.game, 'difficulty_manager'):
                    self.game.difficulty_manager.update_performance_metrics(ship_hit=True)
        
        # Skip boss laser firing if lasers are not set
        if self.lasers is None:
            # Update aliens without firing
            for alien in self.fleet.sprites():
                alien.update(delta_s=delta_s)
            return
        
        # Normal update with boss firing
        for alien in self.fleet.sprites():
            alien.update(delta_s=delta_s)
            
            # Let the boss fire its special laser
            if hasattr(alien, 'is_boss') and alien.is_boss and hasattr(alien, 'can_shoot') and alien.can_shoot:
                if hasattr(alien, 'cooldown_timer'):
                    if alien.cooldown_timer <= 0:
                        self.fire_boss_laser(alien)
                        alien.cooldown_timer = alien.fire_cooldown
                    else:
                        alien.cooldown_timer -= 1
                    
    def fire_boss_laser(self, boss):
        """Fire a special thick laser from the boss"""
        # Skip if no lasers set
        if self.lasers is None:
            return
            
        laser = BossLaser(self.game, boss)
        self.lasers.add(laser)
        self.sound.play_fire_phaser()

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
        
        # Boss laser attack properties
        self.can_shoot = False
        self.fire_cooldown = 0
        self.cooldown_timer = 0

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
        
        # Notify the fleet about the kill
        self.game.alien_fleet.alien_killed()

    def update(self, delta_s=Vector(0, 0)):
        if self.dying and self.timer.is_expired():
            self.kill()
        self.ul += delta_s
        
        # Get the current alien speed factor (with a hard cap for safety)
        speed_factor = min(self.settings.alien_speed_factor, 1.8)  # Cap at 1.8x to prevent excessive speed
        
        # Apply speed factor with a safe maximum velocity
        velocity = self.v * speed_factor
        max_speed = 2.5  # Maximum allowed speed in pixels per frame
        
        # Cap the velocity components if they exceed the max speed
        if abs(velocity.x) > max_speed:
            velocity.x = max_speed if velocity.x > 0 else -max_speed
        if abs(velocity.y) > max_speed:
            velocity.y = max_speed if velocity.y > 0 else -max_speed
            
        self.ul += velocity
        self.rect.x, self.rect.y = self.ul.x, self.ul.y

    def draw(self):  
        image = self.timer.image()
        rect = image.get_rect()
        rect.x, rect.y = self.rect.x, self.rect.y
        self.screen.blit(image, rect)