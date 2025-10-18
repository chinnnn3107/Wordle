import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
import pygame.font
from Screen import Screen
from ResultScreen import ResultScreen

COLOR_RANK = {"unused": 0, "gray": 1, "yellow": 2, "green": 3}

class GameScreen(Screen):
    is_pygame_screen = True

    def __init__(self, app):
        self.app = app
        self.answer = app.context["answer"]
        self.rows   = app.context["max_attempts"]
        self.cols   = 5

        # Local dictionary (optional)
        self.words_set = set(app.words) if hasattr(app, "words") else set()

        # API validation + cache
        self.use_api_validate = True
        self.meaning_cache: dict[str, bool] = {}

        # Pygame
        pygame.init()
        self.W, self.H = 600, 800
        self.surface = pygame.display.set_mode((self.W, self.H))
        pygame.display.set_caption("Wordle - Game")

        # Theme (easy to swap later)
        self.bg          = (18, 18, 19)
        self.grid_empty  = (58, 58, 60)
        self.text_color  = (232, 232, 232)
        self.clr_green   = (83, 141, 78)
        self.clr_yellow  = (181, 159, 59)
        self.clr_gray    = (58, 58, 60)
        self.clr_keycap  = (129, 131, 132)
        self.clr_keytext = (255, 255, 255)

        # Fonts
        font_name = pygame.font.match_font("Consolas)")
        self.font_cell = pygame.font.Font(None, 64)
        self.font_key  = pygame.font.Font(font_name or None, 40)
        self.font_key_small = pygame.font.Font(font_name or None, 26)
        self.font_msg  = pygame.font.Font(None, 32)

        # Board state
        self.board  = [[""] * self.cols for _ in range(self.rows)]
        self.colors = [[None] * self.cols for _ in range(self.rows)]  # None|gray|yellow|green
        self.cur_row = 0
        self.cur_col = 0
        self.message = ""

        # Grid layout
        self.grid_top   = 80
        self.cell_size  = 64
        self.cell_gap   = 10
        grid_w = self.cols * self.cell_size + (self.cols - 1) * self.cell_gap
        self.grid_left  = (self.W - grid_w) // 2

        # Keyboard layout
        self.kb_top    = 520
        self.kb_rows   = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        self.key_rects = []  # list[(pygame.Rect, label)]
        self.key_state = {c: "unused" for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
        self._build_keyboard_layout()

    def _font_supports(self, ch: str) -> bool:
        # returns True if current font has metrics for this glyph
        m = self.font_key.metrics(ch)
        return bool(m and m[0] is not None)

    # -------------- Check Meaning Word --------------
    def _has_meaning(self, word: str, timeout: float = 3.5) -> bool:
        try:
            import requests  
        except Exception:
            return False
        try:
            url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word.lower()}"
            r = requests.get(url, timeout=timeout)
            if r.status_code != 200:
                return False
            data = r.json()
            if not isinstance(data, list) or not data:
                return False
            meanings = data[0].get("meanings", [])
            return bool(meanings)
        except Exception:
            return False

    def _plural_singular_candidates(self, w: str) -> list[str]:
        # Return possible singular bases for a plural word
        w = w.lower()
        cands = set()

        if w.endswith("ies") and len(w) > 3:
            cands.add(w[:-3] + "y")

        if w.endswith("es"):
            if w[:-2].endswith(("ch", "sh")) or w[-3] in "sxz":
                cands.add(w[:-2])

        if w.endswith("s") and not w.endswith("ss"):
            cands.add(w[:-1])

        if w.endswith("ves") and len(w) > 3:
            cands.add(w[:-3] + "f")
            cands.add(w[:-3] + "fe")

        return [c.upper() for c in cands if c]

    def _is_valid_word(self, word: str) -> bool:
        # Check local list → API; if not found, try singular candidates
        # Local list
        if self.words_set and word in self.words_set:
            return True

        # API for the word
        ok = self.meaning_cache.get(word)
        if ok is None and self.use_api_validate:
            ok = self._has_meaning(word)
            self.meaning_cache[word] = ok
        if ok:
            return True

        # Try singular/plural bases
        for base in self._plural_singular_candidates(word):
            if self.words_set and base in self.words_set:
                return True
            okb = self.meaning_cache.get(base)
            if okb is None and self.use_api_validate:
                okb = self._has_meaning(base)
                self.meaning_cache[base] = okb
            if okb:
                return True

        return False

    # ---------------- Keyboard Layout ----------------
    def _build_keyboard_layout(self):
        """
        Build 3 rows:
          Row0: 10 letters
          Row1:  9 letters (centered)
          Row2: [ENTER] + 7 letters + [BKSP], centered as a whole.
        If too wide, auto-scale to fit.
        """
        key_w, key_h = 48, 58
        gap = 8
        margin_x = 24  # left/right padding

        self.key_rects.clear()

        # Row 0
        row0 = "QWERTYUIOP"
        row0_width = len(row0) * key_w + (len(row0) - 1) * gap
        x = (self.W - row0_width) // 2
        y = self.kb_top + 0 * (key_h + 10)
        for i, ch in enumerate(row0):
            rect = pygame.Rect(x + i * (key_w + gap), y, key_w, key_h)
            self.key_rects.append((rect, ch))

        # Row 1
        row1 = "ASDFGHJKL"
        row1_width = len(row1) * key_w + (len(row1) - 1) * gap
        x = (self.W - row1_width) // 2
        y = self.kb_top + 1 * (key_h + 10)
        for i, ch in enumerate(row1):
            rect = pygame.Rect(x + i * (key_w + gap), y, key_w, key_h)
            self.key_rects.append((rect, ch))

        # Row 2: ENTER + letters + BKSP
        row2_letters = "ZXCVBNM"
        enter_w = key_w + 26
        bksp_w  = key_w + 26
        row2_width = enter_w + gap + len(row2_letters)*key_w + (len(row2_letters)-1)*gap + gap + bksp_w

        max_width = self.W - 2 * margin_x
        if row2_width > max_width:
            # scale everything down proportionally
            scale   = max_width / row2_width
            key_w   = int(key_w * scale)
            key_h   = int(key_h * scale)
            enter_w = int(enter_w * scale)
            bksp_w  = int(bksp_w * scale)
            # recompute row widths for rows 0 & 1 since key_w changed
            row0_width = len(row0) * key_w + (len(row0) - 1) * gap
            row1_width = len(row1) * key_w + (len(row1) - 1) * gap

            # rebuild rows 0 & 1 with new size
            self.key_rects = []
            # Row 0
            x = (self.W - row0_width) // 2
            y = self.kb_top + 0 * (key_h + 10)
            for i, ch in enumerate(row0):
                rect = pygame.Rect(x + i * (key_w + gap), y, key_w, key_h)
                self.key_rects.append((rect, ch))
            # Row 1
            x = (self.W - row1_width) // 2
            y = self.kb_top + 1 * (key_h + 10)
            for i, ch in enumerate(row1):
                rect = pygame.Rect(x + i * (key_w + gap), y, key_w, key_h)
                self.key_rects.append((rect, ch))

            # recompute row2 width with scaled sizes
            row2_width = enter_w + gap + len(row2_letters)*key_w + (len(row2_letters)-1)*gap + gap + bksp_w

        # Finally place row 2 centered
        y = self.kb_top + 2 * (key_h + 10)
        x = (self.W - row2_width) // 2
        # ENTER
        rect_enter = pygame.Rect(x, y, enter_w, key_h)
        self.key_rects.append((rect_enter, "ENTER"))
        # 7 letters
        x = rect_enter.right + gap
        for i, ch in enumerate(row2_letters):
            rect = pygame.Rect(x + i * (key_w + gap), y, key_w, key_h)
            self.key_rects.append((rect, ch))
        # BKSP
        x = self.key_rects[-1][0].right + gap
        rect_bk = pygame.Rect(x, y, bksp_w, key_h)
        self.key_rects.append((rect_bk, "BKSP"))

    # ---------------- Events ----------------
    def handle(self, event):
        if event is None:
            return
        if event.type == pygame.QUIT:
            self.app.set_screen(None)
            return

        if event.type == pygame.KEYDOWN:
            if pygame.K_a <= event.key <= pygame.K_z:
                self._push_char(chr(event.key).upper())
            elif event.key == pygame.K_BACKSPACE:
                self._backspace()
            elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                self._submit_guess()

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, label in self.key_rects:
                if rect.collidepoint(event.pos):
                    if label == "ENTER":
                        self._submit_guess()
                    elif label == "BKSP":
                        self._backspace()
                    else:
                        self._push_char(label)
                    break

    # ---------------- Input ops ----------------
    def _push_char(self, ch: str):
        if self.cur_row >= self.rows:
            return
        if self.cur_col < self.cols:
            self.board[self.cur_row][self.cur_col] = ch
            self.cur_col += 1

    def _backspace(self):
        if self.cur_row >= self.rows:
            return
        if self.cur_col > 0:
            self.cur_col -= 1
            self.board[self.cur_row][self.cur_col] = ""

    def _submit_guess(self):
        if self.cur_col < self.cols:
            self._set_message("Word must be 5 letters.")
            return

        guess = "".join(self.board[self.cur_row])

        # -------- VALIDATION: local list -> API fallback --------
        valid = True
        if self.words_set and guess not in self.words_set:
            valid = False

        if not valid and self.use_api_validate:
            ok = self.meaning_cache.get(guess)
            if ok is None:
                ok = self._has_meaning(guess)
                self.meaning_cache[guess] = ok
            valid = ok

        if not valid:
            self._set_message("Not in dictionary.")
            return

        # -------- Evaluate colors --------
        row_colors = self._evaluate_guess(guess, self.answer)
        self.colors[self.cur_row] = row_colors

        for c, col in zip(guess, row_colors):
            self._upgrade_key_state(c, {"green": "green", "yellow": "yellow", "gray": "gray"}[col])

        # -------- Win/Lose/Next --------
        if guess == self.answer:
            self.app.context["result_type"] = "victory"
            self.app.set_screen(ResultScreen(self.app, "victory", self.answer))
            return

        self.cur_row += 1
        self.cur_col = 0
        if self.cur_row >= self.rows:
            self.app.context["result_type"] = "defeat"
            self.app.set_screen(ResultScreen(self.app, "defeat", self.answer))

    def _set_message(self, msg: str):
        self.message = msg

    def _upgrade_key_state(self, ch: str, new_state: str):
        if ch not in self.key_state:
            return
        if COLOR_RANK[new_state] > COLOR_RANK[self.key_state[ch]]:
            self.key_state[ch] = new_state

    # Proper Wordle evaluation w/ double letters
    def _evaluate_guess(self, guess: str, answer: str):
        res = ["gray"] * self.cols
        counts = {}
        for a in answer:
            counts[a] = counts.get(a, 0) + 1

        # greens
        for i in range(self.cols):
            if guess[i] == answer[i]:
                res[i] = "green"
                counts[guess[i]] -= 1

        # yellows
        for i in range(self.cols):
            if res[i] == "gray":
                g = guess[i]
                if counts.get(g, 0) > 0:
                    res[i] = "yellow"
                    counts[g] -= 1
        return res

    # ---------------- Update/Render ----------------
    def update(self):
        pass

    def render(self):
        self.surface.fill(self.bg)
        self._draw_board()
        self._draw_keyboard()
        self._draw_message()
        pygame.display.flip()

    def _draw_board(self):
        for r in range(self.rows):
            for c in range(self.cols):
                x = self.grid_left + c * (self.cell_size + self.cell_gap)
                y = self.grid_top  + r * (self.cell_size + self.cell_gap)
                rect = pygame.Rect(x, y, self.cell_size, self.cell_size)

                col = self.colors[r][c]
                if col == "green":
                    fill = self.clr_green
                elif col == "yellow":
                    fill = self.clr_yellow
                elif col == "gray":
                    fill = self.clr_gray
                else:
                    fill = None

                if fill:
                    pygame.draw.rect(self.surface, fill, rect, border_radius=6)
                else:
                    pygame.draw.rect(self.surface, self.grid_empty, rect, width=3, border_radius=6)

                ch = self.board[r][c]
                if ch:
                    surf = self.font_cell.render(ch, True, self.text_color)
                    self.surface.blit(surf, surf.get_rect(center=rect.center))

    def _draw_keyboard(self):
        for rect, label in self.key_rects:
            # fill color by state
            if label in self.key_state:
                st = self.key_state[label]
                if st == "green":
                    fill = self.clr_green
                elif st == "yellow":
                    fill = self.clr_yellow
                elif st == "gray":
                    fill = self.clr_gray
                else:
                    fill = self.clr_keycap
            else:
                fill = self.clr_keycap

            pygame.draw.rect(self.surface, fill, rect, border_radius=8)

            # --- choose label & font ---
            draw_label = label
            font_to_use = self.font_key   # default

            if label == "BKSP":
                # use arrow if the font can render it; else fall back
                arrow = "←"
                if hasattr(self, "_font_supports") and self._font_supports(arrow):
                    draw_label = arrow
                else:
                    draw_label = "BKSP"
            elif label == "ENTER":
                draw_label = "ENTER"
                font_to_use = self.font_key_small   # ← smaller font just for ENTER

            # --- render with chosen font ---
            txt = font_to_use.render(draw_label, True, self.clr_keytext)
            self.surface.blit(txt, txt.get_rect(center=rect.center))

    def _draw_message(self):
        if not self.message:
            return
        surf = self.font_msg.render(self.message, True, (250, 250, 250))
        rect = surf.get_rect(center=(self.W // 2, 36))
        self.surface.blit(surf, rect)






