from scipy.signal import butter, lfilter
import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import freqz


def butter_bandpass(lowcut, highcut, fs, order=5):
  nyq = 0.5 * fs
  low = lowcut / nyq
  high = highcut / nyq
  b, a = butter(order, [low, high], btype='band')
  return b, a


def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
  b, a = butter_bandpass(lowcut, highcut, fs, order=order)
  y = lfilter(b, a, data)
  return y


def measure_hz(x, sr):
  # https://stackoverflow.com/questions/3694918/how-to-extract-frequency-associated-with-fft-values-in-python
  # For some reason it says 3000 Hz for my 500hz file
  w = np.fft.fft(x)
  freqs = np.fft.fftfreq(len(w))
  idx = np.argmax(np.abs(w))
  freq = freqs[idx]
  freq_in_hertz = abs(freq * sr)
  print(freq_in_hertz)


def plot_mfcc(data):
  plt.figure(figsize=(12, 8))
  librosa.display.specshow(mfcc, y_axis='log', x_axis='time')
  # librosa.display.specshow(mfcc, y_axis='linear', x_axis='time')
  plt.colorbar(format='%+2.0f dB')
  plt.title('Log-frequency power spectrogram')
  plt.show()


def pause():
  input("PRESS KEY TO CONTINUE.")


if __name__ == "__main__":
  # filename = 'music/talkbeep.wav'
  # filename = 'music/500hz.wav'
  # filename = 'music/3sec_beeps.wav'
  # filename = 'music/3sec_beeps_louder_music.wav'
  # filename = 'music/3sec_prat.wav'
  # filename = 'music/3sec_load_talks.wav'
  # filename = 'music/3sec_talk_loudbeep.wav'
  # filename = 'music/1to16.wav'
  # filename = 'music/microbit_freq/100.wav'  # 4199 Hz
  # filename = 'music/microbit_freq/500.wav'  # 3000 Hz
  # filename = 'music/microbit_freq/800.wav'  # 4006
  # filename = 'music/audacity/697.wav'
  filename = 'music/audacity/talk.wav'

  y, sr = librosa.load(filename, sr=44100)  # sr is 44100 in source
  x = y
  # x = librosa.util.normalize(x)

  # mfcc = librosa.feature.melspectrogram(y=y, sr=sr)
  # mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
  # mfcc = librosa.feature.chroma_stft(y=y, sr=sr)
  # print(mfcc.shape)
  # plot_mfcc(mfcc)
  # qwe

  # measure_hz(x, sr)
  # qwe
  # print(len(x))
  # print(sr)
  # print(len(x) / sr) # Duration

  # Sample rate and desired cutoff frequencies (in Hz).
  # fs = 5000.0
  # lowcut = 400.0
  # highcut = 1250.0
  fs = sr
  # lowcut = 3980
  # highcut = 4020

  lowcuts = [670]
  highcuts = [730]
  freqs = [697]

  # Plot the frequency response for a few different orders.
  # plt.figure(1)
  # plt.clf()
  # orders = [1, 2, 3, 4, 5, 6]
  # for order in orders:
  #   b, a = butter_bandpass(lowcuts[0], highcuts[0], fs, order=order)
  #   w, h = freqz(b, a, worN=2000)
  #   plt.plot((fs * 0.5 / np.pi) * w, abs(h), label="order = %d" % order)

  # plt.plot([0, 0.5 * fs], [np.sqrt(0.5), np.sqrt(0.5)],
  #          '--',
  #          label='sqrt(0.5)')
  # plt.xlabel('Frequency (Hz)')
  # plt.ylabel('Gain')
  # plt.grid(True)
  # plt.legend(loc='best')

  # Filter a noisy signal.
  # T = 0.05
  T = len(x) / fs
  nsamples = T * fs
  t = np.linspace(0, T, nsamples, endpoint=False)
  a = 0.02
  # f0 = 600.0
  f0 = 'Microbit'
  # x = 0.1 * np.sin(2 * np.pi * 1.2 * np.sqrt(t))
  # x += 0.01 * np.cos(2 * np.pi * 312 * t + 0.1)
  # x += a * np.cos(2 * np.pi * f0 * t + .11)
  # x += 0.03 * np.cos(2 * np.pi * 2000 * t)

  time_diff = len(x) - len(t)
  if time_diff != 0 and abs(time_diff) < 3:
    # Some rounding error
    if time_diff > 0:
      # x is longer
      x = x[:-1]
    else:
      # t is longer
      t = t[:-1]

  for lowcut, highcut, freq in zip(lowcuts, highcuts, freqs):
    print("WOOWOW")
    plt.figure(2)
    plt.clf()
    plt.plot(t, x, label='Noisy signal')

    y = butter_bandpass_filter(x, lowcut, highcut, fs, order=4)
    plt.plot(t, y, label='Filtered signal (%g Hz)' % freq)
    plt.xlabel('time (seconds)')
    plt.hlines([-a, a], 0, T, linestyles='--')
    plt.grid(True)
    plt.axis('tight')
    plt.legend(loc='upper left')

  plt.show()