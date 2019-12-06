from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol
from PIL import Image
import pyqrcode
import cv2
import aztec_code_generator
import sys
import subprocess
from pathlib import Path
import anyfig


@anyfig.config_class
class Config():
  def __init__(self):
    self.input_file = Path('movies/work.mp4')
    # self.input_file = Path('movies/home.avi')

    # How often to check for qr codes. Measured in #frames
    self.qr_detection_frequency = 20

    # Merges detections close in time. Measured in seconds
    self.detection_squeeze_window = 3

    # self.show_video = False
    self.show_video = True


def main():
  config = anyfig.setup_config(default_config='Config')

  cap = cv2.VideoCapture(str(config.input_file))
  fps = cap.get(cv2.CAP_PROP_FPS)
  qr_detections = find_detections(cap, fps, config)

  qr_detections = squeeze_detections(qr_detections,
                                     config.detection_squeeze_window, fps)
  split_video(qr_detections, config.input_file, fps)

  cv2.waitKey(1)
  cap.release()
  cv2.destroyAllWindows()


def find_detections(cap, fps, config):
  frame_n = 0
  qr_detections = {}

  success, im = cap.read()
  while success:
    frame_n += 1
    success, im = cap.read()

    if frame_n % config.qr_detection_frequency == 0:
      qr_info = read_qr(im)
      print(qr_info)

      if qr_info:
        qr_detections[frame_n] = qr_info[0].data.decode("utf-8")

      if config.show_video:
        cv2.imshow('frame', im)
      k = cv2.waitKey(1)

  return qr_detections


def read_qr(im):
  return decode(im, symbols=[ZBarSymbol.QRCODE])


def squeeze_detections(qr_detections, detection_squeeze_window, fps):
  ''' Squeezes many detections into one '''
  last_detection_frame = -sys.maxsize
  detection_window = detection_squeeze_window * fps

  squeezed_dets = {}

  print(list(qr_detections.keys()))
  for frame_n, qr_det in qr_detections.items():

    if frame_n - last_detection_frame > detection_window:
      squeezed_dets[frame_n] = qr_det

    last_detection_frame = frame_n

  print(list(squeezed_dets.keys()))
  return format_detections(squeezed_dets)


def format_detections(qr_detections):
  action_frames = []
  start_frame, end_frame = None, None
  for frame, action in qr_detections.items():
    if action == 'start scene':
      start_frame = frame
    if action == 'end scene' and start_frame:
      end_frame = frame

    if start_frame and end_frame:
      action_frames.append((start_frame, end_frame))
      start_frame, end_frame = None, None

  return action_frames


def split_video(action_frames, input_file, fps):
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


def clear_outputdir():
  for file in Path('movie_outputs').iterdir():
    file.unlink()


if __name__ == '__main__':
  clear_outputdir()
  main()
