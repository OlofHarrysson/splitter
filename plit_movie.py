import subprocess
import json
import datetime
from datetime import date
from pathlib import Path


def clear_outputdir():
  for file in Path('movie_outputs').iterdir():
    file.unlink()


def main():
  clear_outputdir()

  with open('scene_times.json') as infile:
    scenes = json.load(infile)

  metadata = scenes['metadata']
  for scene in scenes['scenes']:
    cut_scene(scene, metadata)


def cut_scene(scene, metadata):
  fps = metadata['fps']
  scene_name = scene['scene_name']
  scene_start = scene['frame_start'] / fps
  duration = scene['frame_duration'] / fps

  # record_start = datetime.datetime.strptime(metadata['start_time'],
  #                                           '%Y-%m-%d %H:%M:%S.%f')
  # scene_start_abs = datetime.datetime.strptime(scene['starttime'],
  #                                              '%Y-%m-%d %H:%M:%S.%f')
  # scene_stop_abs = datetime.datetime.strptime(scene['stoptime'],
  #                                             '%Y-%m-%d %H:%M:%S.%f')

  # scene_start = (scene_start_abs - record_start).total_seconds()
  # scene_stop = (scene_stop_abs - record_start).total_seconds()
  print(scene_start, duration)

  args = [
    'ffmpeg', '-i', 'movies/output.avi', '-ss', f'{scene_start}', '-t',
    f'{duration}', '-c', 'copy', f'movie_outputs/scene_{scene_name}.avi'
  ]
  completed = subprocess.run(args, capture_output=True)
  print('returncode:', completed.returncode)


if __name__ == '__main__':
  main()