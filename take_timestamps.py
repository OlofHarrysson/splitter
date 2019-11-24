import datetime
import sys
import json
import numpy as np
import cv2
from pathlib import Path


def main():
  wipe_scene()
  scene_name = 1
  cap = cv2.VideoCapture(0)

  # Check if camera opened successfully
  if cap.isOpened() == False:
    print("Unable to read camera feed")

  vid_path = Path(f'movies/output.avi')
  if vid_path.exists():
    vid_path.unlink()

  video_writer, fps = setup_writer(cap, str(vid_path))

  scene_metadata = {'start_time': start_time(), 'fps': fps}
  scenes = []
  n_frames = 0

  while True:
    start, stop, quit, frame_info = record_video(cap, video_writer)

    if quit:
      break

    scene_time = dict(scene_name=scene_name,
                      starttime=start,
                      stoptime=stop,
                      frame_start=frame_info['start'] + n_frames,
                      frame_duration=frame_info['stop'])
    scenes.append(scene_time)
    scene_name += 1
    n_frames += frame_info['stop']

  save_scenes(scenes, scene_metadata)
  # When everything done, release shit
  cv2.waitKey(1)
  cap.release()
  video_writer.release()
  cv2.destroyAllWindows()


def setup_writer(cap, path):
  frame_width = int(cap.get(3))
  frame_height = int(cap.get(4))
  fps = 12  # TODO: Isn't synced with input so causes drift
  out = cv2.VideoWriter(path, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'), fps,
                        (frame_width, frame_height))

  return out, fps


def wipe_scene():
  with open('scene_times.json', 'w') as outfile:
    outfile.write('')


def save_scenes(scenes, scene_metadata):
  data = {'metadata': scene_metadata, 'scenes': scenes}
  with open('scene_times.json', 'w') as outfile:
    json.dump(data, outfile, indent=2, default=str)


def start_time():
  return datetime.datetime.now()


def stop_time():
  return datetime.datetime.now()


def record_video(cap, video_writer):
  start = start_time()
  n_frames = 0
  frame_info = {}

  while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    n_frames += 1

    # Dunno why
    if ret != True:
      print("BREAKING BECAUSE OF SOME BUG I GUESS")
      break

    # Write to file
    video_writer.write(frame)

    # Display the resulting frames
    cv2.imshow('frame', frame)
    k = cv2.waitKey(10)

    # Start
    if k == ord('a'):
      start = start_time()
      frame_info['start'] = n_frames

    # Stop
    if k == ord('s'):
      frame_info['stop'] = n_frames
      return start, stop_time(), False, frame_info

    # Quit
    if k == ord('q'):
      return start, stop_time(), True, frame_info


if __name__ == '__main__':
  main()