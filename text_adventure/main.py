"""
Main entry point for the Text Adventure Game.

This script initializes and starts the enhanced text adventure game.
"""

from core.game import Game


def main():
    """
    Main function to initialize and start the text adventure game.
    """
    try:
        # Create an instance of the enhanced Game class
        game = Game()
        # Start the game
        game.start_game()
    except KeyboardInterrupt:
        print("\nGame interrupted by user")
    except Exception as e:
        print(f"Game crashed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # This ensures that main() is called only when the script is executed directly
    main()
