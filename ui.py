
# ui_parts.py
# 複数の画面で使うUI部品をまとめます。

import tkinter as tk


def make_button(parent, text, command, width=18, font_size=16):
    return tk.Button(
        parent,
        text=text,
        command=command,
        width=width,
        font=("Yu Gothic UI", font_size, "bold"),
        bg="#fff6d9",
        activebackground="#ffe29a",
        relief="raised",
        bd=4,
        cursor="hand2",
    )


def make_label(parent, text, font_size=18, bold=True, bg="#fff4cf"):
    weight = "bold" if bold else "normal"

    return tk.Label(
        parent,
        text=text,
        font=("Yu Gothic UI", font_size, weight),
        bg=bg,
        fg="#2f2418",
        padx=12,
        pady=8,
    )


def draw_text_box(canvas, x, y, text, width=420, fill="#fff4cf"):
    """
    Canvas上に簡単な吹き出し風の箱を描く。
    """
    lines = split_text(text, 20)
    line_height = 26
    height = 28 + line_height * len(lines)

    box = canvas.create_rectangle(
        x,
        y,
        x + width,
        y + height,
        fill=fill,
        outline="#5a3a1d",
        width=3,
    )

    text_id = canvas.create_text(
        x + 18,
        y + 18,
        text="\n".join(lines),
        anchor="nw",
        font=("Yu Gothic UI", 15, "bold"),
        fill="#2f2418",
    )

    return box, text_id


def split_text(text, max_chars):
    """
    日本語でもだいたい読みやすい位置で改行するための簡易関数。
    """
    result = []
    current = ""

    for ch in text:
        current += ch

        if len(current) >= max_chars:
            result.append(current)
            current = ""

    if current:
        result.append(current)

    return result