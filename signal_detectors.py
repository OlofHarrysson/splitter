from collections import namedtuple, defaultdict
from pathlib import Path
import subprocess
import ffmpeg

from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums, types

from fake_data import get_fake_words
from utils import google_utils
from dataformats import Commands


class GoogleSpeechRecognition():
  def __init__(self, commandword_bias):

    self.client = speech.SpeechClient()

    self.commandword_bias = commandword_bias

    command_format = namedtuple('Command', 'command command_variant')
    self.commands = []
    self.commands.append(command_format(Commands.wakeword, 'videohelper'))
    self.commands.append(command_format(Commands.wakeword, 'video helper'))
    self.commands.append(command_format(Commands.startclip, 'start clip'))
    self.commands.append(command_format(Commands.endclip, 'end clip'))
    self.commands.append(command_format(Commands.endclip, 'stop clip'))
    self.commands.append(command_format(Commands.placemarker, 'add markers'))
    self.commands.append(command_format(Commands.placemarker, 'add marker'))

  def find_actions(self, audio, fake_data):
    if fake_data:
      transcriber = Transcriber([])
      transcriber.words = get_fake_words()
    else:
      raw_words = self.transcribe_audio(audio)
      transcriber = Transcriber(raw_words)

    transcriber.print_text()
    words = transcriber.format_transcription(self.commands)

    index2word = {i: w for i, w in enumerate(words)}
    command2index = defaultdict(list)
    for ind, word in index2word.items():
      if isinstance(word.text, Commands):
        command2index[word.text].append(ind)

    to_timestring = lambda x: f'{int(x*1000)}/1000'  # TODO: Problem?

    actions = defaultdict(list)
    for wake_word_ind in command2index[Commands.wakeword]:
      wake_word = index2word[wake_word_ind]
      command_word = index2word[wake_word_ind + 1]

      if command_word.text == Commands.placemarker:
        marker_word = index2word[wake_word_ind + 2]
        action = dict(time=to_timestring(marker_word.start_time),
                      name=marker_word.text)
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
      action = dict(start_time=to_timestring(start_clip['time']),
                    end_time=to_timestring(end_clip['time']),
                    duration=to_timestring(end_clip['time'] -
                                           start_clip['time']))
      formated_actions['clips'].append(action)

    formated_actions['markers'] = actions[Commands.placemarker]
    return dict(formated_actions)

  def transcribe_audio(self, audio):
    phrases = [c.command_variant for c in self.commands]
    config = types.RecognitionConfig(
      encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
      language_code='en-US',
      audio_channel_count=2,
      enable_word_time_offsets=True,
      model='video',
      speech_contexts=[dict(phrases=phrases, boost=self.commandword_bias)])

    operation = self.client.long_running_recognize(config, audio)

    print(u"Analyzing speech...")
    response = operation.result()

    words = []
    for result in response.results:
      for word in result.alternatives[0].words:
        words.append(word)
    return words

  def prepare_data(self, path):
    path = path.replace('file://', '').replace('%20', ' ')
    path = Path(path)
    assert path.exists(), f"File '{path}' doesn't exist"
    assert path.is_file(), f"Path '{path}' wasn't a file"

    tmp_audio_file = f'/tmp/{path.stem}.wav'
    cloud_path = Path(tmp_audio_file)
    ffmpeg.input(path).output(tmp_audio_file).overwrite_output().run(
      quiet=True)

    if not google_utils.blob_exists('splitter-speechtotext', cloud_path.name):
      print(f"Uploading file to {cloud_path.name}...")

      google_utils.upload_blob('splitter-speechtotext', tmp_audio_file,
                               cloud_path.name)

    uri_path = 'gs://splitter-speechtotext/' + cloud_path.name
    audio = {"uri": uri_path}
    return audio


class Transcriber():
  def __init__(self, raw_words):
    self.word_format = namedtuple('Word', 'text start_time end_time')

    self.words = []
    for word in raw_words:
      start_time = word.start_time.seconds + word.start_time.nanos / 1e9
      end_time = word.end_time.seconds + word.end_time.nanos / 1e9
      self.words.append(self.word_format(word.word, start_time, end_time))
      # TODO: Add confidence?

  def format_transcription(self, commands):
    placeholder = '!placeholder!'
    text = ' '.join([w.text for w in self.words])
    for command, command_alternative in commands:
      n_words_command = len(command_alternative.split())
      placeh = " ".join([placeholder for _ in range(n_words_command - 1)])
      text = text.replace(command_alternative, f'{command} {placeh}')
    text = text.split()

    assert len(self.words) == len(text)

    formated_words = []
    for w, t in zip(self.words, text):
      if t != placeholder:
        if t.startswith('Commands.'):
          t = eval(t)

        formated_words.append(self.word_format(t, w.start_time, w.end_time))

    return formated_words

  def print_text(self):
    text = [w.text for w in self.words]
    print(' '.join(text))