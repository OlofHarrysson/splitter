import speech_recognition as sr

import io
import os

# Imports the Google Cloud client library
# from google.cloud import speech
# from google.cloud import speech_v1 as speech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v1p1beta1 import enums
from google.cloud.speech_v1p1beta1 import types

r = sr.Recognizer()

audio_source = sr.Microphone()
# audio_source = sr.AudioFile('music/park.wav')

print("Listening[")
with audio_source as source:
  r.adjust_for_ambient_noise(source)
  audio = r.listen(source)

text = r.recognize_google(audio, show_all=True)
# text = r.recognize_sphinx(audio, show_all=True)
print(text)

# def sample_long_running_recognize():
#   client = speech.SpeechClient()

#   wake_words = ['video helper', 'videohelper']
#   clip_words = ['start clip', 'end clip']
#   marker_words = ['add mark', 'add marks']
#   phrases = wake_words + clip_words + marker_words

#   # When enabled, the first result returned by the API will include a list
#   # of words and the start and end time offsets (timestamps) for those words.
#   config = types.RecognitionConfig(
#     encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
#     language_code='en-US',
#     # audio_channel_count=2,
#     enable_word_time_offsets=True,
#     model='video',
#     speech_contexts=[dict(phrases=phrases, boost=20)])

#   # Loads the audio into memory
#   # file_name = 'music/park.wav'
#   file_name = 'music/park_short.wav'
#   storage_uri = 'gs://splitter-speechtotext/park.wav'
#   with io.open(file_name, 'rb') as audio_file:
#     content = audio_file.read()
#     audio = types.RecognitionAudio(content=content)

#   audio = {"uri": storage_uri}
#   operation = client.long_running_recognize(config, audio)

#   print(u"Waiting for operation to complete...")
#   response = operation.result()

#   # The first result includes start and end time word offsets
#   # result = response.results[0]
#   # # First alternative is the most probable result
#   # alternative = result.alternatives[0]
#   # # Print the start and end time of each word
#   # for word in alternative.words:
#   #   print(u"Word: {}".format(word.word))
#   #   print(u"Start time: {} seconds {} nanos".format(word.start_time.seconds,
#   #                                                   word.start_time.nanos))
#   #   print(u"End time: {} seconds {} nanos".format(word.end_time.seconds,
#   #                                                 word.end_time.nanos))
#   # print(u"Transcript: {}".format(alternative.transcript))

#   for result in response.results:
#     # First alternative is the most probable result
#     alternative = result.alternatives[0]
#     print(u"Transcript: {}".format(alternative.transcript))

# sample_long_running_recognize()