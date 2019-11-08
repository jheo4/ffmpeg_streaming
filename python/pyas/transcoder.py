# system lib
import sys
import os
import multiprocessing
import time

# ffmpeg
import ffmpeg

# pyas
from pyas.error import raise_exception
from pyas.variant_generator import VariantGenerator

class Transcoder:
  __instance = None

  @staticmethod
  def get_instance():
    if Transcoder.__instance is None:
      Transcoder.__instance = Transcoder()
    return Transcoder.__instance


  def __init__(self):
    if Transcoder.__instance is not None:
      raise Exception("singleton violation, use get_instance")


  def sw_transcode(self, input_filename, codec, container, bitrate, resolution,
      output_filename):
    # To tell ffmpeg to read from stdin/write to stdout, use 'pipe:' as the
    # filename.

    output_args = {
      'threads': multiprocessing.cpu_count(),
      'preset': 'fast',
      'vcodec': codec,
      'acodec': 'copy',
      's': resolution,
      'b:v': bitrate,
      'f': container
    }

    start_time = time.time()
    (
        ffmpeg
          .input(input_filename)
          .output(output_filename, **output_args)
          .run()
    )
    execution_time = (time.time() - start_time)
    return execution_time


  def accelerated_codec_convert(self, codec):
    if codec == "libx264":
      return "h264_cuvid", "h264_nvenc"
    elif codec == "mpeg4":
      # decoding only
      print("* * * only decoding process is accelerated... * * *")
      return "mpeg4_cuvid", "mpeg4"
    elif codec == "libvpx-vp9":
      # decoding only
      print("* * * only decoding process is accelerated... * * *")
      return "vp9_cuvid", "libvpx-vp9"
    elif codec == "libx265":
      return "hevc_cuvid", "hevc_nvenc"
    else:
      return None, None


  def gpu_transcode(self, input_filename, codec, container, bitrate,
      resolution, output_filename):


    decoder, encoder = self.accelerated_codec_convert(codec=codec)
    if decoder is None and encoder is None:
      raise_exception(self.__name__, sys._getframe().f_code.co_name,
          "this codec is not supported by Nividia GPU")

    input_args = {
      'hwaccel': 'nvdec',
      'vcodec': decoder,
      'c:v': decoder,
      'vsync': 0
    }

    output_args = {
      'acodec': 'copy',
      'vcodec': encoder,
      'c:v': encoder,
      'preset': 'fast',
      'b:v': bitrate,
      'f': container
    }


    start_time = time.time()
    (
      ffmpeg
        .input(input_filename, **input_args)
        .output(output_filename, **output_args)
        .run()
    )
    execution_time = (time.time() - start_time)
    return execution_time


if __name__ == "__main__":
  from pyas.prober import Prober

  repo_home = os.environ['REPO_HOME']
  input_video = os.path.join(repo_home, "input/5sec.mp4")
  output_video = os.path.join(repo_home, "output/test_out.mp4")
  prober = Prober.get_instance()
  transcoder = Transcoder.get_instance()

  start_time = time.time()
  w, h, fr, br = prober.get_video_info(input_video)
  execution_time = (time.time() - start_time) * 1000
  print("probe execution time: {0:.3f}ms".format(execution_time))

  sw_trans = transcoder.sw_transcode(input_filename=input_video,
      codec='libx264', container='mp4', bitrate=3000000,
      resolution='1920x1080', output_filename=output_video)

  gpu_trans = transcoder.gpu_transcode(input_filename=input_video,
      codec='libx264', container='mp4', bitrate=3000000,
      resolution='1920x1080', output_filename=output_video)

  print("*  *  *  *  *  *  *  *  *  *  *  *")
  print("\tsw transcoding time: ", sw_trans)
  print("\tgpu transcoding time: ", gpu_trans)
  print("*  *  *  *  *  *  *  *  *  *  *  *")

