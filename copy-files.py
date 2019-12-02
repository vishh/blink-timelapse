import os
import shutil
import logging as log

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_string('src_dir', '', 'Source Directory')
flags.DEFINE_string('dst_dir', '', 'Destination Directory')
flags.DEFINE_string('ext', '.mp4', 'File extensions to copy')

def absoluteFilePaths(directory, extension):
   for dirpath,_,filenames in os.walk(directory):
       for f in filenames:
           if f.endswith(extension):
               yield os.path.abspath(os.path.join(dirpath, f))

def main(argv):
    log.basicConfig(format='%(asctime)s - %(message)s', level=log.INFO)
    if FLAGS.src_dir == "":
        log.error("source directory not specified")
        return
    if FLAGS.dst_dir == "":
        log.error("destination directory not specified")
        return
    files = absoluteFilePaths(FLAGS.src_dir, FLAGS.ext)
    for f in files:
        dir = os.path.basename(os.path.dirname(f))
        dst_file = os.path.join(FLAGS.dst_dir, dir, os.path.basename(f))
        if os.path.exists(dst_file) and os.path.getmtime(dst_file) == os.path.getmtime(f):
            continue
        os.makedirs(os.path.dirname(dst_file), exist_ok=True)
        shutil.copyfile(f, dst_file)

if __name__ == "__main__":
  app.run(main)
