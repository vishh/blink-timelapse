#!/usr/local/bin/python3
import cv2
from datetime import datetime, timedelta
import logging as log
import os
import pytz
import sys
import time

from astral import Astral
from blinkpy import blinkpy

def now():
 return pytz.timezone('US/Pacific').localize(datetime.now())

def get_sunrise_sunset():
    city = 'San Francisco'
    a = Astral()
    a.solar_depression = 'civil'
    city = a[city]
    sun = city.sun(date=datetime.now(), local=True)
    if now() >= sun['sunset']:
        sun = city.sun(date=datetime.now()+timedelta(days=1), local=True)
    return sun['sunrise'], sun['sunset']

def get_blink_module(username, password):
    blink = blinkpy.Blink(username=username, password=password, refresh_rate=15)
    blink.start()
    return blink

def snap_pictures(path_prefix, blink, sleep_between):
    for name, camera in blink.cameras.items():
        camera.snap_picture()
        blink.refresh()
        ts = now().strftime('%H_%M_%S')
        output_file = "{}/{}.jpg".format(os.path.join(path_prefix, name), ts)
        camera.image_to_file(output_file)
        time.sleep(sleep_between)

def sleep_until_sunrise():
  sunrise, sunset = get_sunrise_sunset()
  while True:
      ts = now()
      if ts > sunrise:
        log.info('Current time is after sunrise')
        return
      time_to_sleep = (sunrise-ts).total_seconds()
      log.info('Sleeping until sunrise for {} seconds'.format(time_to_sleep))
      time.sleep(time_to_sleep)

def create_output_dirs(path_prefix, blink):
    ts = now()
    date = ts.strftime('%Y_%m_%d')
    for name, camera in blink.cameras.items():
        output_path = os.path.join(path_prefix, 'blink', date, name)
        os.makedirs(output_path, exist_ok=True)
    return os.path.join(path_prefix, 'blink', date)

def daytime_timelapse(output_path_prefix, frequency, blink):
  sunrise, sunset = get_sunrise_sunset()
  path_prefix = create_output_dirs(output_path_prefix, blink)
  if now() <= sunrise:
    log.info("Current time {} is before sunrise {}".format(now(), sunrise))
    return path_prefix
  log.info('starting daytime timelapse capture')
  printcounter = 0
  per_camera_sleep = min(frequency/len(blink.cameras), 30)

  while True:
    if now() >= sunset:
        log.info("Stopping daytime timelapse capture as current time is {} and sunset is {}".format(now(), sunset))
        break
    snap_pictures(path_prefix, blink, per_camera_sleep)
    printcounter += 1
    if (printcounter%1000) == 0:
      log.info("Taking pictures")
    time.sleep(per_camera_sleep)
  return path_prefix

def create_timelapse_video(output_path_prefix, blink):
    for name, _ in blink.cameras.items():
        process_images(os.path.join(output_path_prefix, name))

def process_images(image_dir):
    video_file_name = "{}.mp4".format(os.path.basename(image_dir))
    video_file_path = os.path.join(image_dir, "../", video_file_name)
    log.info('Storing images under {} at {}'.format(image_dir, video_file_path))

    images = [img for img in os.listdir(image_dir) if img.endswith(".jpg")]
    images = sorted(images)
    if len(images) == 0:
        log.info('No images found while attempting to convert images to a timelapse video')
        return
    frame = cv2.imread(os.path.join(image_dir, images[0]))
    height, width, layers = frame.shape
    fourcc = cv2.VideoWriter_fourcc('a','v','c','1')
    video = cv2.VideoWriter(video_file_path, fourcc, 12, (width,height))

    for image in images:
        video.write(cv2.imread(os.path.join(image_dir, image)))

    cv2.destroyAllWindows()
    video.release()

def get_input_args():
    username = os.environ['USERNAME']
    password = os.environ['PASSWORD']
    frequency = int(os.environ['FREQ_SECONDS'])
    output_dir = os.environ['OUTPUT_PATH']
    if username == "":
        log.error('Set USERNAME environment variable')
        return []
    if password == "":
        log.error('Set PASSWORD environment variable')
        return []
    if frequency <= 0:
        frequency = 30
        log.error('Seting capture frequency to 30 seconds')
    if output_dir == "":
        log.error('Set OUTPUT_DIR environment variable')
        return []
    return [username, password, frequency, output_dir]

def main():
    log.basicConfig(format='%(asctime)s - %(message)s', level=log.INFO)
    inputs = get_input_args()
    if len(inputs) != 4:
        sys.exit(-1)

    blink = get_blink_module(inputs[0], inputs[1])
     # In an infinite for loop
     # sleep until it's sunrise
     # take pictures until sunset
     # process the pictures
     # go back to sleeping
    while True:
        output_path_prefix = daytime_timelapse(inputs[3], inputs[2], blink)
        create_timelapse_video(output_path_prefix, blink)
        sleep_until_sunrise()

if __name__ == "__main__":
  main()
