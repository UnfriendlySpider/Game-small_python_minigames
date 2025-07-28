# Enhanced Text Adventure Game

A professionally structured text-based adventure game with modern software architecture and extensive features.

## 🎮 Features

### Core Gameplay
- **Rich Interactive World**: Explore detailed rooms with dynamic descriptions
- **Advanced Inventory System**: Carry items with weight limits and item stacking
- **Character Progression**: Player stats, health, energy, and experience tracking
- **Dynamic Environment**: Room lighting, locked doors, and interactive objects
- **Smart Command System**: Intuitive commands with shortcuts and aliases

### Technical Features
- **Save/Load System**: Multiple save slots with JSON-based persistence
- **State Management**: Professional game state handling with callbacks
- **Modular Architecture**: Clean separation of concerns and extensible design
- **Command History**: Track and review recent commands
- **Error Handling**: Robust error handling with graceful recovery

## 🏗️ Architecture

### Directory Structure
```
text_adventure/
├── main.py                    # Entry point
├── config/                    # Configuration and game data
│   ├── settings.py           # Game configuration
│   └── game_data.py          # Room and item definitions
├── core/                     # Core game systems
│   ├── game.py               # Main game coordinator
│   └── state_manager.py      # Game state management
├── entities/                 # Game entities
│   ├── player.py             # Enhanced player class
│   ├── room.py               # Enhanced room class
│   └── item.py               # Rich item system
├── commands/                 # Command system
│   ├── base_command.py       # Command framework
│   ├── movement_commands.py  # Movement and exploration
│   ├── inventory_commands.py # Item management
│   └── game_commands.py      # Save/load/help commands
└── saves/                    # Save game files (auto-created)
```

### Key Improvements Over Original

#### 1. **Professional Structure**
- **Before**: All code in 4 files in root directory
- **After**: Organized into logical modules with clear responsibilities

#### 2. **Configuration Management**
- **Before**: Hardcoded values scattered throughout code
- **After**: Centralized configuration in `config/settings.py` and `config/game_data.py`

#### 3. **Enhanced Entities**
- **Player**: Stats, equipment, effects, progress tracking
- **Room**: Dynamic lighting, locking, item management
- **Item**: Condition, stacking, special effects, detailed examination

#### 4. **Command System**
- **Before**: Simple if/else chains
- **After**: Pluggable command architecture with validation and help

#### 5. **State Management**
- **Before**: Basic game loop
- **After**: Professional state machine with callbacks and transitions

## 🎯 How to Play

### Starting the Game
```bash
cd text_adventure
python3 main.py
```

### Basic Commands

#### Movement
- `go <direction>` or just `<direction>` (e.g., `north`, `n`)
- `look` - Examine your surroundings
- `examine <item>` - Look at something closely

#### Inventory
- `get <item>` - Pick up an item
- `drop <item>` - Drop an item
- `inventory` or `i` - Show your inventory
- `use <item>` - Use an item
- `equip <item>` - Equip a weapon/armor

#### Character
- `status` - Show health and energy
- `stats` - Show detailed character statistics

#### Game Management
- `save [slot]` - Save your game (slots 1-5)
- `load [slot]` - Load a saved game
- `saves` - List all save files
- `help` - Show all commands
- `quit` - Exit the game

### Shortcuts
- `n`, `s`, `e`, `w` for directions
- `i` for inventory
- `l` for look
- `q` for quit
- `h` for help

## 🔧 Configuration

### Game Settings (`config/settings.py`)
- Player starting stats and inventory limits
- Command shortcuts and aliases
- Display formatting options
- File paths and save settings

### Game Content (`config/game_data.py`)
- Room definitions and connections
- Item properties and behaviors
- Game messages and text
- Special room behaviors

## 💾 Save System

The game uses JSON-based save files with the following features:
- **Multiple Slots**: 5 save slots available
- **Complete State**: Saves player, rooms, items, and progress
- **Metadata**: Timestamps and game statistics
- **Validation**: Corrupted save detection and recovery

Save files are stored in the `saves/` directory as `save_slot_X.json`.

## 🎨 Extensibility

### Adding New Commands
1. Create a new command class inheriting from `BaseCommand`
2. Implement the `execute` method
3. Register the command in the appropriate module

### Adding New Items
1. Add item definition to `ITEMS` in `config/game_data.py`
2. Implement special behaviors in `entities/item.py` if needed

### Adding New Rooms
1. Add room definition to `ROOMS` in `config/game_data.py`
2. Connect to existing rooms via exits
3. Add special behaviors in `ROOM_BEHAVIORS` if needed

## 🐛 Error Handling

The game includes comprehensive error handling:
- **Graceful Degradation**: Game continues even if errors occur
- **User Feedback**: Clear error messages for invalid commands
- **State Recovery**: Automatic recovery from corrupted saves
- **Debug Information**: Detailed error traces for development

## 📈 Performance

- **Lazy Loading**: Rooms and items created on demand
- **Memory Efficient**: Proper cleanup and resource management
- **Fast Commands**: O(1) command lookup with hash tables
- **Minimal Dependencies**: Pure Python with standard library only

## 🔮 Future Enhancements

Potential areas for expansion:
- **Combat System**: Turn-based combat with the existing stats
- **NPCs**: Non-player characters with dialogue trees
- **Quests**: Structured quest system with objectives
- **Magic System**: Spells and magical effects
- **Multiplayer**: Network-based multiplayer support
- **Graphics**: Optional ASCII art or simple GUI
- **Sound**: Audio effects and background music
- **Scripting**: Lua or Python scripting for custom content

## 🤝 Contributing

The modular architecture makes it easy to contribute:
1. Each module has clear responsibilities
2. Commands are self-contained and testable
3. Configuration is externalized
4. Comprehensive documentation and type hints

## 📝 License

This enhanced text adventure game is available under the same license as the original project.

---

**Enjoy your adventure!** 🗡️⚔️🏰
