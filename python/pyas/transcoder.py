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


  def run_ffmpeg(self, in_args, out_args):
    command = ['ffmpeg', '-y']
    command.extend(in_args)
    command.extend(out_args)

    start_time = time.time()
    subprocess.run(command)
    execution_time = (time.time() - start_time)

    return execution_time


  def run_mp4box(self, args):
    command = ['MP4Box']
    command.extend(args)
    print(command)

    start_time = time.time()
    subprocess.run(command)
    execution_time = (time.time() - start_time)

    return execution_time


  def convert_to_gpu_res(self, res):
    x, y = res.split('x')
    return '{}:{}'.format(x, y)


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

    return self.run_ffmpeg(in_args, out_args)


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

    return self.run_ffmpeg(in_args, out_args)


  def sw_generate_mpd(self, input, codec, container, brs, buf, res, output):
    # 0: 480, 1: 720, 2: 1080, 3:1440, 4:2160
    # Target Command
	  #   ffmpeg -re -stream_loop -0  -i 5sec.mp4 \
		#     -map 0 -map 0 -map 0 -c:a aac -c:v libx264 \
		#     -b:v:0 800k -s:v:0 1280x720 -profile:v:0 main \
		#     -b:v:1 500k -s:v:1 640x340  -profile:v:1 main \
		#     -b:v:2 300k -s:v:2 320x170  -profile:v:2 baseline \
		#     -bf 1 -keyint_min 120 -g 120 -sc_threshold 0 -b_strategy 0 \
		#     -ar:a:1 22050 -use_timeline 1 -use_template 1 \
		#     -window_size 5 -adaptation_sets "id=0,streams=v id=1,streams=a" \
		#     -hls_playlist 1 -seg_duration 4 -streaming 1 -remove_at_exit 1 \
		#     -f dash manifest.mpd

    in_args = [
      '-re',
      '-stream_loop', '-0',
      '-i', input
    ]

    out_args = [
      '-map', '0',
      '-map', '0',
      '-map', '0',
      '-c:a', 'copy',
      '-ar:a:1', '22050',

      '-c:v', codec,
      '-b:v:0', brs[0],
      '-s:v:0', res[0],

      '-b:v:1', brs[1],
      '-s:v:1', res[1],

      '-b:v:2', brs[2],
      '-s:v:2', res[2],

      '-b:v:3', brs[3],
      '-s:v:3', res[3],

      '-b:v:4', brs[4],
      '-s:v:4', res[4],

      '-bf', '1',
      '-keyint_min', '120',
      '-g', '120',
      '-sc_threshold', '0',
      '-b_strategy', '0',

      '-use_timeline', '1',
      '-use_template', '1',
      '-window_size', '10',
      '-adaptation_sets', 'id=0,streams=v id=1,streams=a',
      '-hls_playlist', '1',
      '-seg_duration', '5',
      '-streaming', '1',
      '-f', container,
      output
    ]

    return self.run_ffmpeg(in_args, out_args)


  def gpu_generate_mpd(self, input, codec, container, brs, buf, res, output):
    decoder, encoder = self.accelerated_codec_convert(codec=codec)
    dir = os.path.dirname(output)

    transcoded_files = []
    for i in range(0, len(res)):
      transcoded_files.append(os.path.join(dir, (res[i] + "." + container)))

    if decoder is None and encoder is None:
      raise_exception(self.__name__, sys._getframe().f_code.co_name,
          "this codec is not supported by Nividia GPU")

    # Target command
    #   ffmpeg -y -re -vsync 0 -hwaccel cuvid -c:v h264_cuvid -i input.mp4 \
    #     -an -vf scale_npp=1280:720 -c:v h264_nvenc -b:v 5M -dash 1 -f mp4 output_720.mp4 \
    #     -an -vf scale_npp=640:320 -c:v h264_nvenc -b:v 3M -dash 1 -f mp4 output_360.mp4 \
    #     -c:a copy -b:a 128k -vn -f mp4 -dash 1 audio_128k.mp4

    in_args = [
      '-re',
      '-hwaccel_device', '0',
      '-hwaccel', 'cuvid',
      '-c:v', decoder,
      '-vsync', '0',
      '-i', input
    ]

    # 0: 480, 1: 720, 2: 1080, 3:1440, 4:2160
    out_args = []
    for i in range(0, len(res)):
      out_args.extend([
          '-an', '-vf', 'scale_npp={}'.format(self.convert_to_gpu_res(res[i])),
          '-c:v', encoder,
          '-b:v', brs[i],
          '-dash', '1',
          '-f', container,
          transcoded_files[i],
      ])
    out_args.extend([
        '-c:a', 'copy',
        '-b:a', '128k',
        '-vn', '-f', container,
        '-dash', '1',
        os.path.join(dir, ('audio' + '.' + container))
    ])

    ffmpeg_exectime = self.run_ffmpeg(in_args, out_args)

    # Target command
    # MP4Box -dash 4000 -frag 4000 -rap -profile live -out output.mpd output_360.mp4 output_720.mp4 audio_128k.mp4
    args = [
      '-dash', '4000',
      '-frag', '4000',
      '-rap', '-profile', 'live',
      '-out', output
    ]
    for i in range(0, len(res)):
      args.extend([transcoded_files[i]])
    args.extend([os.path.join(dir, ('audio' + '.' + container))])

    mp4box_exectime = self.run_mp4box(args)
    return ffmpeg_exectime + mp4box_exectime


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
      container='mp4', brs=['1M', '2M', '3M', '4M', '5M'], buf='16M',
      res=['720x480', '1280x720'],
      output=acc_output_mpd)


  print("*  *  *  *  *  *  *  *  *  *  *  *")
  print("\tsw transcoding time: ", sw_trans)
  print("\tsw mpd generating time: ", sw_mpd)
  print("\tgpu transcoding time: ", gpu_trans)
  print("\tgpu mpd generating time: ", gpu_mpd)
  print("*  *  *  *  *  *  *  *  *  *  *  *")

