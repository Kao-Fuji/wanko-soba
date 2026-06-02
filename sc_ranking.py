
# screen_ranking.py
# ランキング確認画面

import tkinter as tk

from setting import WINDOW_WIDTH, WINDOW_HEIGHT
from ui import make_button


class RankingScreen(tk.Frame):
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

        self.draw()

    def draw(self):
        bg = self.app.images.load(
            "background",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        if bg is not None:
            self.canvas.create_image(
                WINDOW_WIDTH // 2,
                WINDOW_HEIGHT // 2,
                image=bg
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

        self.canvas.create_rectangle(
            190,
            70,
            810,
            610,
            fill="#fff4cf",
            outline="#5a3a1d",
            width=4
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            120,
            text="ランキング",
            font=("Yu Gothic UI", 36, "bold"),
            fill="#2f2418",
        )

        data = self.app.ranking.top(limit=10)

        if not data:
            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                300,
                text="まだ記録がありません。\n本番モードで遊ぶとここに表示されます。",
                font=("Yu Gothic UI", 21, "bold"),
                fill="#2f2418",
                justify="center",
            )

        else:
            y = 180

            for index, entry in enumerate(data, start=1):
                score = entry.get("score", 0)
                created = entry.get("created_at", "")

                text = f"{index:>2}位　{score:>3}杯　{created}"

                self.canvas.create_text(
                    290,
                    y,
                    text=text,
                    anchor="w",
                    font=("Yu Gothic UI", 17, "bold"),
                    fill="#2f2418",
                )

                y += 38

        back_btn = make_button(
            self,
            "タイトルへ",
            self.app.show_title,
            width=14,
            font_size=15
        )

        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            555,
            window=back_btn
        )