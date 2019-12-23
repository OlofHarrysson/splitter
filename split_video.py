from PIL import Image
import pyqrcode
import cv2
import aztec_code_generator
import sys
import subprocess
from pathlib import Path
import anyfig
from signal_detectors import ZbarQRDetector, OpenCVDetector
import numpy as np
import json


@anyfig.config_class
class Config():
  def __init__(self):
    # self.input_file = Path('movies/work.mp4')
    self.input_file = Path('movies/home.avi')
    # self.input_file = Path('movies/intro1.mp4')
    # self.input_file = Path('movies/park.MOV')
    # self.input_file = Path('movies/birds.MOV')
    # self.input_file = Path('movies/output.avi')

    # QR detection algorithm
    self.qr_detector = ZbarQRDetector()
    # self.qr_detector = OpenCVDetector()

    # Video file
    self.video_cap = cv2.VideoCapture(str(self.input_file))
    self.fps = self.video_cap.get(cv2.CAP_PROP_FPS)

    # How often to check for qr codes. Measures in frames
    freq_sec = 0.7  # In seconds
    # freq_sec = 0.2  # In seconds
    self.check_frame_frequency = int(freq_sec * self.fps)

    # Merges detections close in time. Measured in seconds
    n_sec = 3
    self.detection_squeeze_window = n_sec * self.fps

    # self.show_video = False
    self.show_video = True

    # Actions available
    self.start_signal = ['start scene', 'start']
    self.end_signal = ['end scene', 'stop']


def main():
  config = anyfig.setup_config(default_config='Config')
  print(config)
  input_file = config.input_file
  assert input_file.exists(), f'Wrong path to video: {input_file}'

  qr_detections = find_detections(config)

  qr_detections = squeeze_detections(qr_detections,
                                     config.detection_squeeze_window)

  action_frames = format_detections(qr_detections, config)

  print(f"Actions: {action_frames}")

  split_info = split_video(action_frames, input_file, config.fps)
  save_split_info(split_info, input_file)

  cv2.waitKey(1)
  config.video_cap.release()
  cv2.destroyAllWindows()


def find_detections(config):
  frame_n = 0
  qr_detections = {}
  video_cap = config.video_cap
  detector = config.qr_detector

  window_name = 'image'
  cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
  cv2.resizeWindow(window_name, 1280, 1024)
  cv2.moveWindow(window_name, 20, 20)

  success, im = video_cap.read()
  while success:
    frame_n += 1

    if frame_n % config.check_frame_frequency == 0:
      qr_detection = detector.find_qr(im)

      if qr_detection['text']:
        qr_detections[frame_n] = qr_detection['text']

      if config.show_video:
        im = detector.draw_bounding_box(im, qr_detection)
        cv2.imshow(window_name, im)
      else:
        print(qr_detection)

      k = cv2.waitKey(1)

    success, im = video_cap.read()

  return qr_detections


def squeeze_detections(qr_detections, detection_squeeze_window):
  ''' Squeezes many detections into one '''
  last_detection_frame = -sys.maxsize
  squeezed_dets = {}

  print(list(qr_detections.keys()))
  for frame_n, qr_det in qr_detections.items():

    if frame_n - last_detection_frame > detection_squeeze_window:
      squeezed_dets[frame_n] = qr_det

    last_detection_frame = frame_n

  print(list(squeezed_dets.keys()))
  return squeezed_dets


def format_detections(qr_detections, config):
  action_frames = []
  start_frame, end_frame = None, None
  for frame, action in qr_detections.items():
    if action in config.start_signal:
      start_frame = frame
    if action in config.end_signal and start_frame:
      end_frame = frame

    if start_frame and end_frame:
      action_frames.append((start_frame, end_frame))
      start_frame, end_frame = None, None

  return action_frames


def split_video(action_frames, input_file, fps):
  split_info = {}
  for scene_index, (start_frame, end_frame) in enumerate(action_frames):
    scene_start = start_frame / fps
    duration = (end_frame - start_frame) / fps  # In seconds
    file_ending = input_file.suffix
    args = [
      'ffmpeg', '-i',
      str(input_file), '-ss', f'{scene_start}', '-t', f'{duration}', '-c',
      'copy', f'movie_outputs/scene_{scene_index}.{file_ending}'
    ]
    completed = subprocess.run(args, capture_output=True)
    print('returncode:', completed.returncode)
    split_info[scene_index] = (scene_start, duration)

  return split_info


def save_split_info(split_info, filename):
  data = dict(filename=str(filename), scenes=split_info)
  with open('scene_splits.json', 'w') as outfile:
    json.dump(data, outfile, indent=2)


def clear_outputdir():
  for file in Path('movie_outputs').iterdir():
    file.unlink()


if __name__ == '__main__':
  clear_outputdir()
  main()
