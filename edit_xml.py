from pathlib import Path
import anyfig
import json
from lxml import etree
import subprocess

import xml_utils


def main(xml_file, analyzed_metadatum):
  tree = etree.parse(str(xml_file))
  root = tree.getroot()
  # print_xml(root, only_keys=True)
  # print_xml(root, only_keys=False)

  # Add smart collection
  events = root.findall('./library/event')
  smart_collection = create_smart_collection()
  for event in events:
    event.append(smart_collection)

  print(analyzed_metadatum)

  # Add metadata
  for analyzed_metadata in analyzed_metadatum:
    found_actions = analyzed_metadata['actions']
    for clip in root.iter('asset-clip'):

      if clip.attrib['ref'] == analyzed_metadata['id']:
        print(found_actions)
        if 'clips' in found_actions:
          keywords = get_clips(found_actions['clips'])
          clip = xml_utils.add_children(clip, children=keywords)

        if 'markers' in found_actions:
          markers = get_markers(found_actions['markers'])
          clip = xml_utils.add_children(clip, children=markers)

  tmp_xmlpath = '/tmp/final_cut_metadata.fcpxml'
  xml_utils.save_xml(tree, tmp_xmlpath)
  send_xml_to_finalcut(tmp_xmlpath)


def send_xml_to_finalcut(xml_path):
  args = ['osascript', 'finalcut_integration/send_data.scpt', xml_path]
  completed = subprocess.run(args, capture_output=True)
  print('returncode:', completed.returncode)


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
    start, duration = clip_json['start_time'], clip_json['duration']

    attrs = dict(start=f'{start}s',
                 duration=f'{duration}s',
                 value=f'videohelper clips')
    keywords.append(xml_utils.create_element('keyword', attrs))

  return keywords


if __name__ == '__main__':
  main()