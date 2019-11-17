# syslib
import sys
import os
import multiprocessing
import subprocess
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


  def run(self, in_args, out_args):
    command = ['ffmpeg', '-y']
    command.extend(in_args)
    command.extend(out_args)

    start_time = time.time()
    subprocess.run(command)
    execution_time = (time.time() - start_time)

    return execution_time



  def sw_transcode(self, input, codec, container, brs, buf, res, output):
    # To tell ffmpeg to read from stdin/write to stdout, use 'pipe:' as the
    # filename.

    in_args = [
      '-i', input
    ]
    out_args = [
      #'-threads', str(multiprocessing.cpu_count()),
      '-threads', '0',
      '-preset', 'fast',
      '-vcodec', codec,
      '-acodec', 'copy',
      '-s', res,
      '-b:v', brs['avg'],
      '-minrate', brs['min'],
      '-maxrate', brs['max'],
      '-bufsize', buf,
      '-f', container,
      output
    ]

    return self.run(in_args, out_args)


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


  def gpu_transcode(self, input, codec, container, brs, buf, res, output):
    decoder, encoder = self.accelerated_codec_convert(codec=codec)
    if decoder is None and encoder is None:
      raise_exception(self.__name__, sys._getframe().f_code.co_name,
          "this codec is not supported by Nividia GPU")

    in_args = [
      '-hwaccel_device', '0',
      '-hwaccel', 'cuvid',
      '-vcodec', decoder,
      '-c:v', decoder,
      '-resize', res,
      '-vsync', '0',
      '-i', input
    ]

    out_args = [
      '-acodec', 'copy',
      '-vcodec', encoder,
      '-c:v', encoder,
      '-b:v', brs['avg'],
      '-minrate', brs['min'],
      '-maxrate', brs['max'],
      '-bufsize', buf,
      '-f', container,
      output
    ]

    return self.run(in_args, out_args)


  def sw_generate_mpd(self, input, codec, container, brs, buf, res, output):
    in_args = [
      '-re',
      '-i', input
    ]
    print(res)
    print(brs)
    # 0: 480, 1: 720, 2: 1080, 3:1440, 4:2160
    out_args = [
      '-map', '0:0',
      '-map', '0:1',
      '-c:a', 'copy',
      '-ar:a:1', '22050',

      '-c:v', codec,
      '-b:v', brs[0],
      '-s:v', res[0],

      '-b:v', brs[1],
      '-s:v', res[1],

      '-b:v', brs[2],
      '-s:v', res[2],

      '-b:v', brs[3],
      '-s:v', res[3],

      '-b:v', brs[4],
      '-s:v', res[4],

      '-use_timeline', '1',
      '-window_size', '10',
      '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
      '-f', container,
      output
    ]

    return self.run(in_args, out_args)


  def gpu_generate_mpd(self, input, codec, container, brs, buf, res, output):
    decoder, encoder = self.accelerated_codec_convert(codec=codec)
    if decoder is None and encoder is None:
      raise_exception(self.__name__, sys._getframe().f_code.co_name,
          "this codec is not supported by Nividia GPU")

    in_args = [
      '-re',
      '-hwaccel_device', '0',
      '-hwaccel', 'cuvid',
      '-vcodec', decoder,
      '-c:v', decoder,
      '-vsync', '0',
      '-i', input
    ]

    # 0: 480, 1: 720, 2: 1080, 3:1440, 4:2160
    out_args = [
      '-map', '0:0',
      '-map', '0:1',
      '-c:a', 'copy',
      '-ar:a:1', '22050',

      '-vcodec', encoder,
      '-c:v', encoder,
      '-b:v', brs[0],
      '-s:v', res[0],

      '-b:v', brs[1],
      '-s:v', res[1],

      '-b:v', brs[2],
      '-s:v', res[2],

      '-b:v', brs[3],
      '-s:v', res[3],

      '-b:v', brs[4],
      '-s:v', res[4],

      '-use_timeline', '1',
      '-window_size', '10',
      '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
      '-f', container,
      output
    ]

    return self.run(in_args, out_args)


if __name__ == "__main__":
  repo_home = os.environ['REPO_HOME']

  input_video = os.path.join(repo_home, "input/5sec.mp4")
  sw_output_video = os.path.join(repo_home, "output/test_out.mp4")
  sw_output_mpd = os.path.join(repo_home, "output/test_out.mpd")
  acc_output_video = os.path.join(repo_home, "output/acc_test_out.mp4")
  acc_output_mpd = os.path.join(repo_home, "output/acc_test_out.mpd")

  transcoder = Transcoder.get_instance()

  sw_trans = transcoder.sw_transcode(input=input_video,
      codec='libx264', container='mp4', brs={'avg': '4M', 'min': '3M',
        'max': '5M'}, buf='16M', res='1920x1080', output=sw_output_video)

  sw_mpd = transcoder.sw_generate_mpd(input=input_video, codec='libx264',
      container='dash', brs=['1M', '2M', '3M', '4M', '5M'], buf='16M',
      res=['720x480', '1280x720', '1920x1080', '2560x1440', '3840x2160'],
      output=sw_output_mpd)

  gpu_trans = transcoder.gpu_transcode(input=input_video,
      codec='libx264', container='mp4', brs={'avg': '4M', 'min': '3M',
        'max': '5M'}, buf='8M', res='1920x1080', output=sw_output_video)

  gpu_mpd = transcoder.gpu_generate_mpd(input=input_video, codec='libx264',
      container='dash', brs=['1M', '2M', '3M', '4M', '5M'], buf='16M',
      res=['720x480', '1280x720', '1920x1080', '2560x1440', '3840x2160'],
      output=sw_output_mpd)


  print("*  *  *  *  *  *  *  *  *  *  *  *")
  print("\tsw transcoding time: ", sw_trans)
  print("\tsw mpd generating time: ", sw_mpd)
  print("\tgpu transcoding time: ", gpu_trans)
  print("\tgpu mpd generating time: ", gpu_mpd)
  print("*  *  *  *  *  *  *  *  *  *  *  *")

