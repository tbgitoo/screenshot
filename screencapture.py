from datetime import datetime
from subprocess import getstatusoutput

import click

from get_window_id import gen_window_ids, options, user_options_str, print_window_ids, gen_ids_from_info, \
    get_window_info, summer


def take_screenshot(window: int, filename: str) -> str:
    rc, output = getstatusoutput('screencapture -l %s "%s"' % (window, filename))

    if rc != 0:
        raise Exception("Error in screencapture command %s: %s", (rc, output))

    return filename


def _filename(*args) -> str:
    return '_'.join(map(str, args + (datetime.now(),))) + '.png'


@click.command()
@click.option('-w', '--window_selection_options', default=user_options_str,
              help="Options: " + ' '.join(option for option in options) + '\nDefault: ' + user_options_str)
@click.option('-t', '--title', default=None, help="Title of window from APPLICATION_NAME to capture.")
@click.option('-f', '--filename', default=None, help="Filename to save the captured PNG as.")
@click.option('-a', '--all_windows', is_flag=True, default=False, help="Capture all windows matching parameters")
@click.option('-l', '--list_windows', is_flag=True, default=False, help="List window IDs.")
@click.argument('application_name', default="")
def screenshot_window(application_name: str, title: str='', filename: str='', window_selection_options: str='',
                      all_windows: bool=False, list_windows: bool=False, **kwargs):
    if list_windows:
        print_window_ids(gen_ids_from_info(get_window_info(summer(*window_selection_options.split()))))
        return

    windows = gen_window_ids(application_name, title, window_selection_options)

    try:
        window = next(windows)

    except StopIteration as ex:
        raise ValueError("Window with parent %s and title %s not found." % (application_name, title)) from ex

    if all_windows:
        windows = [window] + list(windows)

        for window in windows:
            filename = _filename(application_name, title)
            print(take_screenshot(window, filename))

    else:
        filename = filename if filename else _filename(application_name, title)
        print(take_screenshot(window, filename))


if __name__ == "__main__":
    screenshot_window()