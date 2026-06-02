
# screen_practice.py
# 練習モードの説明画面

import tkinter as tk

from setting import WINDOW_WIDTH, WINDOW_HEIGHT
from ui import make_button, draw_text_box


PRACTICE_MESSAGES = [
    "ここは練習モードです。まずは、わんこそばの流れを確認します。",
    "そば・うどん・中華麺・ほうとうは食べられます。必要なクリック回数がそれぞれ違います。",
    "ダークマターと岩は食べちゃダメです。出てきたら「食べない」を押して回避します。",
    "岩塩はクリック数2倍、苔は3倍、薬味は全部1回になります。今回は効果が次の5皿続く設定です。",
    "お椀が10個たまるとミニゲームです。お椀をまっすぐ積めるほど、残り時間が増えます。",
    "説明はここまで。次は10秒の練習プレイに入ります。",
]


class PracticeScreen(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent, bg="#f6d28b")

        self.app = app
        self.index = 0

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        self.draw_base()
        self.show_message()

    def draw_base(self):
        bg = self.app.images.load_cover(
            "background",
            size=(WINDOW_WIDTH, WINDOW_HEIGHT)
        )

        if bg is not None:
            self.canvas.create_image(
                0,
                0,
                image=bg,
                anchor= "nw"
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

        guide = self.app.images.load("waiter", size=(220, 280))

        if guide is not None:
            self.canvas.create_image(800, 285, image=guide)
            self.waiter_image = guide

        else:
            self.canvas.create_oval(
                690,
                130,
                830,
                270,
                fill="#fff1c9",
                outline="#5a3a1d",
                width=3
            )

            self.canvas.create_text(
                760,
                205,
                text="給仕係",
                font=("Yu Gothic UI", 20, "bold")
            )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            70,
            text="練習説明",
            font=("Yu Gothic UI", 34, "bold"),
            fill="#2d1c0f",
        )

    def show_message(self):
        self.canvas.delete("message")

        text = PRACTICE_MESSAGES[self.index]

        box, text_id = draw_text_box(
            self.canvas,
            130,
            300,
            text,
            width=560
        )

        self.canvas.itemconfig(box, tags=("message",))
        self.canvas.itemconfig(text_id, tags=("message",))

        button_text = "練習プレイへ" if self.index == len(PRACTICE_MESSAGES) - 1 else "次へ"

        next_btn = make_button(
            self,
            button_text,
            self.next_message,
            width=14,
            font_size=15
        )

        self.canvas.create_window(
            500,
            515,
            window=next_btn,
            tags=("message",)
        )

        back_btn = make_button(
            self,
            "タイトルへ",
            self.app.show_title,
            width=14,
            font_size=15
        )

        self.canvas.create_window(
            500,
            575,
            window=back_btn,
            tags=("message",)
        )

    def next_message(self):
        if self.index >= len(PRACTICE_MESSAGES) - 1:
            self.app.start_practice_game()
            return

        self.index += 1
        self.show_message()