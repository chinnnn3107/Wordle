import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from Screen import Screen

class ResultScreen(Screen):
    # Flag for App.run() to know this is a pygame screen
    is_pygame_screen = True

    def __init__(self, app, result_type: str, answer: str):
        self.app = app
        self.result_type = result_type
        self.answer = answer

        pygame.init()
        self.surface = pygame.display.set_mode((600, 400))
        pygame.display.set_caption("Wordle Result")
        self.font_title = pygame.font.Font(None, 72)
        self.font_text  = pygame.font.Font(None, 36)
        self.theme = {
            "victory": {"title": "YOU WIN!",  "color": (80,200,120), "bg": (240,255,240)},
            "defeat":  {"title": "YOU LOSE!", "color": (220,80,80),  "bg": (255,240,240)},
        }[self.result_type]

        self.btn_restart = pygame.Rect(150, 260, 130, 50)
        self.btn_quit    = pygame.Rect(320, 260, 130, 50)

    def handle(self, event):
        if event is None:
            return
        if event.type == pygame.QUIT:
            self.app.set_screen(None)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.btn_restart.collidepoint(event.pos):
                self.app.new_game()
            elif self.btn_quit.collidepoint(event.pos):
                self.app.set_screen(None)

    def update(self):
        pass

    def render(self):
        self.surface.fill(self.theme["bg"])
        title = self.font_title.render(self.theme["title"], True, self.theme["color"])
        self.surface.blit(title, title.get_rect(center=(300, 100)))
        ans = self.font_text.render(f"Answer: {self.answer}", True, (30,30,30))
        self.surface.blit(ans, ans.get_rect(center=(300, 180)))

        import pygame as pg
        pg.draw.rect(self.surface, (100,200,250), self.btn_restart, border_radius=10)
        pg.draw.rect(self.surface, (200,100,100), self.btn_quit,    border_radius=10)

        self.surface.blit(
            self.font_text.render("Restart", True, (255,255,255)),
            self.font_text.render("Restart", True, (255,255,255)).get_rect(center=self.btn_restart.center)
        )
        self.surface.blit(
            self.font_text.render("Quit", True, (255,255,255)),
            self.font_text.render("Quit", True, (255,255,255)).get_rect(center=self.btn_quit.center)
        )
        pygame.display.flip()
