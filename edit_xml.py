from pathlib import Path
import anyfig
from lxml import etree
import subprocess

from utils import xml_utils


def main(xml_file, analyzed_metadatum, send_to_finalcut):
  tree, root = xml_utils.read_xml(xml_file)

  # Add smart collection
  events = root.findall('./library/event')
  smart_collection = create_smart_collection()
  for event in events:
    event.append(smart_collection)

  # Add metadata
  for analyzed_metadata in analyzed_metadatum:
    found_actions = analyzed_metadata['actions']
    for clip in root.iter('asset-clip'):

      if clip.attrib['ref'] == analyzed_metadata['id']:
        if 'clips' in found_actions:
          keywords = get_clips(found_actions['clips'])
          clip = xml_utils.add_children(clip, children=keywords)

        if 'markers' in found_actions:
          markers = get_markers(found_actions['markers'])
          clip = xml_utils.add_children(clip, children=markers)

  tmp_xmlpath = '/tmp/final_cut_metadata.fcpxml'
  xml_utils.save_xml(tree, tmp_xmlpath)
  if send_to_finalcut:
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


def get_markers(markers):
  xml_markers = []
  for marker in markers:
    time, tag = marker['time'], marker['name']

    attrs = dict(start=f'{time}s', duration='1s', value=f'videohelper {tag}')
    xml_markers.append(xml_utils.create_element('marker', attrs))

  return xml_markers


def get_clips(clips):
  xml_keywords = []
  for clip in clips:
    start, duration = clip['start_time'], clip['duration']

    attrs = dict(start=f'{start}s',
                 duration=f'{duration}s',
                 value=f'videohelper clips')
    xml_keywords.append(xml_utils.create_element('keyword', attrs))

  return xml_keywords


if __name__ == '__main__':
  main()