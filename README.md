# add-subtitles

This repo automatically adds subtitles to your video.

#### Requirement

* [insanely-fast-whisper](https://github.com/Vaibhavs10/insanely-fast-whisper):
  
  ````
  pip install insanely-fast-whisper --ignore-requires-python
  ````
  
* [flash-attn](https://github.com/Dao-AILab/flash-attention): 
  
  ```
  pip install flash-attn --no-build-isolation
  ```

You'll also need to install [`ffmpeg`](https://ffmpeg.org/), which is available from most package managers:

```bash
# on Ubuntu or Debian
sudo apt update && sudo apt install ffmpeg

# on MacOS using Homebrew (https://brew.sh/)
brew install ffmpeg

# on Windows using Chocolatey (https://chocolatey.org/)
choco install ffmpeg
```

After setting up environment, simply:

```bash
python trans.py /path/to/video --language=[auto, zh, en]
```

How it looks:

![image-20240805232502529](https://s2.loli.net/2024/08/06/zxlyvSAaXgYRwho.png)
