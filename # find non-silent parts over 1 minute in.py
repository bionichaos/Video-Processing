# find non-silent parts over 1 minute in a mp4 video file 
# and exports the timestamps to davinci resolve

import os
from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from moviepy.editor import VideoFileClip
from tqdm import tqdm
import time

# Extract audio from video
def extract_audio(video_path, audio_path):
    video = VideoFileClip(video_path)
    duration = video.duration
    pbar = tqdm(total=duration)
    for t in range(int(duration)):
        pbar.update()
        time.sleep(1)  # assuming each second of video takes about 1 second to process
    pbar.close()
    video.audio.write_audiofile(audio_path)

# Detect non-silent parts
def detect_non_silent(audio_path, min_silence_len=1000, silence_thresh=-50):
    audio = AudioSegment.from_file(audio_path, format="wav")
    duration = len(audio) / 1000.0 # convert to seconds  
    pbar = tqdm(total=duration) # create progress bar  
    non_silent_parts = detect_nonsilent(audio, min_silence_len=min_silence_len, silence_thresh=silence_thresh)
    for part in non_silent_parts: # iterate over non-silent parts 
        pbar.update((part[1] - part[0]) / 1000.0) # update progress bar 
    pbar.close() # close progress bar  
    return [(start/1000.0, end/1000.0) for start, end in non_silent_parts] # return list of non-silent parts 

# Convert seconds to timecode
def seconds_to_timecode(seconds):
    hours = int(seconds // 3600)
    seconds %= 3600
    minutes = int(seconds // 60)
    seconds %= 60
    frames = int((seconds % 1) * 30)  # convert fractional part of seconds to frames
    seconds = int(seconds)  # remove the fractional part of seconds
    return f"{hours:02}:{minutes:02}:{seconds:02}:{frames:02}"

# Create EDL file
def create_edl_file(non_silent_parts, edl_path):
    with open(edl_path, "w") as f:
        for i, (start, end) in enumerate(non_silent_parts):
            start_tc = seconds_to_timecode(start)
            end_tc = seconds_to_timecode(end)
            f.write(f"{i+1}  AX       V     C        {start_tc} {end_tc} {start_tc} {end_tc}\n")

# Main function
def main(video_path, edl_path):
    audio_path = "temp_audio.wav"
    extract_audio(video_path, audio_path)
    non_silent_parts = detect_non_silent(audio_path)
    create_edl_file(non_silent_parts, edl_path)
    os.remove(audio_path)  # remove temporary audio file

# Usage
# video_path = r"C:\Users\RTX\Videos\Training a hand gesture recognition model.mp4"
# edl_path = r"C:\Users\RTX\Videos\Training a hand gesture recognition model.edl" 

video_path = r"C:\Users\RTX\Videos\2023-07-20 15-59-52.mp4" 
edl_path = r"C:\Users\RTX\Videos\2023-07-20 15-59-52.edl" 

main(video_path, edl_path)
