class Room:
    """Represents a room in the text adventure game."""
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self.exits = {}  # e.g., {"north": "kitchen"}

    def __str__(self):
        return self.name

    def add_exit(self, direction, room_name):
        """Adds an exit to the room."""
        self.exits[direction] = room_name

    def get_exit(self, direction):
        """Returns the room name for a given exit direction."""
        return self.exits.get(direction)

    def describe(self):
        """Prints the room's description and available exits."""
        print(self.description)
        if self.exits:
            print("Exits:")
            for direction in self.exits:
                print(f"- {direction}")
        else:
            print("There are no obvious exits.")
