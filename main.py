#!/usr/bin/env python3

import subprocess
import time
import random
import json
import requests
import isodate
from datetime import timedelta

VIDEO_PLAY_TIME = 30*60
REST_TIME = 30*60
MAX_DURATION_BUFFER_VALUE = 60

FIRST_HOUR = 9
LAST_HOUR = 22

with open('keys.json') as f:
  keys = json.load(f)
  YOUTUBE_API_KEY = keys['youtube_data_api']

def load_videos(videos_file):
    video_ids = []

    with open(videos_file) as fp:
        line = fp.readline()
        while line:
            line = line.strip()
            if not line.startswith("#") and len(line) > 0:
                video_ids.append(line[32:])
                line = fp.readline()

    return video_ids

def is_good_time_for_video():
    current_time = time.localtime()

    return current_time.tm_hour >= FIRST_HOUR and current_time.tm_hour <= LAST_HOUR

def wake_display():
    subprocess.run(["xset", "dpms", "force", "on"])

def sleep_display():
    subprocess.run(["xset", "dpms", "force", "off"])

def query_video_duration(video_id):
    url = f"https://www.googleapis.com/youtube/v3/videos?id={video_id}&part=contentDetails&key={YOUTUBE_API_KEY}"

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.54 Safari/537.36'}
    r = requests.get(url=url, headers=headers, timeout=5)

    if r.status_code != 200:
        print("Failed to fetch video details")
        return None

    response_json = r.json()
    duration_string = response_json["items"][0]["contentDetails"]["duration"]
    return isodate.parse_duration(duration_string)    

def compute_start_point_in_seconds(duration):
    max_playback_time = timedelta(seconds=VIDEO_PLAY_TIME)
    print(f"Video play time max: {max_playback_time}")
    
    possible_start_time_range = duration - max_playback_time
    possible_start_time_range -= timedelta(seconds=MAX_DURATION_BUFFER_VALUE)
    if possible_start_time_range <= timedelta():
        return 0

    return random.randrange(possible_start_time_range.seconds)

def launch_video(video_id, start_point=0):
    url = f'https://www.youtube.com/embed/{video_id}?autoplay=1&t={start_point}'

    #process = subprocess.Popen(["firefox", f'--kiosk={url}'])

    process = subprocess.Popen([
        "google-chrome",
        #"--use-gl=desktop",
        "--enable-features=VaapiVideoDecoder",
        "--kiosk",
        "--autoplay-policy=no-user-gesture-required",
        url,
    ])

    print(f"Spawned process {process.pid}")
    process.terminate()

def main_loop(video_ids):
    while True:
        if is_good_time_for_video():
            video_id = random.choice(video_ids)
            video_duration = query_video_duration(video_id)
            print(f"Video {video_id} has duration {video_duration}")
            start_point = compute_start_point_in_seconds(video_duration)
            print(f"Will start {video_id} at {start_point}s")
            wake_display()
            launch_video(video_id, start_point)
            time.sleep(VIDEO_PLAY_TIME)
        else:
            print("Too early to watch cat videos")

        sleep_display()
        time.sleep(REST_TIME)

if __name__ == '__main__':
    video_ids = load_videos("videos.dat")
    main_loop(video_ids)
