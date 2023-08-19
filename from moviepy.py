import numpy as np
import moviepy.editor as mpe
from tqdm import tqdm
import matplotlib.pyplot as plt

# Load video
video_path = r"C:\Users\RTX\Videos\2023-07-20 15-59-52.mp4"
video = mpe.VideoFileClip(video_path)
audio = video.audio

# Normalize audio to 0 dB
normalized_audio = audio.volumex(1 / audio.max_volume())

# Convert to mono and get volume
fps = audio.fps  # Get fps from audio
mono_audio = normalized_audio.to_soundarray(fps=fps, nbytes=2)
volume = np.sqrt(((mono_audio ** 2).mean(axis=1)))

# Parameters
volume_threshold = 0.01  # Change this based on your requirement
duration_threshold = 60  # in seconds

# Initialize list to hold non-silent clips
silent_clips = []

# Find start and end times of non-silent parts longer than the duration threshold
start_time = None
for i in tqdm(range(len(volume)), desc='Processing video'):
    if volume[i] <= volume_threshold and start_time is None:
        start_time = i / fps
    elif volume[i] > volume_threshold and start_time is not None:
        end_time = i / fps
        # Only add the clip if the duration is longer than the duration threshold
        if end_time - start_time > duration_threshold:
            silent_clips.append(video.subclip(start_time, end_time))
        start_time = None

# If there are silent clips, concatenate them and write the output
if silent_clips:
    final_clip = mpe.concatenate_videoclips(silent_clips)
    final_clip.write_videofile("output.mp4")
else:
    print("No silent parts longer than one minute were found")

# Plot volume
time = np.array([i / fps for i in range(len(volume))])
plt.figure(figsize=(12, 4))
plt.plot(time, volume, label="Volume")
plt.legend()
plt.show()
