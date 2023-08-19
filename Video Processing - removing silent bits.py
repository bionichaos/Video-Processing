import os
import soundfile as sf
import numpy as np
from moviepy.editor import VideoFileClip
import librosa
# from tqdm.notebook import tqdm
from tqdm import tqdm

# Define the folder where the video is located
# folder_path = "C:\\Users\\RTX\\Videos"

# Specify the video file name
# video_file_name = "2023-07-20 15-59-52.mp4"
video_file_name = "2023-08-10 16-10-24.mp4"

# Construct the full path to the video file
video_path = os.path.join(folder_path, video_file_name)

# Extract audio from video and convert to mono
video_clip = VideoFileClip(video_path)  # Process the entire video
sampling_rate = video_clip.audio.fps  # Get the original audio sampling rate
audio = video_clip.audio.to_soundarray(fps=sampling_rate)
audio_mono = np.mean(audio, axis=1)

# Save mono audio to file
audio_file_path = os.path.join(folder_path, 'audio_mono.wav')  # path to save the extracted audio
sf.write(audio_file_path, audio_mono, sampling_rate)

# Define the chunk size (1 second of audio)
chunk_size = 1 * sampling_rate  # 1 second at original sampling rate

# Initialize variables
clip_num = 1  # number of the current clip
start_time = 0  # start time of the current clip
clip_started = False

# Create a new directory for the clips
new_folder_path = os.path.join(folder_path, os.path.splitext(video_file_name)[0])
if not os.path.exists(new_folder_path):
    os.makedirs(new_folder_path)

# Process the audio in chunks
with sf.SoundFile(audio_file_path) as audio_file:
    for i, chunk in enumerate(tqdm(audio_file.blocks(blocksize=chunk_size, dtype='float32'), total=audio_file.frames // chunk_size)):
        volume = np.mean(librosa.feature.rms(y=chunk))
        if volume > 0:  # check if the volume is above the threshold
            if not clip_started:
                start_time = i * chunk_size / sampling_rate  # start time of the current clip
                clip_started = True
        elif clip_started:  # volume is below the threshold and a clip has started
            end_time = i * chunk_size / sampling_rate  # end time of the current clip
            # Extract the clip and write it to a file
            clip = video_clip.subclip(start_time, end_time)
            clip.write_videofile(f"{new_folder_path}/clip_{clip_num}.mp4", audio_codec='aac', audio_bitrate='96k')
            clip_num += 1
            clip_started = False

# Handle the last clip
if clip_started:
    clip = video_clip.subclip(start_time, len(video_clip))
    clip.write_videofile(f"{new_folder_path}/clip_{clip_num}.mp4", audio_codec='aac', audio_bitrate='96k')