
# screen_title.py
# タイトル画面

import tkinter as tk

from setting import WINDOW_WIDTH, WINDOW_HEIGHT
from ui import make_button


class TitleScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f6d28b")

        self.app = app

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_background()
        self.draw_title()
        self.draw_buttons()

    def draw_background(self):
        bg = self.app.images.load_cover(
            "background",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        if bg is not None:
            self.canvas.create_image(
                0,
                0,
                image=bg,
                anchor ="nw"
            )
            self.bg_image = bg

        else:
            self.canvas.create_rectangle(
                0,
                0,
                WINDOW_WIDTH,
                WINDOW_HEIGHT,
                fill="#f4c06a",
                outline=""
            )

            self.canvas.create_oval(
                -120,
                430,
                260,
                780,
                fill="#e6a74a",
                outline=""
            )

            self.canvas.create_oval(
                760,
                -120,
                1120,
                240,
                fill="#ffd98a",
                outline=""
            )

    def draw_title(self):
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            130,
            text="わんこそば\n連打ゲーム",
            font=("Yu Gothic UI", 46, "bold"),
            fill="#2d1c0f",
            justify="center",
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            245,
            text="食べる？ 食べない？ 皿が積もれば時間も積もる。",
            font=("Yu Gothic UI", 18, "bold"),
            fill="#4c2d15",
        )

    def draw_buttons(self):
        frame = tk.Frame(self, bg="#f6d28b")
        self.canvas.create_window(WINDOW_WIDTH // 2, 420, window=frame)

        make_button(
            frame,
            "練習モード",
            self.app.show_practice
        ).pack(pady=10)

        make_button(
            frame,
            "本番モード",
            self.app.start_real_game
        ).pack(pady=10)

        make_button(
            frame,
            "ランキング",
            self.app.show_ranking
        ).pack(pady=10)

        make_button(
            frame,
            "終了",
            self.app.root.destroy
        ).pack(pady=10)