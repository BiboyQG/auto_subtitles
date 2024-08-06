import os
import ffmpeg
import argparse
import tempfile
import json
import time
from datetime import timedelta


def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("video", nargs="+", type=str,
                        help="paths to video files to transcribe")
    parser.add_argument("--task", type=str, default="transcribe", choices=[
                        "transcribe", "translate"], help="whether to perform X->X speech recognition ('transcribe') or X->English translation ('translate')")
    parser.add_argument("--language", type=str, default="auto", choices=["auto","af","am","ar","as","az","ba","be","bg","bn","bo","br","bs","ca","cs","cy","da","de","el","en","es","et","eu","fa","fi","fo","fr","gl","gu","ha","haw","he","hi","hr","ht","hu","hy","id","is","it","ja","jw","ka","kk","km","kn","ko","la","lb","ln","lo","lt","lv","mg","mi","mk","ml","mn","mr","ms","mt","my","ne","nl","nn","no","oc","pa","pl","ps","pt","ro","ru","sa","sd","si","sk","sl","sn","so","sq","sr","su","sv","sw","ta","te","tg","th","tk","tl","tr","tt","uk","ur","uz","vi","yi","yo","zh"], 
    help="What is the origin language of the video? If unset, it is detected automatically.")

    args = parser.parse_args().__dict__
    language: str = args.pop("language")
    video = args.pop("video")
    audios = get_audio(video)
    audio = list(audios.values())[0]
    os.system(f"insanely-fast-whisper --file-name={audio} --flash True --language={language}")
    output_filename = "output.json"

    with open(output_filename, "r") as f:
        data = f.read()
    
    srt_output = json_to_srt(data)

    with open('output.srt', 'w', encoding='utf-8') as f:
        f.write(srt_output)

    srt_path = "output.srt"
    print("SRT file has been created successfully to -> output.srt!")

    path = video[0]

    out_path = f"{filename(path)}.mp4"

    print(f"Adding subtitles to {filename(path)}...")

    video = ffmpeg.input(path)
    audio = video.audio

    subtitle_style = (
        "Fontname=Noto Sans CJK SC,Fontsize=22,PrimaryColour=&H00FFFFFF,"
        "SecondaryColour=&H000000FF,OutlineColour=&HFF000000,BackColour=&H80000000,"
        "Bold=0,Italic=0,Alignment=2,BorderStyle=4,Outline=4,Shadow=0,MarginL=10,MarginR=10,MarginV=7"
    )

    print("Saving subtitled video...")
    start_time = time.time()

    try:
        ffmpeg.concat(
            video.filter('subtitles', 
                         srt_path, 
                         charenc='UTF-8', 
                         force_style=subtitle_style,
                         ), audio, v=1, a=1
        ).output(
            out_path,
            vcodec='h264_nvenc',
            acodec='aac',
            **{'preset': 'slow', 'crf': '0'}
                 ).run(quiet=True, overwrite_output=True)
    except ffmpeg.Error as e:
        print('stdout:', e.stdout.decode('utf8'))
        print('stderr:', e.stderr.decode('utf8'))
        raise e

    print(f"Finished in {time.time() - start_time:.2f} seconds!")
    print(f"Saved subtitled video to -> {os.path.abspath(out_path)}!")

def format_time(seconds):
    td = timedelta(seconds=seconds)
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    milliseconds = td.microseconds // 1000
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

def json_to_srt(json_data):
    data = json.loads(json_data)
    chunks = data['chunks']
    srt_content = ""

    for i, chunk in enumerate(chunks, 1):
        start_time = format_time(chunk['timestamp'][0])
        end_time = format_time(chunk['timestamp'][1])
        text = chunk['text']

        srt_content += f"{i}\n{start_time} --> {end_time}\n{text}\n\n"

    return srt_content

def filename(path):
    return os.path.splitext(os.path.basename(path))[0]

def get_audio(paths):
    temp_dir = tempfile.gettempdir()

    audio_paths = {}

    for path in paths:
        print(f"Extracting audio from {filename(path)}...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")
        
        try:
            ffmpeg.input(path).output(
                output_path,
                acodec="pcm_s16le", ac=1, ar="16k"
            ).run(quiet=True, overwrite_output=True)
        except ffmpeg.Error as e:
            print('stdout:', e.stdout.decode('utf8'))
            print('stderr:', e.stderr.decode('utf8'))
            raise e

        audio_paths[path] = output_path

    return audio_paths


if __name__ == '__main__':
    main()
