import anyfig

import signal_detectors


@anyfig.config_class
class Config():
  def __init__(self):
    self.data_file = 'music/park_short.wav'
    # self.data_file = 'gs://splitter-speechtotext/park.wav'
    self.recognizer = signal_detectors.GoogleSpeechRecognition()


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)

  recognizer = config.recognizer

  data = recognizer.prepare_data(config.data_file)
  actions = recognizer.find_actions(data)
  # split_info = split_video(action_frames, input_file, config.fps)
  # save_split_info(split_info, input_file)


def save_split_info(split_info, filename):
  data = dict(filename=str(filename), scenes=split_info)
  with open('scene_splits.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)


if __name__ == '__main__':
  main()