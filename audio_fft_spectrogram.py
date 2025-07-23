import os
import subprocess
import numpy as np
import soundfile as sf
import plotly.graph_objects as go
from scipy.fft import fft, fftfreq, spectrogram
import librosa

# ============ Configurable Options ============
AUDIO_FILE = "your_audio.mp3"
FFT_START = 0     # in seconds
FFT_END = 5       # in seconds
EXPORT_HTML = True
SHOW_PITCH_LABELS = True
SLIDING_WINDOW_SECONDS = 5
# ==============================================

def convert_to_wav(input_file, output_file='temp.wav'):
    subprocess.run(['ffmpeg', '-y', '-i', input_file, output_file],
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_file

def frequency_to_note(freq):
    if freq <= 0:
        return ""
    return librosa.hz_to_note(freq)

def plot_fft(data, samplerate, start_time, end_time):
    start_sample = int(start_time * samplerate)
    end_sample = int(end_time * samplerate)
    slice_data = data[start_sample:end_sample]

    N = len(slice_data)
    T = 1.0 / samplerate
    yf = fft(slice_data)
    xf = fftfreq(N, T)[:N//2]
    amplitude = 2.0/N * np.abs(yf[:N//2])

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xf, y=amplitude, mode='lines'))
    fig.update_layout(
        title=f"Fourier Transform ({start_time}s–{end_time}s)",
        xaxis_title='Frequency (Hz)',
        yaxis_title='Amplitude',
        template='plotly_dark',
        height=500,
        width=1000
    )
    fig.show()

def generate_spectrogram_frames(data, samplerate, window_seconds=5, hop_seconds=1):
    total_duration = len(data) / samplerate
    frames = []
    for start in np.arange(0, total_duration - window_seconds, hop_seconds):
        start_sample = int(start * samplerate)
        end_sample = int((start + window_seconds) * samplerate)
        segment = data[start_sample:end_sample]

        f, t, Sxx = spectrogram(segment, samplerate, nperseg=1024)
        Sxx_db = 10 * np.log10(Sxx + 1e-10)
        frames.append((t + start, f, Sxx_db))
    return frames

def plot_spectrogram_animation(frames, show_pitch_labels, export_html):
    fig = go.Figure()

    for i, (t, f, Sxx_db) in enumerate(frames):
        fig.add_trace(go.Heatmap(
            z=Sxx_db,
            x=t,
            y=f,
            visible=(i == 0),
            colorscale="Viridis",
            colorbar=dict(title="dB") if i == 0 else None
        ))

    steps = []
    for i in range(len(frames)):
        steps.append(dict(
            method="update",
            args=[{"visible": [j == i for j in range(len(frames))]}],
            label=f"{i:.1f}s"
        ))

    fig.update_layout(
        title="Sliding Spectrogram Animation",
        xaxis_title="Time (s)",
        yaxis_title="Frequency (Hz)",
        yaxis_type="log",
        sliders=[dict(active=0, steps=steps, currentvalue={"prefix": "Slice: "})],
        updatemenus=[dict(type="buttons", showactive=False,
                          buttons=[dict(label="Play",
                                        method="animate",
                                        args=[None, {"frame": {"duration": 500, "redraw": True},
                                                     "fromcurrent": True}]),
                                   dict(label="Pause",
                                        method="animate",
                                        args=[[None], {"frame": {"duration": 0, "redraw": False},
                                                       "mode": "immediate"}])])],
        template="plotly_dark",
        height=600,
        width=1000
    )

    if show_pitch_labels:
        y_freqs = frames[0][1]
        pitch_labels = [frequency_to_note(f) for f in y_freqs]
        fig.update_yaxes(tickvals=y_freqs[::16], ticktext=pitch_labels[::16])

    if export_html:
        fig.write_html("spectrogram_animation.html")
        print("✅ Spectrogram saved as spectrogram_animation.html")
    else:
        fig.show()

def main(audio_path):
    is_temp = False
    if not audio_path.lower().endswith(".wav"):
        audio_path = convert_to_wav(audio_path)
        is_temp = True

    data, samplerate = sf.read(audio_path)
    if data.ndim > 1:
        data = data[:, 0]

    print("📊 Plotting FFT...")
    plot_fft(data, samplerate, FFT_START, FFT_END)

    print("🎞️ Generating spectrogram frames...")
    frames = generate_spectrogram_frames(data, samplerate, SLIDING_WINDOW_SECONDS)
    print("📈 Plotting animated spectrogram...")
    plot_spectrogram_animation(frames, SHOW_PITCH_LABELS, EXPORT_HTML)

    if is_temp:
        os.remove(audio_path)

if __name__ == "__main__":
    main(AUDIO_FILE)