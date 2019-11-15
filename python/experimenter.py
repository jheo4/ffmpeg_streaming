# syslib
import os
import time

# ffmpeg
import ffmpeg

# data processing
import pandas as pd

# pyas
from pyas.transcoder import Transcoder
from pyas.prober import Prober
from pyas.variant_generator import VariantGenerator
from pyas.error import raise_exception
from pyas.profiler import Profiler

class Experimenter:
  __instance = None
  transcoder = Transcoder.get_instance()
  prober = Prober.get_instance()
  variant_generator = VariantGenerator.get_instance()

  @staticmethod
  def get_instance():
    if Experimenter.__instance is None:
      Experimenter.__instance = Experimenter()
    return Experimenter.__instance


  def __init__(self):
    if Experimenter.__instance is not None:
      raise Exception("singleton violation, use get_instance")


  def create_dir(self, output_dir, video_name, codec):
    dir_path = os.path.join(output_dir, video_name)
    if not os.path.exists(dir_path):
      os.mkdir(dir_path, 0o755)
    dir_path = os.path.join(dir_path, codec)
    if not os.path.exists(dir_path):
      os.mkdir(dir_path, 0o755)
    return dir_path


  def do_experiment(self, input_dir='input', output_dir='output',
      codecs='libx264', containers='mp4', acceleration=False):
    if not os.path.exists(input_dir):
      raise_exception(Experimenter.__name__, sys._getframe().f_code.co_name,
          "input dir does not exist")
    if not os.listdir(input_dir):
      raise_exception(Experimenter.__name__, sys._getframe().f_code.co_name,
        "input dir is empty")
    if not os.path.exists(output_dir):
      os.mkdir(output_dir, 0o755)

    input_videos = (input_video for input_video in os.listdir(input_dir))
    buf_size = '8M'
    success_result = {}
    failed_result = {}
    # (videos)*(codecs)*(bitrates)*(resolutions) = total variants
    for input_video in input_videos:
      video_name_with_path = os.path.join(input_dir, input_video)
      resolutions, zipped_brs = \
          self.variant_generator.get_variant_list(video_name_with_path)

      for container in containers:
        for codec in codecs:
          video_name = input_video.split('.')[0]
          target_dir = self.create_dir(output_dir, video_name, codec)
          width, height, framerate, bitrate = \
              self.prober.get_video_info(video_name_with_path)

          for resolution, zipped_br in zip(resolutions, zipped_brs):
            #i = len(zipped_br)   # for the order of exported data
            for br_set in zipped_br:
              time.sleep(2)   # for profile...
              if(acceleration is True):
                output_fn = "acc_" + resolution + "_" +  "_" \
                    + br_set['avg'] + "." + container
              else:
                output_fn = resolution + "_" + br_set['avg'] \
                    + "." + container
              #i -= 1

              target_output = os.path.join(target_dir, output_fn)

              start_time = time.time()
              if(acceleration is True):
                self.transcoder.gpu_transcode(video_name_with_path, codec,
                    container, br_set['avg'], br_set['min'], br_set['max'],
                    buf_size, resolution, target_output)
              else:
                self.transcoder.sw_transcode(video_name_with_path, codec,
                    container, br_set['avg'], br_set['min'], br_set['max'],
                    buf_size, resolution, target_output)
              elapsed_time = time.time() - start_time

              result_key = video_name + "_" + codec + "_" + container + "_" + \
                  resolution + "_" + br_set['avg']

              if(elapsed_time > 1): # success
                success_result[result_key] = elapsed_time
              else:
                failed_result[result_key]

    return success_result, failed_result


  def export_result(self, res_dict, out_fn):
    if not bool(res_dict):
      raise_exception(Experimenter.__name__, sys._getframe().f_code.co_name,
          "the given dictionary is empty")

    repo_home = os.environ['REPO_HOME']
    output_dir = os.path.join(repo_home, "output")
    output_res = os.path.join(output_dir, out_fn)
    keys = list(res_dict.keys())
    values = list(res_dict.values())
    data = pd.DataFrame({
        'keys': keys,
        'transcoding time': values
      })
    data.to_csv(output_res, index=False)


if __name__ == "__main__":
  from data_exporter import *
  repo_home = os.environ['REPO_HOME']
  input_dir = os.path.join(repo_home, "input")
  output_dir = os.path.join(repo_home, "output")

  experimenter = Experimenter.get_instance()
  codecs = ['libx264']
  containers = ['mp4']

  profiler = Profiler.get_instance()
  res, dps, columns, values = profiler.profile_cpu(5,
      experimenter.do_experiment,
      [input_dir, output_dir, codecs, containers, False])

  sw_sucess_res = res[0]
  sw_failed_res = res[1]
  experimenter.export_result(sw_sucess_res, "sw_res.csv")
  write_csv(output_dir, 'cpu_usage.csv', dps, columns, values)

