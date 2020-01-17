import subprocess
from pathlib import Path
import anyfig
import sys

import signal_detectors
from utils import meta_utils
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

    self.bash = False
    self.clear_outdir = True


@anyfig.config_class
class DebugConfig(Config):
  def __init__(self):
    super().__init__()
    # self.send_to_finalcut = False
    self.send_to_finalcut = True
    self.fake_data = True
    self.bash = False
    self.clear_outdir = True


def main():
  config = anyfig.setup_config(default_config='DebugConfig')
  asset_paths = xml_utils.get_asset_paths(config.xml_file)

  docker_asset_paths = set([f'{p.parent}:{p.parent}' for p in asset_paths])
  docker_asset_paths = [f'-v {a}' for a in docker_asset_paths]
  docker_asset_paths = ' '.join(docker_asset_paths)

  if config.bash:
    command = '/bin/bash'
  else:
    command = 'python extract_info.py ' + ' '.join(sys.argv[1:])

  project_root = meta_utils.get_project_root()
  output_volume = f"{project_root/'output'}:/sticker/output"
  args = f"docker run -it --rm --name stick -v {project_root}:/sticker -v {output_volume} {docker_asset_paths} sticker {command}"

  args = args.split()
  args = [a.replace('%20', ' ') for a in args]  # Spaces can be weird in Mac
  print(args)

  completed = subprocess.run(args, capture_output=False)

  if completed.returncode == 0 and config.send_to_finalcut:
    xml_outpath = Path('output') / config.xml_file.name
    meta_utils.send_xml_to_finalcut(xml_outpath)


if __name__ == '__main__':
  main()
