
import time
import tkinter as tk

from setting import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    PRACTICE_SECONDS,
    REAL_SECONDS,
    COUNTDOWN_SECONDS,
    EFFECT_TURNS,
    BOWLS_TO_TRIGGER_MINIGAME,
    TIMER_INTERVAL_MS,
)
from items import choose_random_item, calc_required_clicks
from ui import make_button


class GameScreen(tk.Frame):
    def __init__(self, parent, app, mode="real"):
        super().__init__(parent, bg="#f6d28b")

        self.app = app
        self.mode = mode

        self.canvas = tk.Canvas(
            self,
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)

        # ゲーム状態
        self.score = 0
        self.total_bowls = 0
        self.bowls_since_minigame = 0
        self.bowl_log = []

        self.active_effect = None
        self.effect_turns_left = 0

        self.current_item = None
        self.required_clicks = 0
        self.current_clicks = 0

        self.running = False
        self.game_over = False
        self.paused_for_minigame = False

        self.time_left = PRACTICE_SECONDS if mode == "practice" else REAL_SECONDS
        self.time_limit_base = PRACTICE_SECONDS if mode == "practice" else REAL_SECONDS
        self.time_bar_max = self.time_limit_base
        self.end_time = None

        self.after_id = None
        self.countdown_value = COUNTDOWN_SECONDS

        self.draw_static_scene()

        if self.mode == "real":
            self.start_countdown()
        else:
            self.start_game()

    # =========================
    # 描画
    # =========================

    def draw_static_scene(self):
        self.canvas.delete("all")
        self.draw_background()
        self.draw_waiter()
        self.draw_left_bowls()
        self.draw_hud()

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
                anchor = "nw",
                tags="bg"
            )
            self.bg_image = bg

        else:
            self.canvas.create_rectangle(
                0,
                0,
                WINDOW_WIDTH,
                WINDOW_HEIGHT,
                fill="#f4c06a",
                outline="",
                tags="bg"
            )

            self.canvas.create_rectangle(
                0,
                520,
                WINDOW_WIDTH,
                WINDOW_HEIGHT,
                fill="#8b5a2b",
                outline="",
                tags="bg"
            )

            self.canvas.create_text(
                WINDOW_WIDTH // 2,
                60,
                text="背景画像がないので仮背景です",
                font=("Yu Gothic UI", 16, "bold"),
                fill="#5a3a1d",
                tags="bg",
            )

    def draw_waiter(self):
        waiter = self.app.images.load("waiter", size=(210, 270))

        if waiter is not None:
            self.canvas.create_image(
                790,
                245,
                image=waiter,
                tags="waiter"
            )
            self.waiter_image = waiter

        else:
            self.canvas.create_oval(
                720,
                120,
                860,
                260,
                fill="#fff1c9",
                outline="#5a3a1d",
                width=3,
                tags="waiter"
            )

            self.canvas.create_rectangle(
                725,
                260,
                855,
                420,
                fill="#f0a24a",
                outline="#5a3a1d",
                width=3,
                tags="waiter"
            )

            self.canvas.create_text(
                790,
                195,
                text="給仕係",
                font=("Yu Gothic UI", 18, "bold"),
                tags="waiter"
            )

    def draw_arm(self):
        arm = self.app.images.load("arm", size=(650, 180))

        if arm is not None:
            self.canvas.create_image(
                530,
                615,
                image=arm,
                tags="arm"
            )
            self.arm_image = arm

        else:
            self.canvas.create_rectangle(
                300,
                585,
                760,
                675,
                fill="#f3c49a",
                outline="#8a5a35",
                width=3,
                tags="arm"
            )

            self.canvas.create_text(
                530,
                625,
                text="自分の腕（仮）",
                font=("Yu Gothic UI", 16, "bold"),
                tags="arm"
            )

    def draw_hud(self):
        self.canvas.delete("hud")

        mode_label = "練習" if self.mode == "practice" else "本番"

        # HUD背景
        self.canvas.create_rectangle(
            230,
            15,
            780,
            100,
            fill="#fff4cf",
            outline="#5a3a1d",
            width=3,
            tags="hud"
        )

        # モード・杯数
        self.canvas.create_text(
            255,
            35,
            text=f"モード: {mode_label}　杯数: {self.total_bowls}",
            anchor="w",
            font=("Yu Gothic UI", 15, "bold"),
            fill="#2f2418",
            tags="hud",
        )

        # 残り時間文字
        remain = max(0, int(self.time_left))
        self.canvas.create_text(
            255,
            62,
            text=f"残り {remain} 秒",
            anchor="w",
            font=("Yu Gothic UI", 15, "bold"),
            fill="#2f2418",
            tags="hud",
        )

        # 時間ゲージ
        bar_x = 380
        bar_y = 60
        bar_w = 360
        bar_h = 18

        self.canvas.create_rectangle(
            bar_x,
            bar_y,
            bar_x + bar_w,
            bar_y + bar_h,
            fill="#ddd0aa",
            outline="#5a3a1d",
            width=2,
            tags="hud"
        )

        ratio = 0

        if self.time_bar_max > 0:
            ratio = max(0, min(1, self.time_left / self.time_bar_max))

        fill_w = int(bar_w * ratio)

        # 残り時間が多いほど長い線
        self.canvas.create_rectangle(
            bar_x,
            bar_y,
            bar_x + fill_w,
            bar_y + bar_h,
            fill="#ffb84d",
            outline="",
            tags="hud"
        )

        # 効果表示
        effect_text = "効果: なし"

        if self.active_effect is not None:
            effect_text = f"効果: {self.active_effect['label']} / 残り{self.effect_turns_left}皿"

        self.canvas.create_text(
            255,
            88,
            text=effect_text,
            anchor="w",
            font=("Yu Gothic UI", 12, "bold"),
            fill="#2f2418",
            tags="hud",
        )

    
    def draw_left_bowls(self):
        self.canvas.delete("bowls")

        self.canvas.create_rectangle(
            20,
            100,
            190,
            640,
            fill="#fff4cf",
            outline="#5a3a1d",
            width=3,
            tags="bowls"
        )

        self.canvas.create_text(
            105,
            125,
            text="お椀",
            font=("Yu Gothic UI", 17, "bold"),
            tags="bowls"
        )

        display_bowls = self.bowl_log[-60:]

        start_x = 45
        start_y = 165
        gap_x = 36
        gap_y = 35

        for index, color in enumerate(display_bowls):
            col = index % 4
            row = index // 4

            x = start_x + col * gap_x
            y = start_y + row * gap_y

            self.canvas.create_oval(
                x,
                y,
                x + 28,
                y + 18,
                fill=color,
                outline="#4b2e16",
                width=2,
                tags="bowls"
            )

            self.canvas.create_arc(
                x,
                y - 6,
                x + 28,
                y + 18,
                start=180,
                extent=180,
                style="arc",
                width=2,
                tags="bowls"
            )

    def draw_item_area(self):
        """ 食べ物・危険物・効果アイテムを表示する。お椀の写真を大きく表示し、
    その上に現在のアイテム画像を載せる。
    """

        self.canvas.delete("item")
        self.canvas.delete("item_buttons")

        if self.current_item is None:
            return

    # =====================================
    # 給仕係の説明
    # =====================================

        speech = f"次は {self.current_item.name}！"

        if self.current_item.category == "noodle":
            speech += f"\n{self.required_clicks}回クリックで食べる！"

        elif self.current_item.category == "bad":
            speech += "\nこれは食べちゃダメ！"

        else:
            speech += "\n食べると効果発動！"

        self.canvas.create_rectangle(
        580,
        80,
        970,
        170,
        fill="#fff4cf",
        outline="#5a3a1d",
        width=3,
        tags="item",
    )

        self.canvas.create_text(
        600,
        100,
        text=speech,
        anchor="nw",
        font=("Yu Gothic UI", 15, "bold"),
        fill="#2f2418",
        tags="item",
    )

    # =====================================
    # 大きめのお椀写真
    # =====================================

        bowl_photo = self.app.images.load(
        "bowl",
        size=(420, 260),
    )

        if bowl_photo is not None:
            self.canvas.create_image(
            500,
            390,
            image=bowl_photo,
            tags="item",
        )

        # Tkinterで画像が消えないように保存
            self.bowl_image = bowl_photo

        else:
        # お椀画像がないときだけ仮のお椀を表示
            self.canvas.create_oval(
            315,
            335,
            685,
            455,
            fill="#d9a46c",
            outline="#4b2e16",
            width=4,
            tags="item",
        )

            self.canvas.create_oval(
            350,
            350,
            650,
            430,
            fill="#fff6dc",
            outline="#4b2e16",
            width=3,
            tags="item",
        )

    # =====================================
    # お椀の上にアイテム写真を表示
    # =====================================

        item_photo = self.app.images.load(
        self.current_item.key,
        size=(220, 145),
    )

        if item_photo is not None:
            self.canvas.create_image(
            500,
            335,
            image=item_photo,
            tags="item",
        )

        # Tkinterで画像が消えないように保存
            self.current_item_image = item_photo

        else:
        # 写真がない場合だけ簡易表示
            self.canvas.create_text(
            500,
            335,
            text=self.current_item.name,
            font=("Yu Gothic UI", 24, "bold"),
            fill="#2f2418",
            tags="item",
        )

    # =====================================
    # クリック数などの表示
    # =====================================

        if self.current_item.category == "noodle":
            click_text = f"{self.current_clicks} / {self.required_clicks}"

        elif self.current_item.category == "bad":
            click_text = "食べちゃダメ！"

        else:
            click_text = "効果アイテム"

        self.canvas.create_text(
        500,
        475,
        text=click_text,
        font=("Yu Gothic UI", 21, "bold"),
        fill="#2f2418",
        tags="item",
    )

    # =====================================
    # ボタン
    # =====================================

        eat_button = make_button(
        self,
        "食べる",
        self.on_eat_clicked,
        width=12,
        font_size=15,
    )

        no_eat_button = make_button(
        self,
        "食べない",
        self.on_no_eat_clicked,
        width=12,
        font_size=15,
    )

        self.canvas.create_window(
        500,
        520,
        window=eat_button,
        tags="item_buttons",
    )

        self.canvas.create_window(
        500,
        580,
        window=no_eat_button,
        tags="item_buttons",
    )

    def draw_fallback_item(self):
        item = self.current_item

        if item.category == "bad":
            if item.key == "dark_matter":
                self.canvas.create_oval(
                    430,
                    275,
                    580,
                    355,
                    fill="#1a1029",
                    outline="#8421ff",
                    width=5,
                    tags="item"
                )

                self.canvas.create_text(
                    505,
                    315,
                    text="闇",
                    font=("Yu Gothic UI", 38, "bold"),
                    fill="#fff",
                    tags="item"
                )

            else:
                self.canvas.create_polygon(
                    450,
                    345,
                    485,
                    280,
                    555,
                    275,
                    585,
                    350,
                    fill="#777",
                    outline="#333",
                    width=4,
                    tags="item"
                )

                self.canvas.create_text(
                    515,
                    320,
                    text="岩",
                    font=("Yu Gothic UI", 28, "bold"),
                    fill="#fff",
                    tags="item"
                )

            return

        if item.category == "effect":
            self.canvas.create_oval(
                440,
                270,
                570,
                360,
                fill=item.bowl_color,
                outline="#4b2e16",
                width=4,
                tags="item"
            )

            self.canvas.create_text(
                505,
                315,
                text=item.name,
                font=("Yu Gothic UI", 24, "bold"),
                fill="#2f2418",
                tags="item"
            )

            return

        for i in range(7):
            y = 285 + i * 10

            self.canvas.create_line(
                415,
                y,
                595,
                y + 18,
                fill=item.bowl_color,
                width=5,
                tags="item"
            )

        self.canvas.create_text(
            505,
            323,
            text=item.name,
            font=("Yu Gothic UI", 23, "bold"),
            fill="#2f2418",
            tags="item"
        )

    # =========================
    # 開始・タイマー
    # =========================

    def start_countdown(self):
        self.running = False
        self.canvas.delete("countdown")

        self.canvas.create_rectangle(
            0,
            0,
            WINDOW_WIDTH,
            WINDOW_HEIGHT,
            fill="#000000",
            stipple="gray50",
            tags="countdown"
        )

        self.canvas.create_text(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2,
            text=str(self.countdown_value),
            font=("Yu Gothic UI", 80, "bold"),
            fill="#ffffff",
            tags="countdown",
        )

        if self.countdown_value <= 0:
            self.canvas.delete("countdown")
            self.start_game()
            return

        self.countdown_value -= 1
        self.after(1000, self.start_countdown)

    def start_game(self):
        self.running = True
        self.game_over = False
        self.end_time = time.monotonic() + self.time_left

        self.next_item()
        self.update_timer()

    def update_timer(self):
        if not self.running or self.game_over or self.paused_for_minigame:
            return

        self.time_left = self.end_time - time.monotonic()

        if self.time_left <= 0:
            self.time_left = 0
            self.finish_game()
            return

        self.draw_hud()
        self.after_id = self.after(TIMER_INTERVAL_MS, self.update_timer)

    # =========================
    # アイテム処理
    # =========================

    def next_item(self):
        if self.game_over or not self.running:
            return

        self.current_item = choose_random_item()
        self.current_clicks = 0
        self.required_clicks = calc_required_clicks(
            self.current_item,
            self.active_effect
        )

        self.draw_item_area()
        self.draw_hud()

    def on_eat_clicked(self):
        if not self.running or self.game_over or self.current_item is None:
            return

        item = self.current_item

        if item.category == "noodle":
            self.current_clicks += 1

            if self.current_clicks >= self.required_clicks:
                self.eat_noodle_success(item)
            else:
                self.draw_item_area()

            return

        if item.category == "bad":
            self.handle_bad_item(item)
            return

        if item.category == "effect":
            self.apply_effect_item(item)
            self.next_item()
            return

    def on_no_eat_clicked(self):
        if not self.running or self.game_over or self.current_item is None:
            return

        item = self.current_item

        if item.category == "bad":
            self.show_message("回避成功！")

        elif item.category == "noodle":
            self.show_message(f"{item.name}を見送った")

        else:
            self.show_message(f"{item.name}を使わなかった")

        self.next_item()

    def eat_noodle_success(self, item):
        self.total_bowls += 1
        self.score = self.total_bowls
        self.bowls_since_minigame += 1
        self.bowl_log.append(item.bowl_color)

        self.reduce_effect_turn_if_needed()
        self.draw_left_bowls()
        self.draw_hud()

        if self.bowls_since_minigame >= BOWLS_TO_TRIGGER_MINIGAME:
            self.bowls_since_minigame = 0
            self.start_minigame()
            return

        self.next_item()

    def reduce_effect_turn_if_needed(self):
        if self.active_effect is None:
            return

        self.effect_turns_left -= 1

        if self.effect_turns_left <= 0:
            self.active_effect = None
            self.effect_turns_left = 0

    def handle_bad_item(self, item):
        if item.penalty == "game_over":
            self.show_message("ダークマターを食べた！ 一発アウト！")
            self.finish_game(force_message="ダークマターを食べてしまった……")
            return

        if item.penalty == "minus_bowls":
            lose = min(3, self.total_bowls)
            self.total_bowls -= lose
            self.score = self.total_bowls

            if lose > 0:
                self.bowl_log = self.bowl_log[:-lose]

            self.show_message(f"岩を食べた！ お椀が{lose}個減った！")
            self.draw_left_bowls()
            self.next_item()
            return

        self.next_item()

    def apply_effect_item(self, item):
        if item.effect_type == "multiply":
            self.active_effect = {
                "type": "multiply",
                "value": item.effect_value,
                "label": f"{item.name}: クリック×{item.effect_value}",
            }

            self.effect_turns_left = EFFECT_TURNS
            self.show_message(
                f"{item.name}発動！ 次の{EFFECT_TURNS}皿はクリック×{item.effect_value}"
            )

        elif item.effect_type == "one_click":
            self.active_effect = {
                "type": "one_click",
                "value": 1,
                "label": f"{item.name}: 全部1回",
            }

            self.effect_turns_left = EFFECT_TURNS
            self.show_message(
                f"{item.name}発動！ 次の{EFFECT_TURNS}皿は全部1回"
            )

    def show_message(self, text):
        self.canvas.delete("floating_message")

        self.canvas.create_rectangle(
            310,
            105,
            690,
            155,
            fill="#fff4cf",
            outline="#5a3a1d",
            width=3,
            tags="floating_message"
        )

        self.canvas.create_text(
            500,
            130,
            text=text,
            font=("Yu Gothic UI", 15, "bold"),
            fill="#2f2418",
            tags="floating_message",
        )

        self.after(
            650,
            lambda: self.canvas.delete("floating_message")
        )

    # =========================
    # ミニゲーム
    # =========================

    def start_minigame(self):
        self.paused_for_minigame = True
        self.running = False
        self.time_left = max(0, self.end_time - time.monotonic())


        self.app.start_minigame(self)

    def on_minigame_finished(self, bonus_seconds, stacked_count):
        self.paused_for_minigame = False
        self.running = True

        self.time_left += bonus_seconds
        self.time_bar_max += bonus_seconds
        self.end_time = time.monotonic() + self.time_left

        self.show_message(
            f"ミニゲーム成功 {stacked_count}個！ +{bonus_seconds}秒"
        )

        self.draw_static_scene()
        self.next_item()
        self.update_timer()

    # =========================
    # 終了
    # =========================

    def finish_game(self, force_message=None):
        if self.game_over:
            return

        self.running = False
        self.game_over = True

        self.canvas.delete("item_buttons")
        self.canvas.delete("item")

        rank = None
        total_people = None

        if self.mode == "real":
            rank, total_people = self.app.ranking.add_score(
                self.score,
                mode="本番"
            )

        self.canvas.create_rectangle(
            220,
            150,
            780,
            560,
            fill="#fff4cf",
            outline="#5a3a1d",
            width=4,
            tags="result"
        )

        title = "結果発表"

        if force_message:
            title = "ゲーム終了"

        self.canvas.create_text(
            500,
            210,
            text=title,
            font=("Yu Gothic UI", 34, "bold"),
            fill="#2f2418",
            tags="result",
        )

        result_lines = []

        if force_message:
            result_lines.append(force_message)

        result_lines.append(f"あなたの記録: {self.score}杯")

        if self.mode == "real":
            result_lines.append(f"あなたは {total_people}人中 {rank}位 です。")
        else:
            result_lines.append("練習モードなのでランキングには登録されません。")

        self.canvas.create_text(
            500,
            300,
            text="\n".join(result_lines),
            font=("Yu Gothic UI", 22, "bold"),
            fill="#2f2418",
            justify="center",
            tags="result",
        )

        btn_frame = tk.Frame(self, bg="#fff4cf")
        self.canvas.create_window(
            500,
            450,
            window=btn_frame,
            tags="result"
        )

        make_button(
            btn_frame,
            "もう一度",
            self.restart_same_mode,
            width=12,
            font_size=14
        ).pack(side="left", padx=8)

        make_button(
            btn_frame,
            "ランキング",
            self.app.show_ranking,
            width=12,
            font_size=14
        ).pack(side="left", padx=8)

        make_button(
            btn_frame,
            "タイトル",
            self.app.show_title,
            width=12,
            font_size=14
        ).pack(side="left", padx=8)

    def restart_same_mode(self):
        if self.mode == "practice":
            self.app.start_practice_game()
        else:
            self.app.start_real_game()