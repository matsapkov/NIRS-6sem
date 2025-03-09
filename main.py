import tkinter as tk
from tkinter import filedialog
import pygame


class WAVPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("WAV Player")
        pygame.init()
        self.select_button = tk.Button(root, text="Выбрать файл", command=self.select_file)
        self.select_button.pack(pady=10)
        self.play_button = tk.Button(root, text="Воспроизвести", command=self.play, state=tk.DISABLED)
        self.play_button.pack(pady=10)
        self.file_path = None

    def select_file(self):
        self.file_path = filedialog.askopenfilename(filetypes=[("WAV files", "*.wav")])
        if self.file_path:
            self.play_button.config(state=tk.NORMAL)

    def play(self):
        if self.file_path:
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.file_path)
            pygame.mixer.music.play()


if __name__ == "__main__":
    root = tk.Tk()
    player = WAVPlayer(root)
    root.mainloop()