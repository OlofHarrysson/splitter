from pathlib import Path


def get_project_root():
  return Path(__file__).parent.parent.absolute()


def send_xml_to_finalcut(xml_path):
  args = ['osascript', 'finalcut_integration/send_data.scpt', xml_path]
  completed = subprocess.run(args, capture_output=True)
  print('returncode:', completed.returncode)


def clear_outdir():
  outdir = get_project_root() / 'output'
  print(outdir)
  qwe
  # for p in outdir.iterdir():
  #   p.unlink()