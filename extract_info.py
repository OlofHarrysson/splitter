import anyfig
from pathlib import Path

import signal_detectors
import analyze_metadata
from edit_xml import main as edit_main
from utils import google_utils
from utils import xml_utils


def main():
  config = anyfig.setup_config(default_config='DebugConfig')
  print(config)
  recognizer = config.recognizer

  assets = get_asset_files(config.xml_file)
  # print(assets)
  # qwe

  analyzed_metadatum = []
  for asset in assets:
    data = recognizer.prepare_data(asset['src'])
    actions = recognizer.find_actions(data, config.fake_data)
    analyzed_metadatum.append(dict(id=asset['id'], actions=actions))

  print(analyzed_metadatum)
  qwe
  edit_main(config.xml_file, analyzed_metadatum, config.send_to_finalcut)


def get_asset_files(path):
  tree, root = xml_utils.read_xml(path)
  asset_xmls = root.findall('resources/asset')
  return [a.attrib for a in asset_xmls]


if __name__ == '__main__':
  main()