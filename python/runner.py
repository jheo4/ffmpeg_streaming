import sys
import argparse
import os
from pathlib import Path
from pyas.transcoder import Transcoder
from pyas.variant_generator import VariantGenerator

transcoder = Transcoder.get_instance()
variant_generator = VariantGenerator.get_instance()

home = Path(os.environ['REPO_HOME'])
output_dir = Path(str(home) + '/output')
output_dir.mkdir(parents=True, exist_ok=True)

parser = argparse.ArgumentParser();
# TODO: URL input / Input Stream (pipe)
parser.add_argument('--input', required=True,
                    help='an input (a local video or a stream)')
parser.add_argument('--codec', default='libx264', required=False,
                    help="supported codec: libx264 libx265.....")
parser.add_argument('--container', default='mp4', required=False,
                    help="supported container: mp4.....")
parser.add_argument('--gpu', default=False, required=False,
                    help='True/False to use GPU')
parser.add_argument('--output', required=True, help='the output mpd file name')


if __name__ == "__main__":
  args = parser.parse_args()
  args.input = Path(args.input).resolve()
  args.output = Path(args.output).resolve()
  args.gpu = int(args.gpu)
  res, brs = variant_generator.get_dash_variant_list(args.input);

  if args.gpu == False:
    exe_time = transcoder.sw_generate_mpd(input=args.input, codec=args.codec,
                                          container='dash', brs=brs, buf='16M',
                                          res=res, output=args.output)
  else:
    exe_time = transcoder.gpu_generate_mpd(input=args.input, codec=args.codec,
                                  container=args.container, brs=brs, buf='16M',
                                  res=res, output=args.output)

  print("transcoding + mpd generation time: ", exe_time)

