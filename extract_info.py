import anyfig
import signal_detectors
from pathlib import Path

from edit_xml import main as edit_main

from utils import google_utils
from utils import xml_utils


@anyfig.config_class
class Config():
  def __init__(self):
    google_utils.register_credentials()
    self.xml_file = Path('finalcut_xml/sofa_event.fcpxml')
    # self.xml_file = Path('finalcut_xml/twowalks.fcpxml')
    # self.xml_file = Path('finalcut_xml/walking.fcpxml')

    self.send_to_finalcut = True
    self.fake_data = False

    self.commandword_bias = 40
    self.recognizer = signal_detectors.GoogleSpeechRecognition(
      self.commandword_bias)


@anyfig.config_class
class DebugConfig(Config):
  def __init__(self):
    super().__init__()
    self.send_to_finalcut = False
    self.fake_data = True


def main():
  config = anyfig.setup_config(default_config='DebugConfig')
  print(config)
  recognizer = config.recognizer

  assets = get_asset_files(config.xml_file)

  analyzed_metadatum = []
  for asset in assets:
    data = recognizer.prepare_data(asset['src'])
    actions = recognizer.find_actions(data, config.fake_data)
    analyzed_metadatum.append(dict(id=asset['id'], actions=actions))

  edit_main(config.xml_file, analyzed_metadatum, config.send_to_finalcut)


def get_asset_files(path):
  tree, root = xml_utils.read_xml(path)
  asset_xmls = root.findall('resources/asset')
  return [a.attrib for a in asset_xmls]


if __name__ == '__main__':
  main()