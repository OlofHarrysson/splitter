from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol
import cv2
import shapely
from shapely.geometry import MultiPoint
import numpy as np
from collections import namedtuple, defaultdict
import itertools

import io
import os
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types

from fake_data import get_fake_words


class QR_Detector():
  def draw_bounding_box(self, im, qr_detection):
    if qr_detection['text']:
      red_color = (0, 0, 255)
      points = qr_detection['points'].astype(np.int32)

      im = cv2.polylines(im, [points],
                         isClosed=True,
                         color=red_color,
                         thickness=4)

      x, y = points[3][0][0], points[3][0][1]  # Point for top left
      cv2.putText(im, qr_detection['text'], (x, y - 10),
                  cv2.FONT_HERSHEY_SIMPLEX, 1.5, red_color, 2)
    return im


class OpenCVDetector(QR_Detector):
  def __init__(self):
    self.qrDecoder = cv2.QRCodeDetector()

  def find_qr(self, image):
    data, points, rectifiedImage = self.qrDecoder.detectAndDecode(image)
    return dict(text=data, points=points)


class ZbarQRDetector(QR_Detector):
  def find_qr(self, image):
    detection = decode(image, symbols=[ZBarSymbol.QRCODE])
    if not detection:
      return dict(text=None, points=None)

    text = detection[0].data.decode("utf-8")
    points = detection[0].polygon
    points = np.array([[p.x, p.y] for p in points])
    return dict(text=text, points=np.expand_dims(points, 1))


class GoogleSpeechRecognition():
  def __init__(self):
    self.client = speech.SpeechClient()

    command_format = namedtuple('Command', 'command command_variant')
    self.commands = []
    self.commands.append(command_format(Commands.wakeword, 'videohelper'))
    self.commands.append(command_format(Commands.wakeword, 'video helper'))
    self.commands.append(command_format(Commands.startclip, 'start clip'))
    self.commands.append(command_format(Commands.endclip, 'end clip'))
    self.commands.append(command_format(Commands.endclip, 'stop clip'))
    self.commands.append(command_format(Commands.placemarker, 'add markers'))
    self.commands.append(command_format(Commands.placemarker, 'add marker'))

    self.word_format = namedtuple('Word', 'text start_time end_time')

  def find_actions(self, audio):
    # words = self.transcribe_audio(audio)
    words = get_fake_words()

    # text = [w.text for w in words]
    # print(text)

    words = self.format_transcription(words)
    # text = [w.text for w in words]
    # print(text)

    index2word = {i: w for i, w in enumerate(words)}
    command2index = defaultdict(list)
    for ind, word in index2word.items():
      if isinstance(word.text, Commands):
        command2index[word.text].append(ind)

    actions = defaultdict(list)
    for wake_word_ind in command2index[Commands.wakeword]:
      wake_word = index2word[wake_word_ind]
      command_word = index2word[wake_word_ind + 1]

      if command_word.text == Commands.placemarker:
        marker_word = index2word[wake_word_ind + 2]
        action = dict(time=marker_word.start_time, name=marker_word.text)
        actions[command_word.text].append(action)

      if command_word.text == Commands.startclip:
        action = dict(time=command_word.start_time)
        actions[command_word.text].append(action)

      if command_word.text == Commands.endclip:
        action = dict(time=command_word.end_time)
        actions[command_word.text].append(action)

    # TODO: Try to match uneven lengths of start/end
    formated_actions = defaultdict(list)
    for start_clip, end_clip in zip(actions[Commands.startclip],
                                    actions[Commands.endclip]):
      action = dict(start_time=start_clip['time'],
                    end_time=end_clip['time'],
                    duration=end_clip['time'] - start_clip['time'])
      formated_actions['clips'].append(action)

    formated_actions['markers'] = actions[Commands.placemarker]
    return formated_actions

  def format_transcription(self, words):
    ''' Changes the occurances of video helper to videohelper '''

    # TODO: Move away from string. Placeholder doesn't work video one word commands (nor three I guess)
    placeholder = '!placeholder!'
    text = ' '.join([w.text for w in words])
    for command, command_alternative in self.commands:
      text = text.replace(command_alternative, f'{command} {placeholder}')
    text = text.split()

    formated_words = []
    for w, t in zip(words, text):
      if t != placeholder:
        if t.startswith('Commands.'):
          t = eval(t)

        formated_words.append(self.word_format(t, w.start_time, w.end_time))

    return formated_words

  def transcribe_audio(self, audio):
    phrases = [c.command_variant for c in self.commands]
    config = types.RecognitionConfig(
      encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
      language_code='en-US',
      audio_channel_count=2,
      enable_word_time_offsets=True,
      model='video',
      speech_contexts=[dict(phrases=phrases, boost=20)])

    operation = self.client.long_running_recognize(config, audio)

    print(u"Waiting for operation to complete...")
    response = operation.result()

    words = []
    for result in response.results:
      for word in result.alternatives[0].words:
        start_time = word.start_time.seconds + word.start_time.nanos / 1e9
        end_time = word.end_time.seconds + word.end_time.nanos / 1e9
        words.append(self.word_format(word.word, start_time, end_time))
        # TODO: Add confidence?

    return words

  def prepare_data(self, path):
    if str(path).startswith('gs://'):
      audio = {"uri": path}
      return audio

    with io.open(path, 'rb') as audio_file:
      content = audio_file.read()
      audio = types.RecognitionAudio(content=content)
    return audio


import enum


@enum.unique
class Commands(enum.Enum):
  wakeword = enum.auto()  # TODO I want wakeword with value videohelper?
  startclip = enum.auto()
  endclip = enum.auto()
  placemarker = enum.auto()