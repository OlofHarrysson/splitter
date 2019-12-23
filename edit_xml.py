from pathlib import Path
import anyfig
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom


@anyfig.config_class
class Config():
  def __init__(self):
    self.scene_input_file = Path('scene_splits.json')
    self.xml_input_file = Path('finalcut_xml/home_split.fcpxml')
    self.outfile = Path('finalcut_xml/output.fcpxml')

    with open(self.scene_input_file) as infile:
      self.scene_splits = json.load(infile)


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)
  tree = ET.parse(config.xml_input_file)
  root = tree.getroot()
  print(root)
  # for child in root.iter():
  #   print(child.tag, child.attrib)

  clip_name = Path(config.scene_splits['filename']).stem
  print(clip_name)

  for scene_name, scene_info in config.scene_splits['scenes'].items():
    start, duration = scene_info
    print(scene_name, scene_info)

  for clip in root.iter('asset-clip'):
    if clip.attrib['name'] == clip_name:
      keywords = get_clip_info(config.scene_splits['scenes'])
      [clip.append(k) for k in keywords]

  # root = prettify(root)
  tree.write(config.outfile)

  clean_up_xml(config)


def get_clip_info(scenes):
  keywords = []
  for scene_name, scene_info in scenes.items():
    start, duration = scene_info
    print(scene_name, scene_info)
    keyword = ET.Element('keyword')
    keyword.set('start', f'{start}s')
    keyword.set('duration', f'{duration}s')
    keyword.set('value', 'scenes')
    keywords.append(keyword)

  return keywords


def clean_up_xml(config):
  prepend_info = '<?xml version="1.0" encoding="UTF-8"?>\n<!DOCTYPE fcpxml>\n\n'
  with open(config.outfile) as f:
    xml_data = f.read()

  with open(config.outfile, 'w') as f:
    f.write(prepend_info + xml_data)


def prettify(elem):
  """Return a pretty-printed XML string for the Element.
    """
  rough_string = ET.tostring(elem, 'utf-8')
  reparsed = minidom.parseString(rough_string)
  return reparsed.toprettyxml(indent="  ")


if __name__ == '__main__':
  main()