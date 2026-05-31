
# make_transparent.py
# 白背景を透明にしたpngを作るファイル
#
# 使い方:
# python make_transparent.py

from pathlib import Path
from PIL import Image


ASSET_DIR = Path(__file__).parent / "assets"


TARGETS = [
    "waiter.png",
    "waiter.jpg",
    "waiter.jpeg",
    "waiter_alt.png",
    "waiter_alt.jpg",
    "arm.png",
    "arm.jpg",
]


def white_to_transparent(input_path, output_path, threshold=245):
    image = Image.open(input_path).convert("RGBA")
    pixels = image.load()

    width, height = image.size

    for y in range(height):
        for x in range(width):
            r, g, b, a = pixels[x, y]

            # 白っぽい部分を透明にする
            if r >= threshold and g >= threshold and b >= threshold:
                pixels[x, y] = (255, 255, 255, 0)

    image.save(output_path)
    print(f"作成: {output_path.name}")


def main():
    if not ASSET_DIR.exists():
        print("assetsフォルダがありません")
        return

    found = False

    for name in TARGETS:
        input_path = ASSET_DIR / name

        if not input_path.exists():
            continue

        found = True
        output_name = input_path.stem + "_transparent.png"
        output_path = ASSET_DIR / output_name

        white_to_transparent(input_path, output_path)

    if not found:
        print("透過したい画像が見つかりませんでした")
        print("waiter.png / waiter.jpg / waiter_alt.png などをassetsに入れてください")


if __name__ == "__main__":
    main()