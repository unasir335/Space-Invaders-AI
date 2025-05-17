# Space Invaders with Adaptive Difficulty

This is an enhanced version of the classic Space Invaders game featuring an AI-based adaptive difficulty system that uses A* search and heuristics to create an optimal challenge for players of all skill levels.

## How to Run the Game

1. Make sure you have Python 3 installed on your system
2. Install the required dependencies:
   ```
   pip install pygame numpy
   ```
3. Run the game by executing:
   ```
   python game.py
   ```

## Game Controls

- **Arrow Keys** or **WASD**: Move your ship
- **Space Bar**: Fire lasers
- **P**: Start the game from the landing page
- **Mouse**: Click the "PLAY GAME" button to start

## Code Structure

### Main Game Files

- **game.py**: The main game class and entry point. Initializes and manages all game components.
- **alien.py**: Contains the AlienFleet class and Alien class for enemy management.
- **ship.py**: Player's ship implementation with movement and firing capabilities.
- **laser.py**: Laser projectiles for both the player and aliens.
- **settings.py**: Game settings and configuration parameters.

### AI and Difficulty Management

- **ai_difficulty_manager.py**: Implements the adaptive difficulty system using A* search and heuristic principles for alien placement. Use 2x8 grid for popssible enemy placement based on difficulty.
- **stats.py**: Tracks game statistics and performance metrics used by the difficulty manager.

### User Interface

- **landing_page.py**: Initial game screen with instructions and start button.
- **scoreboard.py**: Displays game score, lives, and level information.
- **button.py**: UI button component used in the landing page.

### Support/Adjacent Systems

- **game_functions.py**: Helper functions for game operations like event handling.
- **sound.py**: Manages game sounds and music.
- **timer.py**: Handles animation timing and sequences.
- **vector.py**: Vector mathematics for movement and positioning.

### Data Files

- **images/**: Contains all game sprites and visual assets.
- **sounds/**: Contains all audio files.
- **highscore.txt**: Stores the highest score achieved.
- **difficulty_log.txt**: Logs difficulty changes during gameplay.
- **difficulty_settings.json**: Stores current difficulty parameters.

## Key Features

### Adaptive Difficulty System

The game features an innovative difficulty system that:

1. Adjusts game parameters based on player performance
2. Uses A* search principles to place aliens strategically
3. Modifies difficulty in real-time during gameplay
4. Provides appropriate challenge for all skill levels

The difficulty system monitors:
- Level completion time
- Player hits and misses
- Consecutive easy levels passed
- Overall score progression

### A* Search for Alien Placement

The AI difficulty manager uses a modified A* search algorithm to:

1. Create a priority map for alien positions
2. Place stronger aliens at strategic edge positions
3. Adjust the density and type of aliens based on difficulty
4. Create varied but consistently challenging levels

## Development Notes

- The difficulty manager prevents circular dependencies by using an initialization flag
- Ship lives are always kept at a minimum of 3 to prevent "cannot die" bugs
- Difficulty is reduced automatically when a player is hit on higher difficulty levels
- The system logs all difficulty changes to difficulty_log.txt for analysis

## Files Explained

- **game.py**: Main game loop and component management
- **alien.py**: Enemy behavior, spawning, and fleet management
- **ai_difficulty_manager.py**: Core AI system that adjusts game difficulty
- **ship.py**: Player ship controls and state management
- **laser.py**: Projectile physics and collision detection
- **stats.py**: Score and performance tracking
- **scoreboard.py**: Visual display of game statistics
- **landing_page.py**: Start screen and game introduction
- **button.py**: Interactive UI elements
- **game_functions.py**: Input handling and event processing
- **sound.py**: Audio management
- **timer.py**: Animation and timing control
- **vector.py**: Mathematical utilities for movement
- **settings.py**: Game configuration parameters