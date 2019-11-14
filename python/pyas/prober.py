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


  def print_video_info(self, video_path):
    videos = (dir_videos for dir_videos in os.listdir(video_path))
    videos = list(videos)
    videos.sort()
    for video_name in videos:
      video = os.path.join(video_path, video_name)
      probe = ffmpeg.probe(video)
      video_stream = next((stream for stream in probe['streams']\
          if stream['codec_type'] == 'video'), None)
      if video_stream is not None:
        width = video_stream['width']
        height = video_stream['height']
        frames, sec = video_stream['r_frame_rate'].split('/')
        framerate = int(int(frames)/int(sec))
        bitrate = video_stream['bit_rate']
        print(video_name, " w/h/fr/br: {0}/{1}/{2}/{3}".format(width,
          height, framerate, bitrate))


if __name__ == "__main__":
  import time
  repo_home = os.environ['REPO_HOME']
  input_video = os.path.join(repo_home, "input/5sec.mp4")
  print(input_video)
  prober = Prober.get_instance()

  start_time = time.time()
  w, h, fr, br = prober.get_video_info(input_video)
  execution_time = (time.time() - start_time) * 1000


  video_dir = os.path.join(repo_home, "input")
  prober.print_video_info(video_dir)

