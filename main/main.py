import os
import vlc
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk

class MusicPlayer:
    def __init__(self, master):
        self.master = master
        master.title("Music Player")

        # Tạo giao diện
        self.play_button = ttk.Button(master, text="Play", command=self.play_music)
        self.play_button.pack(pady=10)

        self.pause_button = ttk.Button(master, text="Pause", command=self.pause_music)
        self.pause_button.pack(pady=10)

        self.stop_button = ttk.Button(master, text="Stop", command=self.stop_music)
        self.stop_button.pack(pady=10)

        self.seek_bar = ttk.Scale(master, from_=0, to=100, orient=tk.HORIZONTAL, command=self.seek_music)
        self.seek_bar.pack(pady=10)

        self.time_label = ttk.Label(master, text="00:00 / 00:00")
        self.time_label.pack(pady=10)

        self.lyrics_label = tk.Text(master, wrap=tk.WORD, height=10, width=50)
        self.lyrics_label.pack(pady=10)

        self.instance = vlc.Instance()
        self.player = self.instance.media_player_new()
        self.player.event_manager().event_attach(vlc.EventType.MediaPlayerTimeChanged, self.update_time)

        self.current_media = None
        self.lyrics = []
        self.current_lyric_index = 0

    def play_music(self):
        if self.current_media:
            self.player.play()
            self.update_lyrics()
            self.update_time(None)

    def pause_music(self):
        if self.current_media:
            self.player.pause()

    def stop_music(self):
        if self.current_media:
            self.player.stop()

    def seek_music(self, value):
        if self.current_media:
            position = float(value) / 100
            self.player.set_position(position)

    def update_time(self, event):
        if self.current_media:
            current_time = self.player.get_time() // 1000
            total_time = self.current_media.get_duration() // 1000
            self.time_label.configure(text=f"{self.format_time(current_time)} / {self.format_time(total_time)}")
            self.seek_bar.set(self.player.get_position() * 100)
            self.highlight_lyrics(current_time)

    def format_time(self, seconds):
        return f"{seconds // 60:02d}:{seconds % 60:02d}"

    def update_lyrics(self):
        lyrics_file = "../static/lyric.XML"
        if os.path.exists(lyrics_file):
            try:
                tree = ET.parse(lyrics_file)
                root = tree.getroot()
                self.lyrics = []
                for param in root.iter("param"):
                    line = []
                    for i in param.iter("i"):
                        start_time = float(i.attrib['va'])
                        text = i.text
                        line.append((start_time, text))
                    self.lyrics.append(line)
                self.display_lyrics()
            except ET.ParseError:
                self.lyrics_label.insert(tk.END, "Error parsing lyrics file.")
        else:
            self.lyrics_label.insert(tk.END, "Lyrics not found.")

    def display_lyrics(self):
        self.lyrics_label.delete(1.0, tk.END)
        for line in self.lyrics:
            for start_time, text in line:
                self.lyrics_label.insert(tk.END, text + " ", (start_time,))
            self.lyrics_label.insert(tk.END, "\n")
        self.lyrics_label.tag_configure("highlight", foreground="blue")
        self.lyrics_label.tag_configure("highlight_partial", foreground="lightblue")

    def highlight_lyrics(self, current_time):
        self.lyrics_label.tag_remove("highlight", 1.0, tk.END)
        self.lyrics_label.tag_remove("highlight_partial", 1.0, tk.END)

        for line_index, line in enumerate(self.lyrics):
            start_index = f"{line_index + 1}.0"
            for start_time, text in line:
                if current_time >= start_time:
                    end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1]) + len(text)}"
                    self.lyrics_label.tag_add("highlight", start_index, end_index)
                    start_index = end_index
                else:
                    elapsed_time = current_time - start_time
                    total_time = 0.5  # Thời gian để hoàn tất tô màu một ký tự, có thể điều chỉnh
                    char_index = int((elapsed_time / total_time) * len(text))
                    if char_index < len(text):
                        partial_end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1]) + char_index + 1}"
                        end_index = f"{start_index.split('.')[0]}.{int(start_index.split('.')[1]) + char_index}"
                        self.lyrics_label.tag_add("highlight_partial", start_index, partial_end_index)
                        start_index = end_index
                    break

    def set_media(self, music_file):
        self.current_media = self.instance.media_new(music_file)
        self.player.set_media(self.current_media)


root = tk.Tk()
player = MusicPlayer(root)

# Thay đổi đường dẫn tệp nhạc tùy ý
music_file = "../static/beat.mp3"
player.set_media(music_file)

root.mainloop()
