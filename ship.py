import pygame as pg
from vector import Vector
from timer import Timer
from pygame.sprite import Sprite, Group
from sound import Sound


class Ship(Sprite):
  exploding_images = [pg.image.load(f'images/rainbow_explode{n}.png') for n in range(8)]
  images = [pg.image.load(f'images/ship.bmp') for n in range(1)]
   
  def __init__(self, game):
    super().__init__()
    self.game = game
    self.screen = game.screen
    self.settings = game.settings
    self.sound = game.sound
    self.alien_fleet = None
    self.lasers = None
    self.stats = game.stats
    self.image = pg.image.load('images/ship.bmp')

    self.rect = self.image.get_rect()
    self.screen_rect = self.screen.get_rect()
    self.center_bottom()
    self.v = Vector()
    self.firing = False
    self.frames = 0
    
    # Fire rate limiting - get from settings if available
    if hasattr(self.settings, 'ship_fire_rate'):
      self.fire_cooldown = self.settings.ship_fire_rate
    else:
      self.fire_cooldown = 25  # Default fire rate (higher = slower)
      
    self.cooldown_timer = 0  # Current cooldown timer
    
    self.exploding_timer = Timer(image_list=Ship.exploding_images, delay=200, is_loop=False)
    self.normal_timer = Timer(image_list=Ship.images, delay=1000, is_loop=True)
    self.timer = self.normal_timer
    self.dying = False

  def set_alien_fleet(self, alien_fleet): self.alien_fleet = alien_fleet
  def set_lasers(self, lasers): self.lasers = lasers
  def center_bottom(self): 
    self.rect.centerx = self.screen_rect.centerx
    self.rect.bottom = self.screen_rect.bottom
    self.center = Vector(self.rect.centerx, self.rect.centery)
  def reset_timer(self): 
    self.exploding_timer.reset()
    self.normal_timer.reset()
    self.timer = self.normal_timer
  def toggle_firing(self): self.firing = not self.firing 
  def hit(self):  
    self.timer = self.exploding_timer
    self.dying = True
    self.sound.play_ship_explosion()
  def is_dying(self): return self.dying  
  def die(self):
    self.stats.ship_hit()
    if self.stats.ships_left == 0:
      self.game.finished = True
    self.dying = False
    self.game.restart()

  def moving(self, vector): self.v = vector
  def inc_add(self, other): self.v += other
  def clamp(self):
    rw, rh = self.rect.width, self.rect.height
    srw, srb = self.screen_rect.width, self.screen_rect.bottom
    x, y = self.center.x, self.center.y

    self.center.x = min(max(x, rw/2), srw - rw/2)
    self.center.y = min(max(y, rh/2), srb - rh/2)

  def update(self):
    # Update fire rate from settings if they've changed
    if hasattr(self.settings, 'ship_fire_rate'):
      self.fire_cooldown = self.settings.ship_fire_rate
      
    if self.dying and self.timer.is_expired():
      self.die()
    self.center += self.v * self.settings.ship_speed_factor
    self.clamp()
    self.rect.centerx, self.rect.centery = self.center.x, self.center.y
    
    # Handle fire cooldown
    if self.cooldown_timer > 0:
      self.cooldown_timer -= 1
    
    # Control firing rate - requires cooldown to be done
    if self.firing and self.cooldown_timer <= 0:
      self.lasers.fire()
      self.cooldown_timer = self.fire_cooldown
      
      # Track shots fired for difficulty adjustment
      if hasattr(self.game, 'difficulty_manager'):
        self.game.difficulty_manager.shot_fired()
      
    self.frames += 1

  def draw(self):
    image = self.timer.image()
    rect = image.get_rect()
    rect.x, rect.y = self.rect.x, self.rect.y
    self.screen.blit(image, rect)