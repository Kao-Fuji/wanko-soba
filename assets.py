
# assets.py
# 画像読み込みを担当するファイルです。
# png / jpg / jpeg に対応。
# 画像が見つからないときは、どこを探したか表示します。

from pathlib import Path
import tkinter as tk

try:
    from PIL import Image, ImageTk, ImageOps
except Exception:
    Image = None
    ImageTk = None
    ImageOps = None


BASE_DIR = Path(__file__).parent
ASSET_DIR = BASE_DIR / "assets"


IMAGE_NAMES = {
    "waiter": [
    "waiter_transparent",
    "waiter_alt_transparent",
    "waiter",
    "給仕",
    "給仕1",
    "kyuji"
    ],
    "arm": [
    "arm_transparent",
    "arm",
    "腕",
    "ude"
    ],
    "background": ["background", "背景", "haikei"],
    "waiter": ["waiter", "給仕", "給仕1", "kyuji"],
    "arm": ["arm", "腕", "ude"],

    "bowl": [
        "bowl_transparent",
        "bowl",
        "owan",
        "お椀",
    ],

    "soba": ["soba", "そば"],
    "udon": ["udon", "うどん"],
    "ramen": ["ramen", "中華麺", "ラーメン"],
    "houtou": ["houtou", "ほうとう"],
    "somen": ["somen", "そうめん"],

    "dark_matter": ["dark_matter", "ダークマター"],
    "rock": ["rock", "岩", "石"],
    "rock_salt": ["rock_salt", "岩塩"],
    "moss": ["moss", "苔"],
    "yakumi": ["yakumi", "薬味", "雑草"],
}


EXTENSIONS = [".png", ".jpg", ".jpeg", ".webp", ".gif"]


class ImageManager:
    def __init__(self):
        self.cache = {}

    def find_path(self, key):
        """
        keyに対応する画像ファイルをassets内から探す。
        例:
        key="soba" のとき
        soba.png, soba.jpg, そば.png, そば.jpg などを探す。
        """
        names = IMAGE_NAMES.get(key, [key])

        for name in names:
            for ext in EXTENSIONS:
                path = ASSET_DIR / f"{name}{ext}"
                if path.exists():
                    return path

        # 完全一致で見つからない場合、ゆるく探す
        if ASSET_DIR.exists():
            for file in ASSET_DIR.iterdir():
                if not file.is_file():
                    continue

                file_stem = file.stem.lower()
                file_ext = file.suffix.lower()

                if file_ext not in EXTENSIONS:
                    continue

                for name in names:
                    if name.lower() in file_stem:
                        return file

        return None

    def load(self, key, size=None):
        path = self.find_path(key)

        if path is None:
            print(f"[画像なし] {key} が見つかりません")
            print(f"探した場所: {ASSET_DIR}")
            return None

        cache_key = (str(path), size)

        if cache_key in self.cache:
            return self.cache[cache_key]

        # Pillowがある場合
        if Image is not None and ImageTk is not None:
            try:
                image = Image.open(path)

                if ImageOps is not None:
                    image = ImageOps.exif_transpose(image)

                image = image.convert("RGBA")

                if size is not None:
                    image.thumbnail(size, Image.LANCZOS)

                photo = ImageTk.PhotoImage(image)
                self.cache[cache_key] = photo

                print(f"[画像OK] {key} -> {path.name}")
                return photo

            except Exception as e:
                print(f"[画像エラー] {key} -> {path}")
                print(e)
                return None

        # Pillowなしの場合
        try:
            photo = tk.PhotoImage(file=str(path))
            self.cache[cache_key] = photo

            print(f"[画像OK] {key} -> {path.name}")
            return photo

        except Exception as e:
            print(f"[画像エラー] {key} -> {path}")
            print("jpg画像なら Pillow が必要です")
            print(e)
            return None
        
    def load_resize(self, key, size):
        """
        背景用。
        画像を指定サイズぴったりにリサイズする。
        """
        path = self.find_path(key)

        if path is None:
            print(f"[画像なし] {key} が見つかりません")
            return None

        cache_key = (str(path), size, "resize")

        if cache_key in self.cache:
            return self.cache[cache_key]

        if Image is None or ImageTk is None:
            return self.load(key, size=size)

        try:
            image = Image.open(path)

            if ImageOps is not None:
                image = ImageOps.exif_transpose(image)

            image = image.convert("RGBA")
            image = image.resize(size, Image.LANCZOS)

            photo = ImageTk.PhotoImage(image)
            self.cache[cache_key] = photo

            print(f"[背景OK] {key} -> {path.name}")
            return photo

        except Exception as e:
            print(f"[背景エラー] {key} -> {path}")
            print(e)
            return None
        
    def load_cover(self, key, size):
        """
        背景用。
        画像を画面いっぱいに広げる。
        縦横比を保ったまま、はみ出す部分は少し切る。
        """
        path = self.find_path(key)

        if path is None:
            print(f"[背景なし] {key} が見つかりません")
            return None

        cache_key = (str(path), size, "cover")

        if cache_key in self.cache:
            return self.cache[cache_key]

        if Image is None or ImageTk is None:
            return self.load(key, size=size)

        try:
            image = Image.open(path)

            if ImageOps is not None:
                image = ImageOps.exif_transpose(image)

            image = image.convert("RGBA")

            # 画面いっぱいにフィットさせる
            image = ImageOps.fit(
                image,
                size,
                method=Image.LANCZOS,
                centering=(0.5, 0.5)
            )

            photo = ImageTk.PhotoImage(image)
            self.cache[cache_key] = photo

            print(f"[背景OK] {key} -> {path.name}")
            return photo

        except Exception as e:
            print(f"[背景エラー] {key} -> {path}")
            print(e)
            return None
        
        