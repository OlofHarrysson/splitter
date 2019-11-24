import moviepy.editor as mpy
import numpy as np
import cv2
from PIL import Image

from collections import defaultdict

dict_imgs = defaultdict(list)
# with open(txt_path) as f:
#   lines = f.read().splitlines()

lines = ['qwe', '12312', 1]
dict_imgs[0] = lines

print(dict_imgs)
qwe

# for index, line in enumerate(lines):
#   line = line.rstrip()
#   dict_imgs[index].append(line)

# from skvideo.io import VideoWriter
import skvideo.io
import numpy

# writer = VideoWriter(filename, frameSize=(w, h))
# writer.open()
outputdata = np.random.random(size=(5, 480, 680, 3)) * 255
outputdata = outputdata.astype(np.uint8)

writer = skvideo.io.FFmpegWriter("outputvideo.mp4")
for i in range(5):
  writer.writeFrame(outputdata[i, :, :, :])
writer.close()
# writer.write(image)
# writer.release()

# clip = mpy.VideoClip()

# frames = []
# for i in range(112):
#   frames.append(np.random.randn(100, 100, 3).astype(np.uint8))

# def make_frame(t):
#   print(t)
#   t = int(t)
#   """Returns an image of the frame for time t."""
#   # ... create the frame with any library here ...
#   # print(t)
#   # print(type(t))
#   # print(ims)
#   a = frames[t]
#   # print(a.shape)
#   # qwe
#   return a  # (Height x Width x 3) Numpy array

# fps = 5
# duration = len(frames) / fps
# print(duration)
# clip = mpy.VideoClip(make_frame, duration=duration)
# clip.write_videofile('out.mp4', fps=fps)

# fps = 15
# capSize = (1028, 720)  # this is the size of my source video
# # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')  # note the lower case
# # vout = cv2.VideoWriter()
# # success = vout.open('output.mov', fourcc, fps, capSize, True)
# # print(success)

# # fourcc = cv2.VideoWriter_fourcc('8', 'B', 'P', 'S')
# # fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
# # fourcc = cv2.VideoWriter_fourcc(-1)
# # vout = cv2.VideoWriter('output.mp4v', fourcc, 10, capSize)
# # vout = cv2.VideoWriter()
# # succes = vout.open('output.mp4v', fourcc, 15.0, (1280, 720), True)
# # print(succes)

# for i in range(50):
#   frame = np.random.randn(1028, 720, 3).astype(np.uint8)
#   im = Image.fromarray(frame)
#   out_path = f'frames/{i}.jpg'
#   im.save(out_path)
#   # vout.write(frame)

# vout.release()
# vout = None
# cv2.destroyAllWindows()

# Create a VideoCapture object
# cap = cv2.VideoCapture(0)

# # Check if camera opened successfully
# if (cap.isOpened() == False):
#   print("Unable to read camera feed")

# # Default resolutions of the frame are obtained.The default resolutions are system dependent.
# # We convert the resolutions from float to integer.
# frame_width = int(cap.get(3))
# frame_height = int(cap.get(4))

# # Define the codec and create VideoWriter object.The output is stored in 'outpy.avi' file.
# out = cv2.VideoWriter('outpy.avi', cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
#                       10, (frame_width, frame_height))

# while (True):
#   ret, frame = cap.read()

#   if ret == True:

#     # Write the frame into the file 'output.avi'
#     out.write(frame)

#     # Display the resulting frame
#     cv2.imshow('frame', frame)

#     # Press Q on keyboard to stop recording
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#       break

#   # Break the loop
#   else:
#     break

# # When everything done, release the video capture and video write objects
# cap.release()
# out.release()

# # Closes all the frames
# cv2.destroyAllWindows()