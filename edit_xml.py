from pathlib import Path
import anyfig
import json
from lxml import etree

import xml_utils


@anyfig.config_class
class Config():
  def __init__(self):
    self.scene_input_file = Path('scene_splits.json')
    # self.xml_input_file = Path('finalcut_xml/home_split.fcpxml')
    self.xml_input_file = Path('finalcut_xml/tochange.fcpxml')
    self.outfile = Path('finalcut_xml/output.fcpxml')

    with open(self.scene_input_file) as infile:
      self.scene_splits = json.load(infile)


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)
  tree = etree.parse(str(config.xml_input_file))
  root = tree.getroot()
  # print_xml(root, only_keys=True)
  # print_xml(root, only_keys=False)
  clip_name = Path(config.scene_splits['filename']).stem

  # Add smart collection
  events = root.findall('./library/event')
  smart_collection = create_smart_collection()
  for event in events:
    event.append(smart_collection)

  # assert clip_name in clip.attrib['name'] # TODO:
  xml = config.scene_splits['xml_info']
  for clip in root.iter('asset-clip'):
    if clip.attrib['name'] == clip_name:
      keywords = get_clips(xml['clips'])
      xml_utils.add_children(clip, children=keywords)

      markers = get_markers(xml['markers'])
      xml_utils.add_children(clip, children=markers)

  xml_utils.save_xml(tree, str(config.outfile))


def create_smart_collection():
  attrs = dict(rule='includes', value='videohelper')
  m1 = xml_utils.create_element('match-text', attrs)

  attrs = dict(enabled='0', rule='includes', value='marker')
  m2 = xml_utils.create_element('match-text', attrs)

  attrs = dict(name='videohelper markers', match='all')
  smart_collection = xml_utils.create_element('smart-collection', attrs)

  return xml_utils.add_children(smart_collection, children=[m1, m2])


def get_markers(markers_json):
  markers = []
  for m_json in markers_json:
    time, tag = m_json['time'], m_json['name']

    attrs = dict(start=f'{time}s', duration='1s', value=f'videohelper {tag}')
    markers.append(xml_utils.create_element('marker', attrs))

  return markers


def get_clips(clips_json):
  keywords = []
  for clip_json in clips_json:
    start, duration = clip_json['start_time'], clip_json['end_time']
    # TODO: Add duration into json

    attrs = dict(start=f'{start}s',
                 duration=f'{duration}s',
                 value=f'videohelper clips')
    keywords.append(xml_utils.create_element('keyword', attrs))

  return keywords


if __name__ == '__main__':
  main()