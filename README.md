# Audio FFT & Spectrogram Visualizer

This tool performs the following operations on an audio file:

- ✅ Converts any audio format (MP3, FLAC, M4A, etc.) to WAV using FFmpeg
- 📈 Generates a Fourier Transform (FFT) of a time slice (interactive plot)
- 🎞️ Generates an animated spectrogram using sliding time windows
- 🎼 Displays optional pitch labels on the y-axis
- 💾 Exports the spectrogram animation to an HTML file

---

## 📦 Requirements

Install dependencies:

```bash
pip install numpy scipy soundfile plotly librosa
```

Make sure `ffmpeg` is installed and available in your system's PATH:

```bash
ffmpeg -version
```

---

## 🚀 Usage

Edit the top of the script to configure:

```python
AUDIO_FILE = "your_audio.mp3"
FFT_START = 0     # in seconds
FFT_END = 5       # in seconds
EXPORT_HTML = True
SHOW_PITCH_LABELS = True
SLIDING_WINDOW_SECONDS = 5
```

Then run:

```bash
python audio_fft_spectrogram.py
```

---

## 📂 Output

- FFT plot opens in your browser
- Spectrogram animation opens or is saved as `spectrogram_animation.html`