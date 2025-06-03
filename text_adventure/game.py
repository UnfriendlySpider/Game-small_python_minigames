from player import Player
from room import Room

class Game:
    """
    Manages the text adventure game state, including rooms, the player,
    and game progression.

    Attributes:
        rooms (dict): A dictionary storing all rooms in the game,
                      keyed by room name.
        player (Player): The player object.
        current_room (Room): The room the player is currently in.
    """
    def __init__(self):
        """Initializes a new Game instance."""
        self.rooms = {}  # Stores all room objects
        self.player = None  # Player object will be created in start_game
        self.current_room = None  # The room the player is currently in

    def add_room(self, room):
        """
        Adds a room to the game's collection of rooms.

        Args:
            room (Room): The room object to add.
        """
        self.rooms[room.name] = room

    def start_game(self):
        """
        Initializes and starts the game.
        This includes creating default rooms, the player,
        and starting the main game loop.
        """
        # --- Room Creation ---
        # Create instances of the Room class
        start_room = Room("Start Room", "You are in a dimly lit starting room. It's quiet and a bit dusty.")
        kitchen = Room("Kitchen", "You are in a messy kitchen. Dirty dishes are piled in the sink.")

        # Define exits for the rooms
        start_room.add_exit("north", "Kitchen")
        kitchen.add_exit("south", "Start Room")

        # Add rooms to the game
        self.add_room(start_room)
        self.add_room(kitchen)

        # --- Player Creation ---
        player_name = input("Enter your name: ")
        # Create the player object, starting them in the 'start_room'
        self.player = Player(player_name, start_room.name)
        self.current_room = start_room  # Set the game's current room

        # Display the description of the starting room
        self.current_room.describe()

        # Start the main game processing loop
        self.game_loop()

    def process_input(self, command):
        """
        Processes the player's input command.

        Args:
            command (str): The command entered by the player.

        Returns:
            bool: True if the game should continue, False if the player quits.
        """
        parts = command.lower().split()  # Convert to lowercase and split into words
        if not parts:
            print("Please enter a command.")
            return True # Continue game loop

        action = parts[0] # The first word is the action

        if action == "quit":
            print("Thanks for playing!")
            return False  # Signal to end the game loop
        elif action == "look":
            self.current_room.describe()
        elif action == "go":
            if len(parts) > 1:
                direction = parts[1]  # The second word is the direction
                next_room_name = self.current_room.get_exit(direction)
                if next_room_name:
                    # Check if the next room exists in our game's room dictionary
                    if next_room_name in self.rooms:
                        self.current_room = self.rooms[next_room_name]
                        self.player.move(self.current_room.name) # Update player's current room
                        self.current_room.describe()
                    else:
                        # This should ideally not happen if rooms are set up correctly
                        print(f"Error: Room '{next_room_name}' not found in game data.")
                else:
                    print("You can't go that way.")
            else:
                print("Go where? (e.g., 'go north')")
        # Add more command processing here (e.g., "get", "use", "inventory")
        else:
            print("Invalid command. Type 'look', 'go [direction]', or 'quit'.")
        return True # Signal to continue game loop

    def game_loop(self):
        """
        Main game loop that continuously prompts the player for input
        and processes it until the game ends.
        """
        while True:
            command = input("> ")
            if not self.process_input(command):
                break  # Exit loop if process_input returns False (e.g., on "quit")

if __name__ == "__main__":
    # This block allows the game to be run directly from this file
    game = Game()
    game.start_game()
