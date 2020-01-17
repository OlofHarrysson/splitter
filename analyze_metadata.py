import subprocess
from pathlib import Path
import anyfig

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


@anyfig.config_class
class DebugConfig(Config):
  def __init__(self):
    super().__init__()
    self.send_to_finalcut = False
    self.fake_data = True
    # self.bash = True
    self.bash = False


def main():
  config = anyfig.setup_config(default_config='DebugConfig')
  asset_paths = xml_utils.get_asset_paths(config.xml_file)

  docker_asset_paths = set([f'{p.parent}:{p.parent}' for p in asset_paths])
  docker_asset_paths = [f'-v {a}' for a in docker_asset_paths]
  docker_asset_paths = ' '.join(docker_asset_paths)
  # print(docker_asset_paths)
  # qweee

  if config.bash:
    command = '/bin/bash'
  else:
    command = 'python extract_info.py'

  project_root = meta_utils.get_project_root()
  args = f"docker run -it --rm --name stick -v {project_root}:/sticker {docker_asset_paths} sticker {command}"

  args = args.split()
  args = [a.replace('%20', ' ') for a in args]  # Format final cut asset paths
  print(args)
  # qwe

  completed = subprocess.run(args, capture_output=False)
  print('returncode:', completed.returncode)


if __name__ == '__main__':
  main()

# docker run -it --rm --name stick -v /Users/olof/git/splitter:/sticker -v /Users/olof/Movies/split.fcpbundle/sofa_event/Original\ Media:/Users/olof/Movies/split.fcpbundle/sofa_event/Original_Media sticker /bin/bash

# docker run -it \
#   --rm \
#   --name stick \
#   -v "$PWD":/sticker \
#   sticker \
#   /bin/bash

# # docker run -it --entrypoint='bash' jrottenberg/ffmpeg:4.1
# docker run -it --entrypoint='bash' --rm --name stick sticker