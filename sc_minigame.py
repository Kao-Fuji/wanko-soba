

# minigame.py
# お椀をまっすぐ落とすミニゲーム
#
# 変更点:
# ・お椀は左右に自動移動
# ・「落とす」ボタンを押した位置から落下
# ・成功範囲を狭く設定
# ・お椀ごとに移動速度がランダムで変化
# ・assets/bowl.png の画像を表示
# ・画像がない場合だけ仮の楕円を表示

import random
import tkinter as tk

from setting import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    MINIGAME_BOWLS,
    MINIGAME_GOOD_RANGE,
)
from ui import make_button


class MiniGameScreen(tk.Frame):
    def __init__(self, parent, app, game_screen):
        super().__init__(parent, bg="#d8f2ff")

        self.app = app
        self.game_screen = game_screen

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0,
            bg="#d8f2ff",
        )
        self.canvas.pack(fill="both", expand=True)

        # -------------------------
        # ミニゲームの状態
        # -------------------------

        # 今何個目のお椀か
        self.current_index = 0

        # 成功して積めたお椀の数
        self.stacked_count = 0

        # 現在のお椀の位置
        self.bowl_x = WINDOW_WIDTH // 2
        self.bowl_y = 135

        # 左右に動ける範囲
        self.move_left_limit = 260
        self.move_right_limit = 740

        # 横移動速度
        # spawn_bowl() で、お椀を出すたびにランダムで決める
        self.move_speed = 8

        # 落下速度
        self.drop_speed = 15

        # お椀を積む中心位置
        self.target_x = WINDOW_WIDTH // 2

        # 台の高さ
        self.ground_y = 585

        # 状態
        # "waiting"  : 次のお椀を待っている
        # "moving"   : 左右に移動中
        # "dropping" : 落下中
        # "finished" : 終了
        self.phase = "waiting"

        # after() の予約番号
        self.after_id = None

        # -------------------------
        # お椀画像を読み込む
        # -------------------------

        # assets/bowl.png または
        # assets/bowl_transparent.png を読み込む
        self.bowl_photo = self.app.images.load(
            "bowl",
            size=(120, 60),
        )

        # -------------------------
        # 画面を作る
        # -------------------------

        self.draw_scene()
        self.spawn_bowl()

        # スペースキーでも落とせる
        self.bind_all("<space>", self.drop_bowl)

    # =========================
    # 終了時の片付け
    # =========================

    def destroy(self):
        """
        ミニゲーム画面を閉じるとき、
        残っているアニメーション予約を止める。
        """
        try:
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None
        except Exception:
            pass

        try:
            self.unbind_all("<space>")
        except Exception:
            pass

        super().destroy()

    # =========================
    # 画面全体
    # =========================

    def draw_scene(self):
        """
        ミニゲーム画面の土台を描く。
        """
        self.canvas.delete("all")

        # 背景
        self.canvas.create_rectangle(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            fill="#d8f2ff",
            outline="",
        )

        # タイトル
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            45,
            text="ミニゲーム：お椀をまっすぐ落とせ！",
            font=("Yu Gothic UI", 30, "bold"),
            fill="#203040",
        )

        # 説明
        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            88,
            text="お椀が左右に動くので、中央に来た瞬間に「落とす」を押す",
            font=("Yu Gothic UI", 16, "bold"),
            fill="#203040",
        )

        # 積み重ねる台
        self.canvas.create_rectangle(
            310,
            self.ground_y,
            690,
            self.ground_y + 20,
            fill="#7b4a24",
            outline="#4b2e16",
        )

        # 成功範囲
        # settings.py の MINIGAME_GOOD_RANGE で幅を変更できる
        self.canvas.create_rectangle(
            self.target_x - MINIGAME_GOOD_RANGE,
            145,
            self.target_x + MINIGAME_GOOD_RANGE,
            self.ground_y,
            fill="#cce4ff",
            outline="",
            stipple="gray25",
        )

        # 中心線
        self.canvas.create_line(
            self.target_x,
            140,
            self.target_x,
            self.ground_y,
            fill="#4b7cff",
            width=3,
            dash=(8, 6),
        )

        self.canvas.create_text(
            self.target_x + 15,
            150,
            text="成功範囲",
            anchor="w",
            font=("Yu Gothic UI", 12, "bold"),
            fill="#304070",
        )

        self.draw_stack()
        self.draw_status()
        self.draw_buttons()

    def draw_buttons(self):
        """
        落とすボタンを作る。
        """
        self.canvas.delete("buttons")

        frame = tk.Frame(
            self,
            bg="#d8f2ff",
        )

        self.drop_button = make_button(
            frame,
            "落とす",
            self.drop_bowl,
            width=16,
            font_size=16,
        )
        self.drop_button.pack(
            padx=8,
            pady=4,
        )

        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            650,
            window=frame,
            tags="buttons",
        )

    def draw_status(self):
        """
        左上に進行状況を表示する。
        """
        self.canvas.delete("status")

        self.canvas.create_text(
            85,
            120,
            text=f"{self.current_index}/{MINIGAME_BOWLS}",
            font=("Yu Gothic UI", 20, "bold"),
            fill="#203040",
            tags="status",
        )

        self.canvas.create_text(
            85,
            155,
            text=f"成功: {self.stacked_count}個",
            font=("Yu Gothic UI", 16, "bold"),
            fill="#203040",
            tags="status",
        )

    # =========================
    # お椀描画
    # =========================

    def draw_stack(self):
        """
        すでに積み上がったお椀を描く。
        """
        self.canvas.delete("stack")

        for index in range(self.stacked_count):
            y = self.ground_y - 20 * (index + 1)

            self.draw_bowl(
                self.target_x,
                y,
                tag="stack",
            )

    def draw_current_bowl(self):
        """
        現在動いているお椀を描く。
        """
        self.canvas.delete("moving_bowl")

        self.draw_bowl(
            self.bowl_x,
            self.bowl_y,
            tag="moving_bowl",
        )

    def draw_bowl(self, x, y, tag):
        """
        お椀を1個表示する。

        画像がある場合:
            bowl.png を表示

        画像がない場合:
            仮の楕円を表示
        """
        if self.bowl_photo is not None:
            self.canvas.create_image(
                x,
                y + 15,
                image=self.bowl_photo,
                tags=tag,
            )
            return

        # 写真がまだない場合だけ出る仮のお椀
        self.canvas.create_oval(
            x - 55,
            y,
            x + 55,
            y + 25,
            fill="#fff4cf",
            outline="#4b2e16",
            width=3,
            tags=tag,
        )

        self.canvas.create_oval(
            x - 40,
            y + 4,
            x + 40,
            y + 18,
            fill="#ffd7a3",
            outline="#4b2e16",
            width=2,
            tags=tag,
        )

    # =========================
    # お椀の動き
    # =========================

    def spawn_bowl(self):
        """
        新しいお椀を出す。

        お椀を出すたびに、
        横移動速度と開始方向をランダムに変更する。
        """
        if self.current_index >= MINIGAME_BOWLS:
            self.finish()
            return

        self.current_index += 1

        self.bowl_y = 135

        # -------------------------
        # 速度をランダムにする
        # -------------------------

        # 遅い皿から速い皿までランダム
        random_speed = random.choice([
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
        ])

        # 左右どちらから始まるかもランダム
        start_from_left = random.choice([
            True,
            False,
        ])

        if start_from_left:
            self.bowl_x = self.move_left_limit
            self.move_speed = random_speed
        else:
            self.bowl_x = self.move_right_limit
            self.move_speed = -random_speed

        self.phase = "moving"

        self.draw_status()
        self.animate_moving()

    def animate_moving(self):
        """
        お椀を左右に自動移動させる。
        """
        if self.phase != "moving":
            return

        self.bowl_x += self.move_speed

        # 左端に来たら右へ折り返す
        if self.bowl_x <= self.move_left_limit:
            self.bowl_x = self.move_left_limit
            self.move_speed = abs(self.move_speed)

        # 右端に来たら左へ折り返す
        if self.bowl_x >= self.move_right_limit:
            self.bowl_x = self.move_right_limit
            self.move_speed = -abs(self.move_speed)

        self.draw_current_bowl()

        self.after_id = self.after(
            25,
            self.animate_moving,
        )

    def drop_bowl(self, event=None):
        """
        「落とす」ボタンを押したとき、
        左右移動を止めて下に落とす。
        """
        if self.phase != "moving":
            return

        self.phase = "dropping"

        try:
            if self.after_id is not None:
                self.after_cancel(self.after_id)
                self.after_id = None
        except Exception:
            pass

        self.animate_dropping()

    def animate_dropping(self):
        """
        お椀を下へ落とす。
        """
        if self.phase != "dropping":
            return

        self.bowl_y += self.drop_speed

        landing_y = (
            self.ground_y
            - 20 * self.stacked_count
            - 25
        )

        if self.bowl_y >= landing_y:
            self.bowl_y = landing_y

            self.draw_current_bowl()
            self.check_landing()
            return

        self.draw_current_bowl()

        self.after_id = self.after(
            25,
            self.animate_dropping,
        )

    def check_landing(self):
        """
        中心からどれくらい離れているか確認する。
        成功範囲内なら積み重なる。
        """
        self.phase = "waiting"

        distance = abs(
            self.bowl_x - self.target_x
        )

        if distance <= MINIGAME_GOOD_RANGE:
            self.stacked_count += 1

            self.canvas.delete("moving_bowl")
            self.draw_stack()
            self.show_small_message("成功！")

        else:
            self.canvas.delete("moving_bowl")
            self.show_small_message("ずれた！")

        self.draw_status()

        self.after_id = self.after(
            500,
            self.spawn_bowl,
        )

    def show_small_message(self, text):
        """
        成功・失敗メッセージを一時表示する。
        """
        self.canvas.delete("mini_message")

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            205,
            text=text,
            font=("Yu Gothic UI", 28, "bold"),
            fill="#203040",
            tags="mini_message",
        )

        self.after(
            400,
            lambda: self.canvas.delete("mini_message"),
        )

    # =========================
    # ボーナス計算
    # =========================

    def calc_bonus(self):
        """
        積めた数によって、
        元のゲームへ追加する時間を決める。
        """
        if self.stacked_count == 10:
            return 20

        if 5 <= self.stacked_count <= 9:
            return self.stacked_count + 5

        return self.stacked_count

    # =========================
    # ミニゲーム終了
    # =========================

    def finish(self):
        """
        10個のお椀が流れ終わったら結果を表示する。
        """
        self.phase = "finished"

        bonus = self.calc_bonus()

        self.canvas.delete("all")

        self.canvas.create_rectangle(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            fill="#d8f2ff",
            outline="",
        )

        self.canvas.create_rectangle(
            250,
            170,
            750,
            480,
            fill="#fff4cf",
            outline="#4b2e16",
            width=4,
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            235,
            text="ミニゲーム終了！",
            font=("Yu Gothic UI", 34, "bold"),
            fill="#203040",
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            320,
            text=(
                f"積めたお椀: {self.stacked_count}個\n"
                f"ボーナスタイム: +{bonus}秒"
            ),
            font=("Yu Gothic UI", 24, "bold"),
            fill="#203040",
            justify="center",
        )

        back_button = make_button(
            self,
            "ゲームに戻る",
            lambda: self.app.return_from_minigame(
                self.game_screen,
                bonus,
                self.stacked_count,
            ),
            width=14,
            font_size=15,
        )

        self.canvas.create_window(
            WINDOW_WIDTH // 2,
            410,
            window=back_button,
        )