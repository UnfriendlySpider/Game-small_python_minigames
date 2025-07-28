"""
Main game coordinator for Text Adventure Game.
Manages the overall game flow, state, and component integration.
"""

from typing import Dict, Any, Optional
from config.settings import PLAYER, DISPLAY, COMMAND_SHORTCUTS
from config.game_data import get_all_room_ids, MESSAGES
from core.state_manager import StateManager, GameState
from entities.player import Player
from entities.room import Room, create_room
from entities.item import Item
from commands.base_command import CommandManager
from commands.movement_commands import get_all_movement_commands
from commands.inventory_commands import get_all_inventory_commands
from commands.game_commands import get_all_game_commands


class Game:
    """
    Main game coordinator class.
    
    Responsibilities:
    - Initialize and manage all game systems
    - Coordinate between different components
    - Handle the main game loop
    - Manage game state and transitions
    - Process player input and commands
    """
    
    def __init__(self):
        """Initialize the game."""
        # Core systems
        self.state_manager = StateManager(GameState.MENU)
        self.command_manager = CommandManager()
        
        # Game entities
        self.player: Optional[Player] = None
        self.rooms: Dict[str, Room] = {}
        self.current_room: Optional[Room] = None
        
        # Game state
        self.running = True
        self.game_initialized = False
        
        # Initialize systems
        self._initialize_commands()
        self._setup_state_callbacks()
    
    def _initialize_commands(self) -> None:
        """Initialize all game commands."""
        # Register all command types
        all_commands = (
            get_all_movement_commands() +
            get_all_inventory_commands() +
            get_all_game_commands()
        )
        
        for command in all_commands:
            self.command_manager.register_command(command)
    
    def _setup_state_callbacks(self) -> None:
        """Setup callbacks for state transitions."""
        self.state_manager.add_enter_callback(GameState.PLAYING, self._on_enter_playing)
        self.state_manager.add_enter_callback(GameState.MENU, self._on_enter_menu)
        self.state_manager.add_enter_callback(GameState.QUIT, self._on_enter_quit)
    
    def _on_enter_playing(self) -> None:
        """Called when entering the playing state."""
        if not self.game_initialized:
            self._initialize_new_game()
    
    def _on_enter_menu(self) -> None:
        """Called when entering the menu state."""
        self._show_menu()
    
    def _on_enter_quit(self) -> None:
        """Called when entering the quit state."""
        self.running = False
    
    def _initialize_new_game(self) -> None:
        """Initialize a new game with default settings."""
        # Create all rooms
        self.rooms = {}
        for room_id in get_all_room_ids():
            room = create_room(room_id)
            if room:
                self.rooms[room_id] = room
        
        # Get player name
        player_name = self._get_player_name()
        
        # Create player
        starting_room_id = PLAYER.STARTING_LOCATION
        self.player = Player(player_name, starting_room_id)
        
        # Set current room
        self.current_room = self.rooms.get(starting_room_id)
        if not self.current_room:
            raise RuntimeError(f"Starting room '{starting_room_id}' not found!")
        
        # Show welcome message and initial room description
        print(MESSAGES["welcome"])
        self.current_room.describe(self.player.has_light_source)
        
        self.game_initialized = True
    
    def _get_player_name(self) -> str:
        """Get the player's name."""
        while True:
            name = input("Enter your name: ").strip()
            if name:
                return name
            print("Please enter a valid name.")
    
    def _show_menu(self) -> None:
        """Display the main menu."""
        print(f"\n=== {DISPLAY.SEPARATOR_CHAR * 50} ===")
        print("Welcome to Text Adventure Game!")
        print(f"=== {DISPLAY.SEPARATOR_CHAR * 50} ===")
        print("\nOptions:")
        print("1. Start New Game")
        print("2. Load Game")
        print("3. Help")
        print("4. Quit")
        print("\nType the number or command name (e.g., 'new', 'load', 'help', 'quit')")
    
    def start_game(self) -> None:
        """Start the main game."""
        print(f"Starting {DISPLAY.SEPARATOR_CHAR * 20}")
        
        # Show initial menu
        self._show_menu()
        
        # Main game loop
        while self.running:
            try:
                self._game_loop_iteration()
            except KeyboardInterrupt:
                print("\n\nGame interrupted by user.")
                break
            except Exception as e:
                print(f"\nAn error occurred: {e}")
                print("The game will continue, but you may want to save and restart.")
        
        print("\nThanks for playing!")
    
    def _game_loop_iteration(self) -> None:
        """Single iteration of the game loop."""
        # Get user input
        prompt = DISPLAY.PROMPT_SYMBOL
        if self.state_manager.is_in_state(GameState.PLAYING) and self.player:
            # Update player effects
            expired_effects = self.player.update_effects()
            for effect in expired_effects:
                print(f"The {effect} effect has worn off.")
        
        user_input = input(prompt).strip()
        
        if not user_input:
            return
        
        # Process shortcuts
        user_input = self._process_shortcuts(user_input)
        
        # Handle menu state differently
        if self.state_manager.is_in_state(GameState.MENU):
            self._handle_menu_input(user_input)
        else:
            self._handle_game_input(user_input)
    
    def _process_shortcuts(self, user_input: str) -> str:
        """Process command shortcuts."""
        # Check if the entire input is a shortcut
        if user_input.lower() in COMMAND_SHORTCUTS:
            return COMMAND_SHORTCUTS[user_input.lower()]
        
        # Check if the first word is a shortcut
        parts = user_input.split()
        if parts and parts[0].lower() in COMMAND_SHORTCUTS:
            shortcut_expansion = COMMAND_SHORTCUTS[parts[0].lower()]
            return shortcut_expansion + " " + " ".join(parts[1:])
        
        return user_input
    
    def _handle_menu_input(self, user_input: str) -> None:
        """Handle input while in menu state."""
        user_input = user_input.lower()
        
        if user_input in ["1", "new", "new game", "start"]:
            self.state_manager.change_state(GameState.PLAYING)
        elif user_input in ["2", "load", "load game"]:
            self._handle_load_from_menu()
        elif user_input in ["3", "help", "h", "?"]:
            print(MESSAGES["help"])
        elif user_input in ["4", "quit", "q", "exit"]:
            self.state_manager.change_state(GameState.QUIT)
        else:
            print("Invalid option. Please choose 1-4 or type a command name.")
    
    def _handle_load_from_menu(self) -> None:
        """Handle loading a game from the menu."""
        # Show available saves
        game_state = self._get_game_state()
        from commands.game_commands import ListSavesCommand
        list_saves = ListSavesCommand()
        result = list_saves.execute([], game_state)
        print(result["message"])
        
        # Get slot to load
        try:
            slot_input = input("Enter save slot to load (1-5) or press Enter to cancel: ").strip()
            if not slot_input:
                return
            
            slot = int(slot_input)
            if 1 <= slot <= 5:
                from commands.game_commands import LoadCommand
                load_command = LoadCommand()
                result = load_command.execute([str(slot)], game_state)
                
                if result["success"]:
                    save_data = result["data"]["save_data"]
                    self._load_game_from_data(save_data)
                    self.state_manager.change_state(GameState.PLAYING)
                else:
                    print(result["message"])
            else:
                print("Invalid slot number.")
        except ValueError:
            print("Invalid input.")
    
    def _handle_game_input(self, user_input: str) -> None:
        """Handle input while in game state."""
        # Create game state for command execution
        game_state = self._get_game_state()
        
        # Execute command
        result = self.command_manager.execute_command(user_input, game_state)
        
        # Display result message
        if result.message:
            print(result.message)
        
        # Handle state changes
        if result.state_change:
            if result.state_change == "quit":
                self.state_manager.change_state(GameState.QUIT)
        
        # Handle special command results
        if result.data:
            if result.data.get("load_requested"):
                save_data = result.data["save_data"]
                self._load_game_from_data(save_data)
            elif result.data.get("new_game_requested"):
                self._initialize_new_game()
    
    def _get_game_state(self) -> Dict[str, Any]:
        """Get current game state for command execution."""
        return {
            "player": self.player,
            "current_room": self.current_room,
            "rooms": self.rooms,
            "state_manager": self.state_manager,
            "command_manager": self.command_manager,
            "game": self
        }
    
    def _load_game_from_data(self, save_data: Dict[str, Any]) -> None:
        """Load game state from save data."""
        try:
            # Restore player
            self.player = Player.from_dict(save_data["player"])
            
            # Restore rooms
            self.rooms = {}
            for room_id, room_data in save_data["rooms"].items():
                self.rooms[room_id] = Room.from_dict(room_data)
            
            # Set current room
            current_room_id = save_data["current_room_id"]
            self.current_room = self.rooms.get(current_room_id)
            
            if not self.current_room:
                raise RuntimeError(f"Current room '{current_room_id}' not found in save data!")
            
            # Mark game as initialized
            self.game_initialized = True
            
            print(f"\nGame loaded successfully!")
            print(f"Welcome back, {self.player.name}!")
            self.current_room.describe(self.player.has_light_source)
            
        except Exception as e:
            print(f"Error loading game: {e}")
            print("Starting a new game instead...")
            self._initialize_new_game()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get game statistics for debugging.
        
        Returns:
            Dict containing game stats
        """
        stats = {
            "current_state": self.state_manager.get_state_name(),
            "game_initialized": self.game_initialized,
            "running": self.running,
            "rooms_count": len(self.rooms),
            "commands_count": len(self.command_manager.get_all_commands())
        }
        
        if self.player:
            stats.update({
                "player_name": self.player.name,
                "current_room": self.current_room.room_id if self.current_room else None,
                "player_health": self.player.health,
                "inventory_count": len(self.player.inventory)
            })
        
        return stats
    
    def save_game(self, slot: int = 1) -> bool:
        """
        Save the current game state.
        
        Args:
            slot: Save slot number (1-5)
            
        Returns:
            bool: True if save was successful
        """
        if not self.player or not self.current_room:
            return False
        
        game_state = self._get_game_state()
        from commands.game_commands import SaveCommand
        save_command = SaveCommand()
        result = save_command.execute([str(slot)], game_state)
        
        return result["success"]
    
    def load_game(self, slot: int = 1) -> bool:
        """
        Load a game from the specified slot.
        
        Args:
            slot: Save slot number (1-5)
            
        Returns:
            bool: True if load was successful
        """
        game_state = self._get_game_state()
        from commands.game_commands import LoadCommand
        load_command = LoadCommand()
        result = load_command.execute([str(slot)], game_state)
        
        if result["success"]:
            save_data = result["data"]["save_data"]
            self._load_game_from_data(save_data)
            return True
        
        return False


def main():
    """Entry point for the game."""
    try:
        game = Game()
        game.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game crashed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
