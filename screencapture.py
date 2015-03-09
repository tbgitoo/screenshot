from datetime import datetime
from subprocess import getstatusoutput

import click

from get_window_id import gen_window_ids, options, user_options_str


def take_screenshot(window: int, filename: str):
    rc, output = getstatusoutput('screencapture -l %s %s.png' % (window, filename))

    if rc != 0:
        raise Exception("Error in screencapture command %s: %s", (rc, output))

    else:
        return '%s.png' % filename


def _filename(*args):
    return '_'.join(map(str, args + (datetime.now(),))) + '.png'


@click.command()
@click.option('-t', '--title', default=None, help="Title of window from APPLICATION_NAME to capture.")
@click.option('-f', '--filename', default=None, help="Filename to save the captured PNG as.")
@click.option('-w', '--window_selection_options', default=user_options_str, help="Options: " + ' '.join(option for option in options))
@click.option('-a', '--all', is_flag=True, default=False)
@click.argument('application_name')
def screenshot_window(application_name: str, title: str=None, filename: str=None, window_selection_options: str=None, all: bool=False, **kwargs):
    windows = gen_window_ids(application_name, title, window_selection_options)

    try:
        window = next(windows)

    except StopIteration as ex:
        raise ValueError("Window with parent %s and title %s not found." % (application_name, title)) from ex

    windows = (list(windows) + [window]) if all else [window]

    for window in windows:
        filename = _filename(application_name, title)
        print(take_screenshot(window, filename))


if __name__ == "__main__":
    screenshot_window()