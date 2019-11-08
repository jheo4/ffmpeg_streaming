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
    else:
      offset = int(original_bitrate/4)

    results = []
    for i in rnage (0, 4):
      results.append(original_bitrate - (offset * i))
    return results


  def get_variant_list(self, video_name):
    width, height, framerate, bitrate = self.prober.get_video_info(video_name)
    variant_resolutions = []
    variant_bitrates = []
    base_bitrates = {'480': 1000000, '720': 2000000,
        '1080':4000000, '2160':8000000}

    if(height >= 480): # 480
      variant_resolutions.append("720x480")
      bitrates = self.calculate_bitrate_variants(bitrate, base_bitrates['480'])
      variant_bitrates.append(bitrates)

    if(height >= 720): # 720
      variant_resolutions.append("1280x720")
      bitrates = self.calculate_bitrate_variants(bitrate, base_bitrates['720'])
      variant_bitrates.append(bitrates)

    if(height >= 1080): # 1080
      variant_resolutions.append("1920x1080")
      bitrates = \
          self.calculate_bitrate_variants(bitrate, base_bitrates['1080'])
      variant_bitrates.append(bitrates)

    if(height >= 2160): # 4K
      variant_resolutions.append("3840x2160")
      bitrates = \
          self.calculate_bitrate_variants(bitrate, base_bitrates['2160'])
      variant_bitrates.append(bitrates)

    return variant_resolutions, variant_bitrates

