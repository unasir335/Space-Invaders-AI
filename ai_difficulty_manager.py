import pygame as pg
import numpy as np
import os
from datetime import datetime
import random
import json
import time

class AIDifficultyManager:

    # AI Difficulty Manager
    # uses A* search algorithm to determine optimal difficulty settings
    
    # Difficulty levels
    NOVICE = 0
    EASY = 1
    MEDIUM = 2
    HARD = 3
    EXTREME = 4
    
    DIFFICULTY_NAMES = ["NOVICE", "EASY", "MEDIUM", "HARD", "EXTREME"]
    DIFFICULTY_COLORS = [
        (0, 255, 0),    # Green for NOVICE
        (150, 255, 0),  # Yellow-green for EASY
        (255, 255, 0),  # Yellow for MEDIUM
        (255, 150, 0),  # Orange for HARD
        (255, 0, 0)     # Red for EXTREME
    ]
    
    def __init__(self, game, initial_difficulty=MEDIUM):
        self.game = game
        self.screen = game.screen
        self.current_difficulty = initial_difficulty
        self.log_file = "difficulty_log.txt"
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Track stats for difficulty adjustment
        self.level_count = 0
        self.consecutive_easy_levels = 0
        self.last_level_time = time.time()
        self.recent_ship_hits = 0
        self.shots_fired = 0
        self.hits_landed = 0
        
        # baseline game parameters
        self.params = {
            'alien_rows': 2,
            'alien_cols': 4,
            'fleet_drop_speed': 0.4,
            'alien_speed': 0.4,
            'boss_spawn_threshold': 30,
            'boss_speed': 0.4,
            'boss_fire_rate': 120,
            'ship_lives': 3,  # Ensure at least 3 lives to prevent "cannot die" bug
            'boss_count': 1,
            'ship_fire_rate': 15,
        }
        
        #log file init
        self._initialize_log()
        self.initialized = False
        
        # difficulty font
        self.font = pg.font.SysFont(None, 36)
        
    def _initialize_log(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, "w") as f:
                f.write("Session,Timestamp,Difficulty,Reason\n")
    
    def log_event(self, reason="Update"):
        """Log a difficulty event to the file"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        difficulty_name = self.DIFFICULTY_NAMES[self.current_difficulty]
        
        with open(self.log_file, "a") as f:
            f.write(f"{self.session_id},{timestamp},{difficulty_name},{reason}\n")
    
    def a_star_placement(self, rows, cols):
        
        #Uses A* search principles to determine optimal alien placement based on the current difficulty.
        
        # Convert rows and cols to integers to avoid TypeError
        rows = int(rows)
        cols = int(cols)
        
        # Create grid (1 = normal alien, 2 = stronger alien, 0 = no alien)
        grid = np.ones((rows, cols), dtype=int)
        
        # Calculate difficulty-based parameters
        if self.current_difficulty <= self.EASY:
            # Easier difficulties have greater empty spaces between aliens
            empty_cells = int(rows * cols * (0.2 - 0.05 * self.current_difficulty))
            # Randomly select cells to empty
            for _ in range(empty_cells):
                r, c = random.randint(0, rows-1), random.randint(0, cols-1)
                grid[r, c] = 0
                
        elif self.current_difficulty >= self.MEDIUM:
            # Harder difficulties have stronger aliens
            stronger_aliens = int(rows * cols * (0.1 * self.current_difficulty))
            # Prioritize edges for stronger aliens using A* heuristic
            
            # Create priority map based on distance from edge
            priority_map = np.ones((rows, cols))
            for r in range(rows):
                for c in range(cols):
                    # Calculate distance from edge
                    edge_dist = min(r, rows-r-1, c, cols-c-1)
                    priority_map[r, c] = 1.0 / (edge_dist + 1)
            
            priority_map = priority_map / np.sum(priority_map)
            
            # Select cells for stronger aliens based on priority
            flat_indices = np.arange(rows * cols)
            flat_priorities = priority_map.flatten()
            
            # Select indices with probability proportional to priority
            chosen_indices = np.random.choice(
                flat_indices, 
                size=min(stronger_aliens, rows * cols),
                replace=False,
                p=flat_priorities
            )
            
            # Place stronger aliens in level
            for idx in chosen_indices:
                r, c = idx // cols, idx % cols
                grid[r, c] = 2
                        
        return grid
    
    def set_difficulty(self, difficulty):
        #Set difficulty directly and apply appropriate parameters
        old_difficulty = self.current_difficulty
        self.current_difficulty = difficulty
        
        # Reset consecutive easy level counter if moving out of easy
        if difficulty > self.EASY:
            self.consecutive_easy_levels = 0
            
        # Apply difficulty settings for each specific difficulty ---> modifiers
        if difficulty == self.NOVICE:
            self.params['fleet_drop_speed'] = 0.2
            self.params['boss_spawn_threshold'] = 25
            self.params['boss_speed'] = 0.2
            self.params['boss_fire_rate'] = 30
            self.params['ship_lives'] = 6 
            self.params['boss_count'] = 1
            self.params['ship_fire_rate'] = 5
            self.params['alien_speed'] = 0.3
            self.params['alien_rows'] = 2
            self.params['alien_cols'] = 5
        elif difficulty == self.EASY:
            self.params['fleet_drop_speed'] = 0.3
            self.params['boss_spawn_threshold'] = 20
            self.params['boss_speed'] = 0.3
            self.params['boss_fire_rate'] = 50
            self.params['ship_lives'] = 3
            self.params['boss_count'] = 1
            self.params['ship_fire_rate'] = 10
            self.params['alien_speed'] = 0.5
            self.params['alien_rows'] = 2
            self.params['alien_cols'] = 6
        elif difficulty == self.MEDIUM:
            self.params['fleet_drop_speed'] = 0.4
            self.params['boss_spawn_threshold'] = 30
            self.params['boss_speed'] = 0.5
            self.params['boss_fire_rate'] = 70
            self.params['ship_lives'] = 3
            self.params['boss_count'] = 1
            self.params['ship_fire_rate'] = 10
            self.params['alien_speed'] = 0.4
            self.params['alien_rows'] = 2
            self.params['alien_cols'] = 4
        elif difficulty == self.HARD:
            self.params['fleet_drop_speed'] = 0.6
            self.params['boss_spawn_threshold'] = 10
            self.params['boss_speed'] = 0.6
            self.params['boss_fire_rate'] = 90
            self.params['ship_lives'] = 3  # Minimum of 3 lives to prevent "cannot die" bug
            self.params['boss_count'] = 2
            self.params['ship_fire_rate'] = 15
            self.params['alien_speed'] = 0.8
            self.params['alien_rows'] = 3
            self.params['alien_cols'] = 10
        else:  # EXTREME
            self.params['fleet_drop_speed'] = 0.8
            self.params['boss_spawn_threshold'] = 5
            self.params['boss_speed'] = 0.7
            self.params['boss_fire_rate'] = 100
            self.params['ship_lives'] = 3 
            self.params['boss_count'] = 3
            self.params['ship_fire_rate'] = 16
            self.params['alien_speed'] = 1.0
            self.params['alien_rows'] = 4
            self.params['alien_cols'] = 12
            
        # Apply settings to game if possible
        if self.initialized and hasattr(self.game, 'apply_difficulty_settings'):
            self.game.apply_difficulty_settings()
            
        # Log the change if it's not the initial setup
        if old_difficulty != difficulty:
            print(f"Difficulty changed: {self.DIFFICULTY_NAMES[old_difficulty]} -> {self.DIFFICULTY_NAMES[difficulty]}")
            self.log_event(f"Changed from {self.DIFFICULTY_NAMES[old_difficulty]}")
            
            # Save current settings to file
            try:
                with open("difficulty_settings.json", "w") as f:
                    save_data = {
                        "difficulty": self.current_difficulty,
                        "avg_score": getattr(self.game.stats, "score", 0),
                        "win_rate": 0.9,  # Placeholder
                        "hit_rate": self.hits_landed / max(1, self.shots_fired),
                    }
                    
                    for key, value in self.params.items():
                        save_data[key] = value
                    
                    json.dump(save_data, f)
            except Exception as e:
                print(f"Error saving difficulty settings: {e}")
    
    def on_level_complete(self):
        """Called when a level is completed"""
        self.level_count += 1
        current_time = time.time()
        level_duration = current_time - self.last_level_time
        self.last_level_time = current_time
        
        print(f"Level {self.level_count} completed in {level_duration:.2f} seconds")
        
        # Handle novice/easy progressions - avoid consecutive easy levels bug
        if self.current_difficulty <= self.EASY:
            self.consecutive_easy_levels += 1
            print(f"Consecutive easy/novice levels: {self.consecutive_easy_levels}")
            
            # Fast completion (less than 10 seconds) or multiple easy levels should increase difficulty
            if level_duration <= 5.0 or self.consecutive_easy_levels >= 2:
                reason = "fast completion" if level_duration <= 10.0 else "multiple easy levels"
                print(f"Increasing difficulty due to {reason}")
                self.set_difficulty(min(self.MEDIUM, self.current_difficulty + 1))
            
        # For medium+ difficulties, increase based on level count
        elif self.level_count >= 1 and self.current_difficulty < self.EXTREME:
            self.set_difficulty(self.current_difficulty + 1)
            self.level_count = 0  # Reset level counter after increasing difficulty
    
    def on_ship_hit(self):
        """Called when player ship is hit"""
        self.recent_ship_hits += 1
        
        # Reduce difficulty if on hard/extreme and lost a life
        if self.current_difficulty >= self.HARD:
            print("Reducing difficulty to MEDIUM due to ship hit on hard/extreme")
            self.set_difficulty(self.MEDIUM)
            self.recent_ship_hits = 0
    
    def shot_fired(self):
        """Track shots fired for difficulty adjustment"""
        self.shots_fired += 1
        
    def update_performance_metrics(self, alien_killed=False, ship_hit=False):
        """Update performance metrics based on game events"""
        if alien_killed:
            self.hits_landed += 1
            
        if ship_hit:
            self.on_ship_hit()
    
    def update(self):
        """Update routine to be called once per frame"""
        # Set initialized flag to true on first update
        if not self.initialized:
            self.initialized = True
            self.set_difficulty(self.current_difficulty)
        
        # Check if current level is taking too long - lower difficulty if so
        current_time = time.time()
        if current_time - self.last_level_time > 20 and self.current_difficulty > self.NOVICE:
            print("Level taking too long, reducing difficulty")
            self.set_difficulty(max(self.NOVICE, self.current_difficulty - 1))
            self.last_level_time = current_time  # Reset timer
        
        # Reset ship hit counter periodically - fix bug with difficulty change here
        if self.recent_ship_hits > 0 and random.random() < 0.001:  # Small delta for chance each frame
            self.recent_ship_hits = 0
    
    def draw(self):
        """Draw the difficulty indicator on screen"""
        difficulty_name = self.DIFFICULTY_NAMES[self.current_difficulty]
        color = self.DIFFICULTY_COLORS[self.current_difficulty]
        
        # Create text surface
        text = self.font.render(f"Difficulty: {difficulty_name}", True, color)
        
        # Position at bottom right
        text_rect = text.get_rect()
        text_rect.bottomright = (self.screen.get_rect().right - 20, 
                                self.screen.get_rect().bottom - 10)
        
        # Draw text
        self.screen.blit(text, text_rect)
    
    def game_over(self):
        """Handle game over event"""
        self.log_event("Game Over")