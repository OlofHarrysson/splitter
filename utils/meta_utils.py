from pathlib import Path
import subprocess


def get_project_root():
  return Path(__file__).parent.parent.absolute()


def send_xml_to_finalcut(xml_path):
  xml_path = xml_path.absolute()
  assert xml_path.exists(), f"XML file '{xml_path} didn't exist'"
  args = ['osascript', 'finalcut_integration/send_data.scpt', xml_path]
  completed = subprocess.run(args, capture_output=True)
  print('returncode:', completed.returncode)


def clear_outdir():
  outdir = get_project_root() / 'output'
  for p in outdir.iterdir():
    p = p.absolute()
    p.unlink()
