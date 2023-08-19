from pydub import AudioSegment
from pydub.silence import detect_nonsilent
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import moviepy.editor as mpe
from tqdm import tqdm
import numpy as np
import matplotlib.pyplot as plt
import scipy.io.wavfile

# Load video
video_path = r"C:\Users\RTX\Videos\2023-07-20 15-59-52.mp4"
video = mpe.VideoFileClip(video_path)
audio = video.audio

# Convert audio to .wav format
audio.write_audiofile("temp.wav")
sample_rate, audio_data = scipy.io.wavfile.read("temp.wav")

# Parameters
min_silence_len = 1000
silence_thresh = -40
duration_threshold = 60  # in seconds
sampling_rate = 22000.0 if audio.fps <= 22000.0 else audio.fps

# Find non-silent parts
nonsilent_parts = detect_nonsilent(audio_data, min_silence_len=min_silence_len, silence_thresh=silence_thresh)

# Initialize list to hold non-silent clips and progress bar
non_silent_clips = []
pbar = tqdm(total=len(audio_data), desc='Processing video')

# Find start and end times of non-silent parts longer than the duration threshold
start_time = None
for i in range(len(audio_data)):
    if audio_data[i] > silence_thresh and start_time is None:
        start_time = i / sample_rate
    elif audio_data[i] <= silence_thresh and start_time is not None:
        end_time = i / sample_rate
        # Only add the clip if the duration is longer than the duration threshold
        if end_time - start_time > duration_threshold:
            non_silent_clips.append(video.subclip(start_time, end_time))
        start_time = None
    pbar.update()

# Close progress bar
pbar.close()

# If there are non-silent clips, concatenate them and write the output
if non_silent_clips:
    final_clip = mpe.concatenate_videoclips(non_silent_clips)
    final_clip.write_videofile("output.mp4")
else:
    print("No non-silent parts longer than one minute were found")

# Plot volume
volume = np.array(audio_data ** 2)
time = np.array([i / sampling_rate for i in range(len(volume))])
plt.figure(figsize=(12, 4))
plt.plot(time, volume, label="Volume")
plt.legend()
plt.show()
