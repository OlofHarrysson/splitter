import numpy as np
import matplotlib
import matplotlib.pyplot as plt

import librosa

import plotly.express as px


def pause():
  input("PRESS KEY TO CONTINUE.")


def plot(y, sr):
  plt1 = plt.figure(figsize=(16, 4))
  f = librosa.display.waveplot(y, sr=sr)
  plt.title('Slower Version $X_1$')
  plt.show()
  # pause()


def mfcc():
  # filename = 'music/three.wav'
  filename = 'music/talkbeep.wav'
  # filename = 'music/distractor.wav'
  hop_length = 512
  y, sr = librosa.load(filename)
  y = librosa.util.normalize(y)
  mfcc = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
  y_orig, sr_orig = y, sr
  # plot(y, sr)

  # print(y.shape[0] / sr)  # Time in seconds

  filename = 'music/500hz.wav'
  y, sr = librosa.load(filename)
  y = librosa.util.normalize(y)
  mfcc2 = librosa.feature.mfcc(y=y, sr=sr, hop_length=hop_length, n_mfcc=13)
  # plot(y, sr)

  # print(mfcc.shape)
  # print(mfcc2.shape)
  a = librosa.segment.cross_similarity(mfcc2, mfcc)
  print(a.shape)
  preds = a.astype(np.float32).mean(axis=1)
  print(preds.shape)
  time_preds = []
  time = 0
  for pred in preds:
    if pred > 0.5:
      time_preds.append(time)
    time += hop_length / sr

  print(time_preds)

  plot_result(y_orig, sr_orig, time_preds)


def plot_result(y, sr, xs):
  plt.figure(figsize=(16, 4))
  plt.subplot(2, 1, 1)
  f = librosa.display.waveplot(y, sr=sr)
  xmin, xmax = f.axes.get_xlim()

  ax2 = plt.subplot(2, 1, 2)
  ys = [1 for x in xs]
  ax2.scatter(xs, ys)
  ax2.set_xlim([xmin, xmax])

  plt.title('Slower Version $X_1$')
  plt.show()
  # pause()


def chroma():
  hop_length = 2205
  n_fft = 4410
  filename = 'music/two.wav'
  x_1, sr = librosa.load(filename)
  x_1_chroma = librosa.feature.chroma_stft(y=x_1,
                                           sr=sr,
                                           tuning=0,
                                           norm=2,
                                           hop_length=hop_length,
                                           n_fft=n_fft)

  filename = 'music/click.wav'
  x_2, sr = librosa.load(filename)

  x_2_chroma = librosa.feature.chroma_stft(y=x_2,
                                           sr=sr,
                                           tuning=0,
                                           norm=2,
                                           hop_length=hop_length,
                                           n_fft=n_fft)

  D, wp = librosa.sequence.dtw(X=x_1_chroma, Y=x_2_chroma, metric='cosine')
  wp_s = np.asarray(wp) * hop_length / sr

  fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 8))

  # Plot x_1
  librosa.display.waveplot(x_1, sr=sr, ax=ax1)
  ax1.set(title='Slower Version $X_1$')

  # Plot x_2
  librosa.display.waveplot(x_2, sr=sr, ax=ax2)
  ax2.set(title='Slower Version $X_2$')

  plt.tight_layout()
  # plt.show()

  trans_figure = fig.transFigure.inverted()
  lines = []
  arrows = 30
  points_idx = np.int16(np.round(np.linspace(0, wp.shape[0] - 1, arrows)))

  # for tp1, tp2 in zip((wp[points_idx, 0]) * hop_length, (wp[points_idx, 1]) * hop_length):
  for tp1, tp2 in wp[points_idx] * hop_length / sr:
    # get position on axis for a given index-pair
    coord1 = trans_figure.transform(ax1.transData.transform([tp1, 0]))
    coord2 = trans_figure.transform(ax2.transData.transform([tp2, 0]))

    # draw a line
    line = matplotlib.lines.Line2D((coord1[0], coord2[0]),
                                   (coord1[1], coord2[1]),
                                   transform=fig.transFigure,
                                   color='r')
    lines.append(line)

  fig.lines = lines
  plt.tight_layout()
  plt.show()


if __name__ == '__main__':
  mfcc()
  # chroma()
