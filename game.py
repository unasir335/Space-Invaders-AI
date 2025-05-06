import pygame as pg
from landing_page import LandingPage
from sys import exit
import game_functions as gf
from time import sleep
from stats import Stats
from scoreboard import Scoreboard
from laser import Lasers
from ship import Ship
from alien import AlienFleet
from settings import Settings
from sound import Sound
from ai_difficulty_manager import AIDifficultyManager


class Game:
    RED = (255, 0, 0)

    def __init__(self):
        pg.init()
        self.settings = Settings()
        self.screen = pg.display.set_mode((self.settings.screen_width,
                                           self.settings.screen_height))
        self.bg_color = self.settings.bg_color
        self.sound = Sound()
        
        # Frame counter for timing
        self.frames = 0
        
        # Initialize the AI difficulty manager - wait to apply
        self.difficulty_manager = AIDifficultyManager(game=self)
        
        # Create stats 
        self.stats = Stats(game=self)
        
        # Set difficulty manager in stats
        self.stats.set_difficulty_manager(self.difficulty_manager)
        
        # Create ship before scoreboard
        self.ship = Ship(game=self)
        
        # Create scoreboard after stats and ship
        self.sb = Scoreboard(game=self)
        
        # Create other game objects
        self.alien_fleet = AlienFleet(game=self)
        self.lasers = Lasers(game=self, owner=self.ship)
        
        #  Set the lasers for the alien fleet
        self.alien_fleet.set_lasers(self.lasers)
        
        pg.display.set_caption("Alien Invasion")
        
        # Setup connections between objects
        self.ship.set_alien_fleet(self.alien_fleet)
        self.ship.set_lasers(self.lasers)
        self.alien_fleet.set_ship(self.ship)
        
        # Flag to indicate when restart is needed
        self.need_restart = False
        
        # after init apply difficulty settings
        self.apply_difficulty_settings()

    def apply_difficulty_settings(self):
        # Apply difficulty manager settings here
        params = self.difficulty_manager.params
        
        # Apply settings to Ship
        self.settings.ship_limit = max(3, int(params['ship_lives']))  # Ensure at least 3 lives
        
        # Apply settings to Aliens
        self.settings.fleet_drop_speed = params['fleet_drop_speed']
        self.settings.alien_speed_factor = params['alien_speed']
        
        # Store other parameters that will be used during gameplay
        self.settings.alien_rows = int(params['alien_rows'])
        self.settings.alien_cols = int(params['alien_cols'])
        self.settings.boss_spawn_threshold = params['boss_spawn_threshold']
        self.settings.boss_speed = params['boss_speed']
        self.settings.boss_fire_rate = params['boss_fire_rate']
        self.settings.boss_count = int(params['boss_count'])
        self.settings.ship_fire_rate = params['ship_fire_rate']
        
        print(f"Applied difficulty settings: {self.difficulty_manager.DIFFICULTY_NAMES[self.difficulty_manager.current_difficulty]}")
        print(f"Ship lives: {self.settings.ship_limit}, Alien speed: {self.settings.alien_speed_factor}")

    def restart(self):
        if self.stats.ships_left == 0: 
            self.game_over()
            return
            
        print("restarting game")
        
        # Re-apply difficulty settings in case they've changed
        self.apply_difficulty_settings()
        
        while self.sound.busy():    # wait for explosion sound to finish
            pass
        self.lasers.empty()
        self.alien_fleet.empty()
        self.alien_fleet.create_fleet()
        self.ship.center_bottom()
        self.ship.reset_timer()
        self.draw()  # draw ship and alien after restart
        sleep(0.5)

    def update(self):
        # Increment frame counter
        self.frames += 1
        
        # Update difficulty manager
        self.difficulty_manager.update()
        
        # Update game components
        self.ship.update()
        self.alien_fleet.update()
        self.lasers.update()
        self.sb.update()
        
        # Re-apply difficulty settings periodically
        if self.frames % 60 == 0:  # Every second at 60fps
            self.apply_difficulty_settings()

    def draw(self):
        self.screen.fill(self.bg_color)
        self.ship.draw()
        self.alien_fleet.draw()
        self.lasers.draw()
        self.sb.draw()
        
        # Draw difficulty indicator
        self.difficulty_manager.draw()
        
        pg.display.flip()

    def play(self):
        self.finished = False
        self.sound.play_bg()
        clock = pg.time.Clock()  # Create a clock for framerate control
        
        while not self.finished:
            # Process events first
            gf.check_events(game=self)  # exits game if QUIT pressed
            
            # Check if restart is needed before updating
            if self.need_restart:
                print("Need restart detected, resetting flag")
                self.need_restart = False  # Reset the flag
                self.restart()  # Restart the game
                # Add a short delay to prevent multiple restarts
                pg.time.delay(300)
                continue  # Skip the rest of this iteration
            
            # Normal update and draw cycle
            self.update()
            self.draw()
            
            # Framerate control
            clock.tick(60)
        
        self.game_over()

    def game_over(self):
        # Notify difficulty manager of game over
        self.difficulty_manager.game_over()
        
        self.sound.play_game_over()
        print('\nGAME OVER!\n\n')
        exit()    # can ask to replay here instead of exiting the game

def main():
    g = Game()
    lp = LandingPage(game=g)
    lp.show()
    g.play()


if __name__ == '__main__':
    main()