# system lib
import sys
import os

# ffmpeg
import ffmpeg

# pyas
from pyas.error import raise_exception


class Prober:
  __instance = None

  @staticmethod
  def get_instance():
    if Prober.__instance == None:
      Prober.__instance = Prober()
    return Prober.__instance


  def __init__(self):
    if Prober.__instance is not None:
      raise Exception("singleton violation, use get_instance")


  def get_video_info(self, video_name):
    probe = ffmpeg.probe(video_name)

    video_stream = next((stream for stream in probe['streams']\
        if stream['codec_type'] == 'video'), None)
    if video_stream == None:
      raise_exception(Prober.__name__, sys._getframe().f_code.co_name,
          "NO video stream...")

    width = int(video_stream['width'])
    height = int(video_stream['height'])
    frames, sec = video_stream['r_frame_rate'].split('/')
    framerate = int(int(frames)/int(sec))
    bitrate = int(video_stream['bit_rate'])

    return width, height, framerate, bitrate


if __name__ == "__main__":
  import time
  repo_home = os.environ['REPO_HOME']
  input_video = os.path.join(repo_home, "input/5sec.mp4")
  print(input_video)
  prober = Prober.get_instance()

  start_time = time.time()
  w, h, fr, br = prober.get_video_info(input_video)
  execution_time = (time.time() - start_time) * 1000
  print("w/h/fr/br: ", w, h, fr, br)
  print("probe execution time: {0:.3f}ms".format(execution_time))

