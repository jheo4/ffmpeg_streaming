# ffmpeg_streaming

## Setup
### FFMPEG with CUDA
1. Install nvidia driver (>= 435.21)
2. Clone & install ffmpeg
```
# clone repo and submodule (ffmpeg)
git clone --recursive https://github.com/jheo4/ffmpeg_streaming.git

# install ffmpeg dependencies
sudo apt-get update -qq && sudo apt-get -y install autoconf automake \
  build-essential cmake git libass-dev libfreetype6-dev libsdl2-dev \
  libtool libva-dev libvdpau-dev libvorbis-dev libxcb1-dev libxcb-shm0-dev \
  libxcb-xfixes0-dev pkg-config texinfo wget zlib1g-dev nasm yasm libx264-dev \
  libx265-dev libnuma-dev libvpx-dev libfdk-aac-dev libmp3lame-dev \
  libopus-dev

# install nv codecs for gpu acceleration
export REPO_HOME=$(pwd)
cd $REPO_HOME/nv-codec-headers && make && sudo make Install

export LD_LIBRARY_PATH=/usr/local/cuda/lib64

export FFMPEG_HOME=$REPO_HOME/FFmpeg
cd FFmpeg && PKG_CONFIG_PATH="$FFMPEG_HOME/ffmpeg_build/lib/pkgconfig" &&
./configure \
  --prefix="$FFMPEG_HOME/ffmpeg_build" \
  --pkg-config-flags="--static" \
  --extra-libs="-lpthread -lm" \
  --bindir="$FFMPEG_HOME/bin" \
  --enable-gpl \
  --enable-libass \
  --enable-libfdk-aac \
  --enable-libfreetype \
  --enable-libmp3lame \
  --enable-libopus \
  --enable-libvorbis \
  --enable-libvpx \
  --enable-libx264 \
  --enable-libx265 \
  --enable-cuda  \
  --enable-cuvid \
  --enable-nvenc \
  --enable-libnpp \
  --extra-cflags=-I/usr/local/cuda/include \
  --extra-ldflags=-L/usr/local/cuda/lib64 \
  --enable-nonfree && \
  make -j4 && \
  make install

export PATH=$FFMPEG_HOME/bin:$PATH
export PYTHONPATH=$FFMPEG_HOME/python
```
