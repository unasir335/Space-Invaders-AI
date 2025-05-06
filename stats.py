import os

class Stats:
    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.difficulty_manager = None
        self.reset_stats()
        self.last_ships_left = self.ships_left
        self.score = 0
        self.level = 0
        self.highscore = self.load_high_score()

    def __del__(self): 
        self.save_high_score()    

    def set_difficulty_manager(self, difficulty_manager):
        """Set the difficulty manager for performance tracking"""
        self.difficulty_manager = difficulty_manager

    def load_high_score(self): 
        try:
            with open("highscore.txt", "r") as f:
                return int(f.read())    
        except:
                return 0
        
    def save_high_score(self):
        try:
            with open("highscore.txt", "w+") as f:
                f.write(str(round(self.highscore, -1)))  # 314.15 --> 310,  (0) --> 314
        except:
            print("highscore.txt not found...")

    def get_score(self): return self.score
    def get_highscore(self): return self.highscore
    def get_level(self): return self.level
    def get_ships_left(self): return int(self.ships_left)  # Ensure this is an integer
    
    def reset_stats(self): 
        # Use ship_limit from settings, pass from settings to difficulty
        if hasattr(self.settings, 'ship_limit'):
            self.ships_left = int(self.settings.ship_limit)  # Ensure this is an integer
        else:
            self.ships_left = 3  # Default ship/lives
        
    def level_up(self): 
        self.level += 1
        print("leveling up: level is now ", self.level)
        
        # Notify difficulty manager of level completion
        if self.difficulty_manager:
            self.difficulty_manager.on_level_complete()
            
    def alien_hit(self, alien):
        self.score += alien.points
        self.highscore = max(self.score, self.highscore)
            
    def ship_hit(self):
        self.ships_left -= 1
        n = self.ships_left
        print(f'SHIP HIT!', end=' ')
        if self.last_ships_left != self.ships_left:
            print(f'{self.ships_left} ship{"s" if n != 1 else ""} left')
            self.last_ships_left = self.ships_left
            
        # Notify difficulty manager of ship hit
        if self.difficulty_manager:
            self.difficulty_manager.on_ship_hit()