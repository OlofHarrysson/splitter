import anyfig
import json
import signal_detectors
from pathlib import Path
from lxml import etree
import os

from edit_xml import main as edit_main


@anyfig.config_class
class Config():
  def __init__(self):
    # self.data_file = 'music/walk.wav'
    # self.data_file = 'walk.aac'
    # self.data_file = 'gs://splitter-speechtotext/park.wav'
    # self.data_file = 'gs://splitter-speechtotext/walk.wav'
    self.xml_file = Path('finalcut_xml/tochange.fcpxml')

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = str(
      Path(__file__).parent.absolute() / 'speech_key.json')
    self.recognizer = signal_detectors.GoogleSpeechRecognition()


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)
  recognizer = config.recognizer

  root, tree, assets = get_src_files(config.xml_file)

  for asset in assets:
    data = recognizer.prepare_data(asset['src'])
    actions = recognizer.find_actions(data)

  action_data = save_split_info(actions, config.xml_file)
  edit_main(root, tree, action_data)
  qwe


def get_src_files(path):
  tree = etree.parse(str(path))
  root = tree.getroot()
  asset_xmls = root.findall('resources/asset')

  return root, tree, [a.attrib for a in asset_xmls]


def save_split_info(split_info, filename):
  data = dict(filename=str(filename), xml_info=split_info)
  # with open('scene_splits.json', 'w') as outfile:
  #   json.dump(data, outfile, indent=2)
  return data


if __name__ == '__main__':
  main()