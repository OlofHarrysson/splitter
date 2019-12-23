from pyzbar.pyzbar import decode
from pyzbar.wrapper import ZBarSymbol
import cv2
import shapely
from shapely.geometry import MultiPoint
import numpy as np


class QR_Detector():
  def draw_bounding_box(self, im, qr_detection):
    if qr_detection['text']:
      red_color = (0, 0, 255)
      points = qr_detection['points'].astype(np.int32)

      im = cv2.polylines(im, [points],
                         isClosed=True,
                         color=red_color,
                         thickness=4)

      x, y = points[3][0][0], points[3][0][1]  # Point for top left
      cv2.putText(im, qr_detection['text'], (x, y - 10),
                  cv2.FONT_HERSHEY_SIMPLEX, 1.5, red_color, 2)
    return im


class OpenCVDetector(QR_Detector):
  def __init__(self):
    self.qrDecoder = cv2.QRCodeDetector()

  def find_qr(self, image):
    data, points, rectifiedImage = self.qrDecoder.detectAndDecode(image)
    return dict(text=data, points=points)


class ZbarQRDetector(QR_Detector):
  def find_qr(self, image):
    detection = decode(image, symbols=[ZBarSymbol.QRCODE])
    if not detection:
      return dict(text=None, points=None)

    text = detection[0].data.decode("utf-8")
    points = detection[0].polygon
    points = np.array([[p.x, p.y] for p in points])
    return dict(text=text, points=np.expand_dims(points, 1))
