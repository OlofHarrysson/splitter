import anyfig
from pathlib import Path

import signal_detectors
import analyze_metadata
import edit_xml
from utils import google_utils
from utils import xml_utils
from utils import meta_utils


def main():
  config = anyfig.setup_config(default_config='DebugConfig')
  if config.clear_outdir:
    meta_utils.clear_outdir()

  print(config)
  recognizer = config.recognizer

  analyzed_metadatum = []
  for asset in get_asset_files(config.xml_file):
    # Upload data to cloud
    data, cloud_file_name = recognizer.prepare_data(
      asset['src'], config.google_bucket_name, config.unique_cloud_file_id)

    # Speech -> text -> actions
    actions = recognizer.find_actions(data, config.fake_data)

    if config.delete_cloud_file:
      print(f"Deleting file {cloud_file_name} from Google storage...")
      google_utils.delete_blob(config.google_bucket_name, cloud_file_name)
    analyzed_metadatum.append(dict(id=asset['id'], actions=actions))

  edit_xml.main(config.xml_file, analyzed_metadatum, config.send_to_finalcut)


def get_asset_files(path):
  tree, root = xml_utils.read_xml(path)
  asset_xmls = root.findall('resources/asset')
  return [a.attrib for a in asset_xmls]


if __name__ == '__main__':
  main()