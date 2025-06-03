from player import Player
from room import Room

class Game:
    """Manages the text adventure game state."""
    def __init__(self):
        self.rooms = {}
        self.player = None
        self.current_room = None

    def add_room(self, room):
        """Adds a room to the game."""
        self.rooms[room.name] = room

    def start_game(self):
        """Starts the game."""
        # Create rooms
        start_room = Room("Start Room", "You are in a dimly lit starting room.")
        kitchen = Room("Kitchen", "You are in a messy kitchen.")
        start_room.add_exit("north", "Kitchen")
        kitchen.add_exit("south", "Start Room")

        self.add_room(start_room)
        self.add_room(kitchen)

        # Create player
        player_name = input("Enter your name: ")
        self.player = Player(player_name, start_room.name)
        self.current_room = start_room
        self.current_room.describe()

        self.game_loop()

    def process_input(self, command):
        """Processes player input."""
        parts = command.lower().split()
        if not parts:
            return

        action = parts[0]

        if action == "quit":
            print("Thanks for playing!")
            return False  # Signal to end the game loop
        elif action == "look":
            self.current_room.describe()
        elif action == "go":
            if len(parts) > 1:
                direction = parts[1]
                next_room_name = self.current_room.get_exit(direction)
                if next_room_name:
                    if next_room_name in self.rooms:
                        self.current_room = self.rooms[next_room_name]
                        self.player.move(self.current_room.name)
                        self.current_room.describe()
                    else:
                        print(f"Error: Room '{next_room_name}' not found.")
                else:
                    print("You can't go that way.")
            else:
                print("Go where?")
        else:
            print("Invalid command.")
        return True # Signal to continue game loop

    def game_loop(self):
        """Main game loop."""
        while True:
            command = input("> ")
            if not self.process_input(command):
                break

if __name__ == "__main__":
    game = Game()
    game.start_game()
