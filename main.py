import configparser
import datetime
import math
import os
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

import CTkMenuBar
import customtkinter as ctk
import pyperclip
import yt_dlp
from win11toast import toast


class App(ctk.CTk):
    config = configparser.ConfigParser()
    ini_path = "config.ini"

    def __init__(self):
        super().__init__()

        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")
        self.fonts = ("游ゴシック", 15)
        self.title("yt-dlp_GUI")
        self.geometry("800x300")

        self.create_menu()
        self.read_config()
        self.setup()

        self.opt = {
            "progress_hooks": [self.progress_hook],
            "postprocessor_hooks": [self.postprocessor_hook],
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
        }

        # メニューバーを追加

    def create_menu(self):
        menu = CTkMenuBar.CTkMenuBar(self)
        self.pack_propagate(0)
        # File menu
        file_menu = menu.add_cascade("開く")
        file_dropdown = CTkMenuBar.CustomDropdownMenu(file_menu, font=self.fonts)
        file_dropdown.add_option(
            "YouTubeを開く",
            command=lambda: subprocess.run("start https://youtube.com", shell=True),
        )
        file_dropdown.add_separator()

        # メニューバーのテンプレート
        """
        export_submenu = file_dropdown.add_submenu("Export As")
        export_submenu.add_option(".TXT")
        export_submenu.add_option(".PDF")

        # Edit menu
        edit_menu = menu.add_cascade("Edit")
        edit_dropdown = CustomDropdownMenu(edit_menu)
        edit_dropdown.add_option("Cut")
        edit_dropdown.add_option("Copy")
        edit_dropdown.add_option("Paste")

        # Settings menu
        settings_menu = menu.add_cascade("Settings")
        settings_dropdown = CustomDropdownMenu(settings_menu)
        settings_dropdown.add_option("Preferences")
        settings_dropdown.add_option("Update")

        # About menu
        about_menu = menu.add_cascade("About")
        about_dropdown = CustomDropdownMenu(about_menu)
        about_dropdown.add_option("Hello World")
        """

    def read_config(self):
        if not os.path.exists(self.ini_path):
            with open(self.ini_path, "w") as f:
                self.config["Directory"] = {}
                self.config["Directory"]["lastdir"] = ""
                self.config.write(f)
        self.config.read(self.ini_path, encoding="shift-jis")

    def write_config(self, section, key, value):
        self.config.set(section, key, str(value))
        with open(self.ini_path, "w") as f:
            self.config.write(f)

    def setup(self):

        self.frame_main = ctk.CTkFrame(self, width=540)
        self.frame_main.grid(row=0, column=0, padx=10, pady=35, sticky="nsew")

        self.frame_option = ctk.CTkFrame(self, width=360)
        self.frame_option.grid(row=0, column=1, padx=10, pady=35, sticky="nsew")

        self.frame_progress = ctk.CTkFrame(self, width=920)
        self.frame_progress.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew"
        )
        self.rowconfigure(1, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.frame_main.columnconfigure(0, weight=1)

        self.frame_progress.columnconfigure(0, weight=1)

        self.ent_url = ctk.CTkEntry(
            self.frame_main, width=400, placeholder_text="URL", font=self.fonts
        )
        self.ent_url.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.btn_paste = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="ペースト",
            command=self.paste,
            font=self.fonts,
        )
        self.btn_paste.grid(
            row=0,
            column=1,
            padx=10,
            pady=10,
        )

        self.ent_savedir = ctk.CTkEntry(
            self.frame_main,
            width=400,
            placeholder_text="保存先フォルダ",
            font=self.fonts,
        )
        self.ent_savedir.grid(row=1, column=0, padx=10, pady=10, sticky="ew")
        if self.config["Directory"]["lastdir"] != "":
            self.ent_savedir.insert(0, self.config["Directory"]["lastdir"])

        self.btn_savedir = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="参照",
            command=self.savedir,
            font=self.fonts,
        )
        self.btn_savedir.grid(row=1, column=1, padx=10, pady=10)

        self.ent_filename = ctk.CTkEntry(
            self.frame_main,
            placeholder_text="保存ファイル名(空白ならタイトル)",
            width=400,
            font=self.fonts,
        )
        self.ent_filename.grid(row=2, column=0, padx=10, pady=10, sticky="ew")

        self.btn_download = ctk.CTkButton(
            self.frame_main,
            width=100,
            text="ダウンロード",
            command=self.start_download,
            font=self.fonts,
        )
        self.btn_download.grid(row=2, column=1, padx=10, pady=10)

        self.chk_audio = ctk.CTkCheckBox(
            self.frame_option, text="音声のみダウンロード", font=self.fonts
        )
        self.chk_audio.grid(row=0, column=0, padx=10, pady=10, sticky="w")

        self.lbl_progress = ctk.CTkLabel(self.frame_progress, text="", font=self.fonts)
        self.lbl_progress.grid(row=0, column=0, padx=10, sticky="w")

        self.lbl_eta = ctk.CTkLabel(self.frame_progress, text="", font=self.fonts)
        self.lbl_eta.grid(row=0, column=1, padx=10, sticky="e")

        self.pbar_progress = ctk.CTkProgressBar(self.frame_progress, width=920)
        self.pbar_progress.grid(
            row=1, column=0, columnspan=2, padx=10, pady=10, sticky="ew"
        )
        self.pbar_progress.set(0)

    def paste(self):
        clip_text = pyperclip.paste()
        self.ent_url.delete(0, tk.END)
        self.ent_url.insert(0, clip_text)

    def savedir(self):
        inidir = self.config["Directory"]["lastdir"]
        file_path = filedialog.askdirectory(initialdir=inidir)
        self.write_config("Directory", "lastdir", file_path)
        self.ent_savedir.delete(0, tk.END)
        self.ent_savedir.insert(0, file_path)

    def start_download(self):
        file_path = self.ent_savedir.get()
        file_name = self.ent_filename.get()
        url = self.ent_url.get()

        if url == "":
            messagebox.showerror("エラー", "URLを入力してください")
            return
        if file_path == "":
            messagebox.showerror("エラー", "保存フォルダを指定してください")
            return
        if file_name == "":
            file_name = "%(title)s"

        download_audio = self.chk_audio.get()

        if download_audio:
            self.opt["postprocessors"] = [
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                }
            ]
            self.opt["format"] = "bestaudio/best"

        self.opt["outtmpl"] = file_path + "/" + file_name + ".%(ext)s"
        self.download_finished = 1 if download_audio else 2
        self.thread = threading.Thread(target=self.download, args=(url,))
        self.thread.start()

    def download(self, url):
        self.pbar_progress.set(0)
        self.lbl_progress.configure(text="準備中")
        self.lbl_eta.configure(text="")
        with yt_dlp.YoutubeDL(self.opt) as ydl:
            ydl.download([url])

    def progress_hook(self, d):
        if d["status"] == "downloading":
            self.set_progress(
                self.download_finished,
                d.get("downloaded_bytes", None),
                d.get("total_bytes_estimate", None),
                d.get("speed", None),
                d.get("eta", None),
            )

        elif d["status"] == "finished":
            self.download_finished -= 1

    def set_progress(self, downloading, downloaded_bytes, total_bytes, speed, eta):
        if downloading == 2:
            downloading_text = "動画"
        else:
            downloading_text = "音声"

        if total_bytes is None:
            total_bytes = downloaded_bytes

        self.lbl_progress.configure(
            text=(
                downloading_text
                + "をダウンロード中："
                + str(round((downloaded_bytes / total_bytes * 100), 1))
                + "% / "
                + self.convert_size(total_bytes)
                + " ("
                + (self.convert_size(speed) if speed is not None else "...")
                + "/s)"
            )
        )
        if eta is None:
            eta = "..."
        else:
            eta = str(datetime.timedelta(seconds=round(float(eta))))
        self.lbl_eta.configure(text="残り " + eta)
        self.pbar_progress.set(downloaded_bytes / total_bytes)

    def convert_size(self, size):
        units = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB")
        i = math.floor(math.log(size, 1024)) if size > 0 else 0
        size = round(size / 1024**i, 2)
        return f"{size} {units[i]}"

    def postprocessor_hook(self, d):
        if d["status"] == "started":
            self.lbl_progress.configure(text="処理中")
            self.lbl_eta.configure(text="")

        elif d["status"] == "finished":
            if d["postprocessor"] == "MoveFiles":
                self.lbl_progress.configure(text="ダウンロード完了")
                self.lbl_eta.configure(text="")
                toast("yt-dlp_GUI", "ダウンロードが完了しました")


app = App()
app.mainloop()
