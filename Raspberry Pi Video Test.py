import RPi.GPIO as gp
import os
import time
import subprocess
import time
from picamera2 import Picamera2
from picamera2.encoders import H264Encoder

'''
picam2 = Picamera2(0)    #change to 0 or 1 based on which port the camera is connected to     #for the singular camera, remove comments when ready to use
video_config = picam2.create_video_configuration()
picam2.configure(video_config)

encoder = H264Encoder(10000000)
'''


gp.setwarnings(False)
gp.setmode(gp.BOARD)

gp.setup(7, gp.OUT)
gp.setup(11, gp.OUT)
gp.setup(12, gp.OUT)

camera_configs = [
    {"label": "A", "i2c": "0x04", "gpio": (False, False, True)},
    {"label": "B", "i2c": "0x05", "gpio": (True, False, True)},
    {"label": "C", "i2c": "0x06", "gpio": (False, True, False)},
    {"label": "D", "i2c": "0x07", "gpio": (True, True, False)}
]


loops = 10        #loops is total number of times it runs through camera
duration = 0.4      #duration is amount of time recorded for cameras, -0.3s for switching, always need to be >=0.3
segment_dir = "segments"

def ensure_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)

def switch_camera(config):
    os.system(f"i2cset -y 1 0x70 0x00 {config['i2c']}")
    gp.output(7, config['gpio'][0])
    gp.output(11, config['gpio'][1])
    gp.output(12, config['gpio'][2])

def record_segment(cam_number, loop_num):
    filename = f"{segment_dir}/camera_{cam_number}_part_{loop_num}.h264"
    cmd = f"rpicam-vid --low-latency -t {duration}s -o {filename}"
    os.system(cmd)

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

def main():
    ensure_directory(segment_dir)

    #picam2.start_recording(encoder, '/home/ARC/Desktop/Constant_Camera.h264')

    for loop in range(1, loops + 1):
        for cam_number, config in enumerate(camera_configs, 1):
            print(f"Loop {loop+1} - Recording camera {config['label']}")

            switch_camera(config)
            record_segment(cam_number, loop)

    gp.output(7, False)
    gp.output(11, False)
    gp.output(12, True)

    #picam2.stop_recording()

    for cam_number in range(1,5):
        concatenate_segments(cam_number)


if __name__ == "__main__":
    main()