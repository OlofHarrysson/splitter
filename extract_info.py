import anyfig
import json
import signal_detectors


@anyfig.config_class
class Config():
  def __init__(self):
    # self.data_file = 'music/walk.wav'
    # self.data_file = 'walk.aac'
    # self.data_file = 'gs://splitter-speechtotext/park.wav'
    self.data_file = 'gs://splitter-speechtotext/walk.wav'
    self.recognizer = signal_detectors.GoogleSpeechRecognition()


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)

  recognizer = config.recognizer

  data = recognizer.prepare_data(config.data_file)
  actions = recognizer.find_actions(data)
  save_split_info(actions, config.data_file)


def save_split_info(split_info, filename):
  data = dict(filename=str(filename), xml_info=split_info)
  with open('scene_splits.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)


if __name__ == '__main__':
  main()