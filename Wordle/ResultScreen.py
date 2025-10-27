import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from Screen import Screen

class ResultScreen(Screen):
    def __init__(self, app, result_type: str, answer: str):
        self.app = app
        self.result_type = result_type
        self.answer = answer
        self.mouse_down = False

        # Initialize pygame modules
        pygame.init() 

        # ---------------- Window Setup ----------------
        self.W, self.H = 1200, 800
        self.surface = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Wordle")

        # ---------------- Fonts ----------------
        self.font_title = pygame.font.Font(None, 72)
        self.font_text  = pygame.font.Font(None, 36)

        # ---------------- Theme ----------------
        # Choose colors and text based on the result type
        self.theme = {
            "victory": {"title": "YOU WIN!",  "color": (80,200,120), "background": (240,255,240)},
            "defeat":  {"title": "YOU LOSE!", "color": (220,80,80),  "background": (255,240,240)},
        }[self.result_type]

        # ---------------- Buttons Layout ----------------
        # Define two buttons, centered horizontally
        button_w, button_h = 160, 60
        gap = 40  # space between buttons
        total_w = button_w * 2 + gap
        start_x = (self.W - total_w) // 2
        y = self.H // 2 + 100  # slightly below center

        # Create rectangle areas for the buttons
        self.button_restart = pygame.Rect(start_x, y, button_w, button_h)
        self.button_quit = pygame.Rect(start_x + button_w + gap, y, button_w, button_h)

    def handle(self, event):
        if event is None:
            return

        if event.type == pygame.QUIT:
            self.app.set_screen(None)

        # If user clicks with mouse
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.mouse_down = True
            if self.button_restart.collidepoint(event.pos):
                self.app.new_game()
            elif self.button_quit.collidepoint(event.pos):
                self.app.set_screen(None)

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_down = False


    def update(self):
        pass

    def render(self):
        # ---------------- Background ----------------
        self.surface.fill((18, 18, 19))  # Dark theme background

        # ---------------- Title ----------------
        title = self.font_title.render(self.theme["title"], True, self.theme["color"])
        self.surface.blit(title, title.get_rect(center=(self.W // 2, self.H // 2 - 120)))

        # ---------------- Answer ----------------
        ans = self.font_text.render(f"Answer: {self.answer}", True, (220, 220, 220))
        self.surface.blit(ans, ans.get_rect(center=(self.W // 2, self.H // 2 - 10)))

        # ---------------- Hover detection ----------------
        mouse_pos = pygame.mouse.get_pos()
        mouse_down = pygame.mouse.get_pressed()[0]  # Left mouse button pressed?

        # Helper function to draw a scaling button
        def draw_button(base_rect, color, text):
            # Determine if mouse is over this button
            hovering = base_rect.collidepoint(mouse_pos)

            # Scale factor (grow on hover, shrink when pressed)
            if hovering and mouse_down:
                scale = 0.93   # pressed
            elif hovering:
                scale = 1.08   # hover
            else:
                scale = 1.0    # normal

            # Compute new scaled rect (centered around original center)
            new_w = int(base_rect.width * scale)
            new_h = int(base_rect.height * scale)
            scaled_rect = pygame.Rect(0, 0, new_w, new_h)
            scaled_rect.center = base_rect.center

            # Draw button background
            pygame.draw.rect(self.surface, color, scaled_rect, border_radius=12)

            # Draw text centered
            txt = self.font_text.render(text, True, (255, 255, 255))
            self.surface.blit(txt, txt.get_rect(center=scaled_rect.center))

        # ---------------- Draw Buttons ----------------
        draw_button(self.button_restart, (100, 200, 250), "Restart")
        draw_button(self.button_quit, (200, 100, 100), "Quit")

        # ---------------- Display Update ----------------
        pygame.display.flip()

