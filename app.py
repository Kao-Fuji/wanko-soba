
# app.py
# 画面切り替えの中心です。

import tkinter as tk

from setting import WINDOW_WIDTH, WINDOW_HEIGHT
from assets import ImageManager
from ranking import RankingManager

from screen.title import TitleScreen
from screen.practice import PracticeScreen
from screen.game import GameScreen
from screen.minigame import MiniGameScreen
from screen.ranking import RankingScreen


class WankoSobaApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("わんこそば連打ゲーム")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.resizable(False, False)

        self.images = ImageManager()
        self.ranking = RankingManager()

        self.current_screen = None

        self.show_title()

    def clear_screen(self):
        """
        今表示している画面を消す。
        通常の画面切り替えではこれを使う。
        """
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

    def set_screen(self, screen):
        """
        通常の画面切り替え用。
        タイトル、練習、本番、ランキングなどで使う。
        """
        self.clear_screen()
        self.current_screen = screen
        self.current_screen.pack(fill="both", expand=True)

    def show_title(self):
        self.set_screen(TitleScreen(self.root, self))

    def show_practice(self):
        self.set_screen(PracticeScreen(self.root, self))

    def start_practice_game(self):
        self.set_screen(GameScreen(self.root, self, mode="practice"))

    def start_real_game(self):
        self.set_screen(GameScreen(self.root, self, mode="real"))

    def show_ranking(self):
        self.set_screen(RankingScreen(self.root, self))

    def start_minigame(self, game_screen):
        """
        ミニゲーム開始。

        重要：
        ここで set_screen() を使うと、元のゲーム画面が destroy されてしまう。
        だから game_screen は消さずに pack_forget() で一時的に隠すだけにする。
        """
        game_screen.pack_forget()

        mini_screen = MiniGameScreen(self.root, self, game_screen)
        self.current_screen = mini_screen
        self.current_screen.pack(fill="both", expand=True)

    def return_from_minigame(self, game_screen, bonus_seconds, stacked_count):
        """
        ミニゲーム終了後、元のわんこそばゲーム画面に戻る。
        """
        if self.current_screen is not None:
            self.current_screen.destroy()
            self.current_screen = None

        self.current_screen = game_screen
        self.current_screen.pack(fill="both", expand=True)

        game_screen.on_minigame_finished(bonus_seconds, stacked_count)

    def run(self):
        self.root.mainloop()