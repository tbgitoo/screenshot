#!/usr/bin/python3
from itertools import chain
from datetime import datetime
from time import time
from subprocess import getstatusoutput
from typing import List, Iterable, Iterator
from os import chdir
from os import mkdir
from os import getcwd
from os import stat
from os import rmdir
from os import scandir
from os import remove
from PIL import Image

import click

from .get_window_id import gen_window_ids, WINDOW_OPTIONS, USER_OPTS_STR

FILE_EXT = '.png'
COMMAND = 'screencapture {options} -l {window} "{filename}"'
STATUS_OK = 0
STATUS_FAIL = 1

IMG_TYPES = 'png', 'pdf', 'jpg', 'tiff'


class ScreencaptureEx(Exception):
    pass


def take_screenshot(window: int, filename: str, options: List[str] = None) -> str:
    if options is None:
        options = []

    for option in options:
        if '-t' in option and not any(img_type in option.lower()
                                      for img_type in IMG_TYPES):
                raise ScreencaptureEx(f"Bad option {option}. File type unknown.")

    options = ' '.join(options)

    rc, output = getstatusoutput(COMMAND.format(window=window, filename=filename, options=options))


    if rc != STATUS_OK:
        raise ScreencaptureEx(f"Error: screencapture output: {output}")

    return filename


def get_filename(*args) -> str:
    return ' '.join(map(str, args + (datetime.now(),))) + FILE_EXT


def gen_windows(application_name: str, title: str, window_selection_options: str) -> Iterator[int]:
    windows = gen_window_ids(application_name, title, window_selection_options)

    try:
        yield next(windows)

    except StopIteration as e:
        raise ScreencaptureEx(f"Window with parent {application_name} and title {title} not found.") from e

    yield from windows


def screenshot_windows(application_name: str,
                       title: str = '',
                       window_selection_options: str = '',
                       options: List[str] = None) -> Iterator[str]:
    windows = gen_windows(application_name, title, window_selection_options)

    for window in windows:
        yield take_screenshot(window, get_filename(application_name, title), options)


def screenshot_window(application_name: str,
                      title: str = '',
                      filename: str = '',
                      window_selection_options: str = '',
                      options: List[str] = None) -> str:
    windows = gen_windows(application_name, title, window_selection_options)
    window = next(windows)
    filename = filename if filename else get_filename(application_name, title)
    return take_screenshot(window, filename, options)

def get_temp_directory():
    current_dir = getcwd()
    chdir("/tmp")
    dir_exists=True
    dirname_root="screenshot_"
    index=0
    dirname = dirname_root + str(index)
    while dir_exists:
        index=index+1
        dirname = dirname_root + str(index)
        try:
                stat(dirname)
        except FileNotFoundError as e:
            dir_exists=False
    mkdir(dirname)
    chdir(current_dir)
    return "/tmp/"+dirname







@click.command()
@click.option('-w', '--window_selection_options', default=USER_OPTS_STR,
              help="Options: " + ', '.join(WINDOW_OPTIONS) + '\nDefault: ' + USER_OPTS_STR)
@click.option('-t', '--title', default='', help="Title of window from APPLICATION_NAME to capture.")
@click.option('-f', '--filename', default=None, help="Filename to save the captured PNG as.")
@click.option('-a', '--all_windows', is_flag=True, default=False, help="Capture all windows matching parameters.")
@click.option('-o', '--output', default='png',
              help="Image format to create, default is png (other options include pdf, jpg, tiff)")
@click.option('-s', '--shadow', is_flag=True, help="Capture the shadow of the window.")
@click.option('-V', '--Video', default='0',
              help="Take images for a video (series of images), for a time indicated in seconds")
@click.argument('application_name')
def run(application_name: str,
        title: str,
        filename: str,
        window_selection_options: str,
        output: str,
        shadow: bool,
        video: str,
        all_windows: bool):
    options = []

    if output:
        options.append(f'-t {output}')

    if not shadow:
        options.append('-o')

    try:
        if all_windows:
            if filename:
                print(f'Taking screenshots of all windows beloning to {application_name}, filename option ignored.')

            for filename in screenshot_windows(application_name, title, window_selection_options):
                print(filename)

        else:
            if int(video)<=0:
                print(screenshot_window(application_name, title, filename, window_selection_options, options))
            else:
                current_dir=getcwd()
                temp_dir=get_temp_directory()
                chdir(temp_dir)
                timenow=time()
                fname=0
                while time()<timenow+int(video):
                    fileNameExtended=str(fname)
                    if fname<10:
                        fileNameExtended="0"+fileNameExtended
                    if fname<100:
                        fileNameExtended = "0"+fileNameExtended
                    if fname<1000:
                        fileNameExtended = "0"+fileNameExtended
                    print(screenshot_window(application_name, title, fileNameExtended+".png", window_selection_options, options))
                    fname=fname+1
                length_s=time()-timenow
                frame_rate=fname/length_s
                print("Frame rate: ",frame_rate," frames per second\n")
                im = Image.open(temp_dir+"/0000.png")
                print(im.size)
                ffmpeg_command="ffmpeg -y -r "+str(frame_rate)+ " -i %04d.png "
                ffmpeg_command=ffmpeg_command+" -vf scale=2484:952 -vf fps=24 "+current_dir+"/0.mpg"
                print("ffmpg command:\n",ffmpeg_command)
                rc, output = getstatusoutput(ffmpeg_command)


                if rc != STATUS_OK:
                    raise ScreencaptureEx(f"Error: screencapture output: {output}")

                if temp_dir:
                    chdir(temp_dir)
                    si = scandir()
                    for theFile in si:
                        if theFile.is_file():
                            remove(theFile.name)
                    chdir(current_dir)
                    rmdir(temp_dir)


        exit(STATUS_OK)

    except ScreencaptureEx as e:
        print('Error:', e)
        exit(STATUS_FAIL)


if __name__ == "__main__":
    screenshot_window()
