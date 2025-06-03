"""
Main entry point for the Text Adventure Game.

This script initializes and starts the game.
"""
from game import Game

def main():
    """
    Main function to initialize and start the text adventure game.
    """
    # Create an instance of the Game class
    game = Game()
    # Start the game
    game.start_game()

if __name__ == "__main__":
    # This ensures that main() is called only when the script is executed directly
    main()
