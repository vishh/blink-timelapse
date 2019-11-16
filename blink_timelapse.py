#!/usr/local/bin/python3
import cv2
from datetime import datetime, timedelta
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
  sun = city.sun(date=datetime.now()+timedelta(days=1), local=True)
  return sun['sunrise'], sun['sunset']

def get_blink_module(username, password):
    blink = blinkpy.Blink(username=username, password=password, refresh_rate=15)
    blink.start()
    return blink

def snap_pictures(path_prefix, blink):
    for name, camera in blink.cameras.items():
        camera.snap_picture()
        blink.refresh()
        ts = now().strftime('%H_%M_%S')
        output_file = "{}/{}.jpg".format(os.path.join(path_prefix, name), ts)
        camera.image_to_file(output_file)
        time.sleep(5)

def sleep_until_sunrise():
  sunrise, sunset = get_sunrise_sunset()
  while True:
      ts = now()
      if ts > sunrise:
        print('Current time is after sunrise')
        return
      time_to_sleep = (sunrise-ts).total_seconds()
      print('Sleeping until sunrise for {} seconds'.format(time_to_sleep))
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
    print("Current time {} is before sunrise {}".format(now(), sunrise))
    #return path_prefix
  print('starting daytime timelapse capture')
  printcounter = 0
  while True:
    if now() >= sunset:
       break
    snap_pictures(path_prefix, blink)
    printcounter += 1
    if (printcounter%1000) == 0:
      print("Taking pictures")
    time.sleep(frequency)
  return path_prefix

def create_timelapse_video(output_path_prefix, blink):
    for name, _ in blink.cameras.items():
        process_images(os.path.join(output_path_prefix, name))

def process_images(image_dir):
    video_file_name = "{}.avi".format(os.path.basename(image_dir))
    video_file_path = os.path.join(image_dir, "../", video_file_name)
    print('Storing images under {} at {}'.format(image_dir, video_file_path))
    images = [img for img in os.listdir(image_dir) if img.endswith(".jpg")]
    frame = cv2.imread(os.path.join(image_dir, images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter(video_file_path, 0, 1, (width,height))

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
  print('Set USERNAME environment variable')
  return []
 if password == "":
  print('Set PASSWORD environment variable')
  return []
 if frequency <= 0:
  print('Set FREQ_SECONDS environment variable')
  return []
 if output_dir == "":
  print('Set OUTPUT_DIR environment variable')
  return []
 return [username, password, frequency, output_dir]

def main():
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