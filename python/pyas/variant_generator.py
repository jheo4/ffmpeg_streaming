# system lib
import sys
import os

# ffmpeg
import ffmpeg

# pyas
from pyas.error import raise_exception
from pyas.prober import Prober

class VariantGenerator:
  __instance = None
  prober = Prober.get_instance()

  @staticmethod
  def get_instance():
    if VariantGenerator.__instance is None:
      VariantGenerator.__instance = VariantGenerator()
    return VariantGenerator.__instance


  def __init__(self):
    if VariantGenerator.__instance is not None:
      raise Exception("singleton violation, use get_instance")


  def calculate_bitrate_variants(self, original_bitrate, base_bitrates):
    if(original_bitrate > base_bitrates):
      offset = int(base_bitrates/4)
      max_bitrate = base_bitrates
    else:
      offset = int(original_bitrate/4)
      max_bitrate = original_bitrate
    half_offset = int(offset/2)

    results = []
    for i in range (3, -1, -1):
      avg_br = max_bitrate - (offset * i)
      min_br = avg_br - half_offset
      max_br = avg_br + half_offset

      results.append( {'avg': str(avg_br), 'min': str(min_br),
        'max': str(max_br)})
    return results


  def get_variant_list(self, video_name):
    width, height, framerate, bitrate = self.prober.get_video_info(video_name)
    resolutions = []
    zipped_bitrates = []
    base_bitrates = {
        '480': 1000000,
        '720': 2000000,
        '1080':4000000,
        '2160':8000000
        }

    if(height >= 480): # 480
      resolutions.append("720x480")
      bitrates = self.calculate_bitrate_variants(bitrate, base_bitrates['480'])
      zipped_bitrates.append(bitrates)

    if(height >= 720): # 720
      resolutions.append("1280x720")
      bitrates = self.calculate_bitrate_variants(bitrate, base_bitrates['720'])
      zipped_bitrates.append(bitrates)

    if(height >= 1080): # 1080
      resolutions.append("1920x1080")
      bitrates = \
          self.calculate_bitrate_variants(bitrate, base_bitrates['1080'])
      zipped_bitrates.append(bitrates)

    if(height >= 2160): # 4K
      resolutions.append("3840x2160")
      bitrates = \
          self.calculate_bitrate_variants(bitrate, base_bitrates['2160'])
      zipped_bitrates.append(bitrates)

    return resolutions, zipped_bitrates


if __name__ == "__main__":
  import time
  repo_home = os.environ['REPO_HOME']
  input_path = os.path.join(repo_home, "input/5sec.mp4")
  variant_generator = VariantGenerator.get_instance()

  start_time = time.time()
  resolutions, zipped_bitrates = variant_generator.get_variant_list(input_path)
  execution_time = (time.time() - start_time) * 1000
  print("*  *  *  *  *  *  *  *  *  *  *  *")
  print("variant_generator execution time: {0:.3f}ms".format(execution_time))
  print("\t", resolutions)
  print("\t", zipped_bitrates)
  print("*  *  *  *  *  *  *  *  *  *  *  *")

