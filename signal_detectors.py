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

    # wake_words = ['video helper', 'videohelper']
    # clip_words = ['start clip', 'end clip']
    # marker_words = ['add mark']
    # self.phrases = dict(wake_words=wake_words,
    #                     clip_words=clip_words,
    #                     marker_words=marker_words)

    # # phrase -> variants
    command_format = namedtuple('Command', 'command command_variant')
    self.commands = []
    self.commands.append(command_format('videohelper', 'videohelper'))
    self.commands.append(command_format('videohelper', 'video helper'))
    self.commands.append(command_format('startclip', 'start clip'))
    self.commands.append(command_format('endclip', 'end clip'))
    self.commands.append(command_format('markclip', 'mark clip'))

    self.word_format = namedtuple('Word', 'text start_time end_time')

  def find_actions(self, audio):
    # words = self.transcribe_audio(audio)
    words = ['hej', 'video', 'helper', 'start', 'clip', 'videohelper']
    words = [self.word_format(w, 0, 1) for w in words]
    words = self.format_transcription(words)

    index2word = {i: w for i, w in enumerate(words)}
    word2indecies = defaultdict(list)
    {word2indecies[w].append(i)
     for i, w in enumerate(words)}  # TODO check if phrase
    print(words)
    qwe

    # keyword_phrases
    # videohelper start clip, vh add mark, vh end clip
    # actions, startclip, endclip, marker

    def get_next_action(i):
      action = {}
      action_text = words[i + 1].text + words[i + 2].text
      if action_text == 'startclip':  # TODO
        action_type = 'clip'

    actions = defaultdict(list)
    for ind, word in words.items():
      if word.text in self.phrases['wake_words']:
        # print(word)
        action = get_next_action(ind)
        actions[action.type] = action
        print(action)

  def format_transcription(self, words):
    ''' Changes the occurances of video helper to videohelper '''
    placeholder = '!placeholder!'
    text = ' '.join([w.text for w in words])
    for command, command_alternative in self.commands:
      text = text.replace(command_alternative, f'{command} {placeholder}')
    text = text.split()

    formated_words = []
    for w, t in zip(words, text):
      if t != placeholder:
        formated_words.append(self.word_format(t, w.start_time, w.end_time))

    return formated_words

  def transcribe_audio(self, audio):
    phrases = list(itertools.chain.from_iterable(self.phrases.values()))
    config = types.RecognitionConfig(
      encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
      language_code='en-US',
      audio_channel_count=2,
      enable_word_time_offsets=True,
      model='video',
      speech_contexts=[dict(phrases=self.phrases, boost=20)])

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