import RPi.GPIO as gp
import os
import time
import subprocess
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

loops = 10 # adjust to amount of loops used as necessary
segment_dir = "segments"

def concatenate_segments(cam_number):
    concat_list_path = f"{segment_dir}/cam{cam_number}_concat.txt"
    with open(concat_list_path, 'w') as f:
        for loop in range(1, loops + 1):
            full_path = os.path.abspath(f"{segment_dir}/camera_{cam_number}_part_{loop}.h264")
            f.write(f"file '{full_path}'\n")

    output_file = f"camera_{cam_number}_full.mp4"
    cmd = [
        "ffmpeg",
        "-f", "concat",
        "-safe", "0",
        "-i", concat_list_path,
        "-c", "copy",
        output_file
    ]

    print(f"Concatenating segments for camera {cam_number} into {output_file}")
    subprocess.run(cmd)

for cam_number in range(1,5):
        concatenate_segments(cam_number)