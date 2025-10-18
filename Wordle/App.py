from typing import Optional
from Screen import Screen
from GameScreen import GameScreen
from WordList import load_words, choose_random_word

class App:
    def __init__(self):
        # Load all valid 5-letter words from file
        self.words = load_words("WordList.txt")

        # Store game-wide data in a shared dictionary
        self.context = {
            "answer": choose_random_word(self.words), # The target word to guess
            "attempts": [],                           # List of previous guesses
            "max_attempts": 5,                        # Maximum allowed guesses
            "result_type": None,                      # "victory" | "defeat"
        }

        # Set the initial screen to the main game screen
        # Optional[Screen] means it can be either a Screen or None
        self.current: Optional[Screen] = GameScreen(self)   

    # Change to another screen (or None to end the game)
    def set_screen(self, screen: Optional[Screen]):         
        self.current = screen

    # Restart
    def new_game(self): 
        from WordList import choose_random_word
        self.context["answer"] = choose_random_word(self.words)
        self.context["attempts"].clear()
        self.context["result_type"] = None
        self.set_screen(GameScreen(self))
        
    def run(self):
        import pygame

        clock = None
        while self.current is not None:
            # If current screen is a pygame screen, pump events and limit FPS
            if hasattr(self.current, "is_pygame_screen") and self.current.is_pygame_screen:
                if clock is None:
                    clock = pygame.time.Clock()

                # Render first (optional ordering), then handle events
                self.current.render()
                for e in pygame.event.get():
                    self.current.handle(e)

                # Let screen update any internal state
                self.current.update()
                clock.tick(60)
            else:
                # CLI screen: render once, then block on handle() which uses input()
                self.current.render()
                self.current.handle(None)
                self.current.update()
            

