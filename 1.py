import sys
import numpy as np
import sounddevice as sd
import scipy.signal as signal
import wave
from PyQt6.QtWidgets import QApplication, QSlider, QPushButton, QFileDialog, QVBoxLayout, QWidget, QLabel
from PyQt6.QtCore import Qt

# Определяем частоты полос
bands = [(20, 100), (100, 500), (500, 2000), (2000, 5000), (5000, 10000)]  # 5 полос
highpass_cutoff = 10000  # Граница для ВЧ-фильтра
gain_values = [0] * 6  # Начальные усиления


def butter_bandpass(lowcut, highcut, fs, order=4):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a


def butter_highpass(cutoff, fs, order=4):
    nyq = 0.5 * fs
    high = cutoff / nyq
    b, a = signal.butter(order, high, btype='high')
    return b, a


def apply_equalizer(audio, fs):
    global gain_values
    filtered_audio = np.zeros_like(audio, dtype=np.float32)

    for i, (low, high) in enumerate(bands):
        b, a = butter_bandpass(low, high, fs)
        band_signal = signal.lfilter(b, a, audio) * (10 ** (gain_values[i] / 20))
        band_signal = np.nan_to_num(np.clip(band_signal, -1.0, 1.0))  # Ограничение амплитуды
        filtered_audio += band_signal

    # Фильтр высоких частот
    b, a = butter_highpass(highpass_cutoff, fs)
    high_signal = signal.lfilter(b, a, audio) * (10 ** (gain_values[-1] / 20))
    high_signal = np.nan_to_num(np.clip(high_signal, -1.0, 1.0))
    filtered_audio += high_signal

    # Проверка на NaN и бесконечные значения
    if np.isnan(filtered_audio).any() or np.isinf(filtered_audio).any():
        print("Ошибка: В аудиосигнале появились NaN или бесконечности!")
        filtered_audio = np.zeros_like(audio)  # Заполняем нулями, чтобы избежать аварийного завершения

    # Ограничение и нормализация
    filtered_audio = np.clip(filtered_audio, -1.0, 1.0)
    print(f"Мин. значение: {filtered_audio.min()}, Макс. значение: {filtered_audio.max()}")
    return filtered_audio


class EqualizerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.audio_data = None
        self.fs = None

    def initUI(self):
        layout = QVBoxLayout()
        self.sliders = []

        for i in range(5):
            label = QLabel(f'Полоса {bands[i][0]}-{bands[i][1]} Hz')
            slider = QSlider(Qt.Orientation.Vertical)
            slider.setMinimum(-12)
            slider.setMaximum(12)
            slider.setValue(0)
            slider.valueChanged.connect(self.update_gain(i))
            layout.addWidget(label)
            layout.addWidget(slider)
            self.sliders.append(slider)

        # Ползунок для ВЧ-фильтра
        label = QLabel(f'Полоса >{highpass_cutoff} Hz')
        slider = QSlider(Qt.Orientation.Vertical)
        slider.setMinimum(-12)
        slider.setMaximum(12)
        slider.setValue(0)
        slider.valueChanged.connect(self.update_gain(5))
        layout.addWidget(label)
        layout.addWidget(slider)
        self.sliders.append(slider)

        self.load_button = QPushButton('Загрузить WAV')
        self.load_button.clicked.connect(self.load_audio)
        layout.addWidget(self.load_button)

        self.play_button = QPushButton('Воспроизвести')
        self.play_button.clicked.connect(self.play_audio)
        layout.addWidget(self.play_button)

        self.setLayout(layout)
        self.setWindowTitle('6-полосный эквалайзер')
        self.show()

    def update_gain(self, index):
        def update(value):
            gain_values[index] = value
            print(f"Изменение усиления: {gain_values}")  # Отладка значений усиления

        return update

    def load_audio(self):
        file_path, _ = QFileDialog.getOpenFileName(self, 'Выберите WAV-файл', '', 'WAV Files (*.wav)')
        if file_path:
            print(f"Загружен файл: {file_path}")
            with wave.open(file_path, 'rb') as wf:
                self.fs = wf.getframerate()
                audio_data = np.frombuffer(wf.readframes(wf.getnframes()), dtype=np.int16)
                self.audio_data = audio_data.astype(np.float32) / 32768.0
            print(f"Частота дискретизации: {self.fs}, Длина аудиоданных: {len(self.audio_data)}")

    def play_audio(self):
        if self.audio_data is not None:
            processed_audio = apply_equalizer(self.audio_data, self.fs)
            sd.play(processed_audio, self.fs)
            sd.wait()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = EqualizerApp()
    sys.exit(app.exec())
