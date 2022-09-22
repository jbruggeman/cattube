#!/usr/bin/env python3

import subprocess
import time
import random

VIDEO_PLAY_TIME = 60*60
REST_TIME = 60*60

FIRST_HOUR = 9
LAST_HOUR = 22

def load_videos(videos_file):
    video_ids = []

    with open(videos_file) as fp:
        line = fp.readline()
        while line:
            video_ids.append(line[32:].strip())
            line = fp.readline()

    return video_ids

def is_good_time_for_video():
    current_time = time.localtime()

    return current_time.tm_hour >= FIRST_HOUR and current_time.tm_hour <= LAST_HOUR

def wake_display():
    subprocess.run(["xset", "dpms", "force", "on"])

def sleep_display():
    subprocess.run(["xset", "dpms", "force", "off"])

def launch_video(video_id, runtime):
    url = f'https://www.youtube.com/embed/{video_id}?autoplay=1'

    process = subprocess.Popen(["firefox", f'--kiosk={url}'])
    #process = subprocess.Popen(["google-chrome", '--kiosk', url], env={"DISPLAY": ":0"})

    time.sleep(runtime)
    print(f"Spawned process {process.pid}")
    process.kill()

def main_loop(video_ids):
    while True:
        if is_good_time_for_video():
            video = random.choice(video_ids)
            wake_display()
            launch_video(video, VIDEO_PLAY_TIME)
            sleep_display()
        else:
            print("Too early to watch cat videos")

        time.sleep(REST_TIME)

if __name__ == '__main__':
    video_ids = load_videos("videos.dat")
    main_loop(video_ids)
