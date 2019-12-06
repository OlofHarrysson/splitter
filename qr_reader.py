from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol
from PIL import Image
import pyqrcode
import cv2
import aztec_code_generator
import sys
import subprocess
from pathlib import Path


def create_qr():
  qr = pyqrcode.create(1, error='L', version=1)
  print(qr)
  qr.png("qr_codes/test1.png", scale=10)

  # aztec_code = aztec_code_generator.AztecCode('Aztec Code 2D :)')
  # aztec_code.save("qr_codes/test1.png", module_size=8)


def image_reader():
  create_qr()
  im = Image.open('qr_codes/test1.png')
  # im = Image.open('qr_codes/side.jpg')
  data = decode(im)
  print(data)


def read_qr(im):
  # return decode(im)
  return decode(im, symbols=[ZBarSymbol.QRCODE])


def squeeze_detections(qr_detections):
  ''' Squeezes many detections into one '''
  last_detection_frame = -sys.maxsize
  fps = 12
  seconds = 1
  detection_window = seconds * fps

  squeezed_dets = {}

  print(list(qr_detections.keys()))

  for frame_n, qr_det in qr_detections.items():

    if frame_n - last_detection_frame > detection_window:
      squeezed_dets[frame_n] = qr_det

    last_detection_frame = frame_n

  print(list(squeezed_dets.keys()))
  return squeezed_dets


def split_video(qr_detections, input_file, fps):

  start_frames, end_frames = [], []

  for frame, action in qr_detections.items():
    if action == 'start scene':
      start_frames.append(frame)
    elif action == 'end scene':
      end_frames.append(frame)
    else:
      assert False
  scene_name = 0
  for start_frame, end_frame in zip(start_frames, end_frames):
    print(start_frame, end_frame)
    scene_start = start_frame / fps
    duration = (end_frame - start_frame) / fps
    print(scene_start, duration)
    file_ending = input_file.suffix
    args = [
      'ffmpeg', '-i',
      str(input_file), '-ss', f'{scene_start}', '-t', f'{duration}', '-c',
      'copy', f'movie_outputs/scene_{scene_name}.{file_ending}'
    ]
    completed = subprocess.run(args, capture_output=True)
    print('returncode:', completed.returncode)
    scene_name += 1


def video_reader():
  # input_file = Path('movies/home.avi')
  input_file = Path('movies/work.mp4')
  cap = cv2.VideoCapture(str(input_file))
  fps = cap.get(cv2.CAP_PROP_FPS)

  success, im = cap.read()
  frame_n = 0
  analyse_frequency = 10
  qr_detections = {}

  while success:
    frame_n += 1
    success, im = cap.read()

    if frame_n % analyse_frequency == 0:
      qr_info = read_qr(im)
      print(qr_info)

      if qr_info:
        qr_detections[frame_n] = qr_info[0].data.decode("utf-8")

      cv2.imshow('frame', im)
      k = cv2.waitKey(1)

  # print(qr_detections)

  qr_detections = squeeze_detections(qr_detections)
  split_video(qr_detections, input_file, fps)

  cv2.waitKey(1)
  cap.release()
  cv2.destroyAllWindows()


def clear_outputdir():
  for file in Path('movie_outputs').iterdir():
    file.unlink()


if __name__ == '__main__':
  clear_outputdir()

  # image_reader()
  video_reader()
