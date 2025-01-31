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

MORNING = 9
END_OF_CRAZY_TIME = 21
BED_TIME = 22

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

    return current_time.tm_hour >= MORNING and current_time.tm_hour <= END_OF_CRAZY_TIME

def is_good_time_for_night_time_video():
    current_time = time.localtime()

    return current_time.tm_hour >= END_OF_CRAZY_TIME and current_time.tm_hour <= BED_TIME

def wake_display():
    subprocess.run(["wlr-randr", "--output", "HDMI-A-1", "--on"])

def sleep_display():
    subprocess.run(["wlr-randr", "--output", "HDMI-A-1", "--off"])

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

def launch_video(video_id, video_duration):
    if video_duration is None:
        start_point = 0
        video_play_time = VIDEO_PLAY_TIME
    else:
        start_point = compute_start_point_in_seconds(video_duration)
        video_play_time = min(VIDEO_PLAY_TIME, video_duration.seconds - MAX_DURATION_BUFFER_VALUE)
        print(f"Will start {video_id} at {start_point}s and play for {video_play_time}s")


    url = f'https://www.youtube.com/embed/{video_id}?autoplay=1&start={start_point}'

    firefox_process_args = [
        "firefox",
        f'--kiosk={url}'
    ]

    chrome_process_args = [
        "google-chrome",
        #"--use-gl=desktop",
        "--enable-features=VaapiVideoDecoder",
        "--kiosk",
        "--autoplay-policy=no-user-gesture-required",
        url,
    ]

    args = firefox_process_args
    #args = chrome_process_args

    printable_args = " ".join(args)
    print(f"Spawning process {printable_args}")

    process = subprocess.Popen(args)
    print(f"Spawned process {process.pid}")

    time.sleep(video_play_time)
    process.terminate()

def play_next_video_loop():
    video_ids = None
    if is_good_time_for_video():
        print("Lets find a good cat video...")
        video_ids = load_videos("videos.dat")
    elif is_good_time_for_night_time_video():
        print("Lets find a good night time cat video...")
        video_ids = load_videos("night_time.dat")
    
    if video_ids is not None:
        video_id = random.choice(video_ids)
        video_duration = query_video_duration(video_id)
        print(f"Video {video_id} has duration {video_duration}")
        wake_display()
        launch_video(video_id, video_duration)
    else:
        print("Too early to watch cat videos")

    sleep_display()
    time.sleep(REST_TIME)

def main_loop():
    while True:
        try:
            play_next_video_loop()
        except BaseException as e:
            print(f"Exception! {e}")
            time.sleep(REST_TIME)

if __name__ == '__main__':
    main_loop()
