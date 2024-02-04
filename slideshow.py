#!/usr/bin/env python3

# Copyright (C) 2023 by Jasonm23 / ocodo
# Licenced under GPL v3 see LICENSE
# See README.md for more info

import os
import sys
import random
import pyglet
import pyperclip

SLIDESHOW_EXTENSION = '.slideshow'
IMAGE_EXTENSIONS = ('jpg', 'jpeg', 'png', 'gif', 'bmp', 'dds', 'exif', 'jp2', 'jpx', 'pcx', 'pnm', 'ras', 'tga', 'tif', 'tiff', 'xbm', 'xpm')

help_osd = """
Slideshow Controls (v2.0)

Keyboard:
SPACE - Pause/resume                   /   - Show this page
Q     - Quit (also Esc)                k   - Ken Burns effect toggle
[,]   - Change image delay time        i   - Copy filename to clipboard
1-9   - Change image delay time        o,n - Oldest/newest order
f     - Maximize window                a,z - Alphabetical/reverse order
r     - Random/selection order toggle  ← → - Prev/next image

Mouse:
Left Click left or right side - Prev/next image
Right click window 3rds - Toggle Random // Toggle Pause // Toggle Ken Burns
Scroll - Zoom
"""

help_usage = f"""
Slideshow will look for valid image filenames in stdin,
or from a directory and display them.

Usage:
    slideshow [filename.slideshow]
or
    slideshow [directory]
or
    slideshow < list_of_filenames_via_stdin
or
    image_filenames_pipe_source | slideshow

Keyboard Controls:
  Esc,q - quit
  [, ] - change image delay time
  1-9 - change image delay time (number to seconds)
  f - maximize window/reset image zoom/panning (fullscreen)
  r - random toggle
  k - Ken Burns effect toggle
  i - Copy image filename to clipboard
  SPACE - pause/resume
  left, right - move between images

Mouse Controls:
  Scroll - zoom in/out
  Drag - pan
  Left click - move between images (click on left or right side)
  Right click
    left side (1/3) - random/ordered
    middle (1/3) - pause/resume
    right side (1/3) - Ken Burns effect toggle

Slideshow recognizes these image file extensions:

{IMAGE_EXTENSIONS}

"""

class ShadowLabel:
    def __init__(self, text, x, y, font_name='Arial', font_size=14,
                 opacity=255, color=(255,255,255,255), shadow_color=(0,0,0,127),
                 offset_x=2, offset_y=-2,
                 anchor_x='center', anchor_y='center',
                 multiline=False, width=None):
        self._x = x
        self._offset_x = offset_x
        self._y = y
        self._offset_y = offset_y
        self._opacity = opacity
        self._text = text
        self.main_label = pyglet.text.Label(
            self._text,
            font_name=font_name,
            font_size=font_size,
            x=self._x,
            y=self._y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = color,
            multiline = multiline,
            width = width
        )
        self.shadow_label = pyglet.text.Label(
            self._text,
            font_name = font_name,
            font_size = font_size,
            x = self._x + self._offset_x,
            y = self._x + self._offset_y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color=shadow_color,
            multiline = multiline,
            width = width
        )

    def show(self, message):
        self.text = message
        self.opacity = 255

    def hide(self):
        self.opacity = 0

    @property
    def opacity(self):
        return self._opacity

    @opacity.setter
    def opacity(self, value):
        self._opacity = value
        self.main_label.opacity = value
        self.shadow_label.opacity = value

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = value
        self.main_label.text = value
        self.shadow_label.text = value

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        self._x = value
        self.main_label.x = value
        self.shadow_label.x = self._offset_x + value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.main_label.y = value
        self.shadow_label.y = self._offset_y + value

    def draw(self):
        self.shadow_label.draw()
        self.main_label.draw()

image_paths = []
saved_image_paths = []

image_filename = ""
image_index = 0
img = None
slide = None
status_label = None
status_label_small = None

osd_banner_delay = 5
status_label_hide_delay = 1
update_interval_seconds = 6.0
mouse_hide_delay = 1

pan_speed_slowest = 20
pan_speed_fastest = 40
pan_speed_alt_axis = 3
pan_speed_x = 10
pan_speed_y = 10
zoom_speed = 0
progress = 0
progress_bar_height = 2

ken_burns = True
paused = False
random_image = False
drag_pan = False # on during pan and off at the next mouse

window = pyglet.window.Window(resizable=True,style='borderless')

def osd_banner(message, delay=osd_banner_delay):
    pyglet.clock.unschedule(hide_osd_banner)

    banner_label.x = window.width // 2
    banner_label.y = window.height // 2
    banner_label.show(message)

    pyglet.clock.schedule_once(hide_osd_banner, delay)

def osd(message, delay=status_label_hide_delay):
    pyglet.clock.unschedule(hide_status_message)
    status_label.show(message)
    pyglet.clock.schedule_once(hide_status_message, delay)

def osd_small(message, delay=status_label_hide_delay):
    pyglet.clock.unschedule(hide_small_status_message)
    status_label_small.x = window.width - 10
    status_label_small.show(message)
    pyglet.clock.schedule_once(hide_small_status_message, delay)

def is_gif_animation(image):
    return isinstance(image, pyglet.image.Animation)

def hide_small_status_message(dt):
    status_label_small.hide()

def hide_status_message(dt):
    status_label.hide()

def hide_osd_banner(dt):
    banner_label.hide()

def coin_toss():
    return random.randint(0,100) > 50

def randomize_pan_zoom_speeds(image):
    global pan_speed_x, pan_speed_y, zoom_speed
    width, height = get_width_height(image)
    if is_landscape(width, height):
        pan_speed_x = random.randint(pan_speed_slowest, pan_speed_fastest) * (height/width)
        pan_speed_y = random.randint(-pan_speed_alt_axis, pan_speed_alt_axis) * (height/width)
        if coin_toss():
            pan_speed_x = -pan_speed_x
    else:
        pan_speed_y = random.randint(pan_speed_slowest, pan_speed_fastest) * (width/height)
        pan_speed_x = random.randint(-3, 3) * (width/height)
        if coin_toss():
            pan_speed_y = -pan_speed_y

    zoom_speed = random.uniform(-0.01,-0.001)

def update_pan(dt):
    if ken_burns:
        slide.x += dt * pan_speed_x
        slide.y += dt * pan_speed_y

def update_zoom(dt):
    if ken_burns:
        slide.scale -= dt * zoom_speed

def load_image(filename):
    if filename.endswith('gif'):
        return pyglet.image.load_animation(filename)
    else:
        return pyglet.image.load(filename)

def center_slide():
    slide.x = (window.width - slide.width) / 2
    slide.y = (window.height - slide.height) / 2

def setup_slide():
    width, height = get_width_height(img)
    if ken_burns:
        randomize_pan_zoom_speeds(img)
        slide.scale = get_oversize_scale(window, img)
        if is_landscape(width, height):
            slide.y = (window.height - slide.height) / 2
            if pan_speed_x > 0:
                slide.x = window.width - slide.width
            else:
                slide.x = 0
        else:
            slide.x = (window.width - slide.width) / 2
            if pan_speed_y > 0:
                slide.y = window.height - slide.height
            else:
                slide.y = 0

    else:
        slide.scale = get_fit_scale(window, img)
        slide.x = (window.width - slide.width) / 2
        slide.y = (window.height - slide.height) / 2

def nav_next():
    if len(image_paths) > 0:
        if not paused:
            pause()
            update_image(0)
            resume()
        else:
            update_image(0)

def nav_prevous():
    if len(image_paths) > 0:
        if not paused:
            pause()
            previous_image()
            resume()
        else:
            previous_image()

def previous_image():
    global random_image, image_index, image_filename, img
    if image_index > 0:
        image_index -= 1
    else:
        image_index = len(image_paths) - 1

    reset_clock(False)
    image_filename = image_paths[image_index]
    img = load_image(image_filename)
    slide.image = img

    setup_slide()

    window.clear()

def next_image():
    global image_index, image_filename, img

    if image_index < len(image_paths) - 1:
        image_index += 1
    else:
        image_index = 0

    image_filename = image_paths[image_index]
    img = load_image(image_filename)
    return img

def update_image(dt):
    global img
    img = next_image()
    slide.image = img
    reset_clock(False)
    setup_slide()

    window.clear()

def hide_mouse(dt):
    window.set_mouse_visible(visible=False)
    hide_progress_bar()

def hide_progress_bar():
    progress_bar.opacity = 0
    background_bar.opacity = 0

def show_progress_bar():
    progress_bar.opacity = 255
    background_bar.width = window.width
    background_bar.opacity = 255

def get_valid_image_path(base_dir, input_path):
    # Check if the path is an absolute path
    if os.path.isabs(input_path):
        return input_path

    # If not, treat it as a relative path to the containing file location
    return os.path.abspath(os.path.join(base_dir, input_path))

def get_image_paths(input_list):
    paths = []
    for f in input_list:
        f = f.rstrip()
        if f.endswith(SLIDESHOW_EXTENSION):
            paths.extend(get_image_paths_from_file(f))
        elif f.endswith(IMAGE_EXTENSIONS):
            path = os.path.abspath(f)
            paths.append(path)

    return paths

def get_image_paths_from_directory(input_dir='.'):
    file_list = os.listdir(input_dir)
    file_paths = [os.path.join(input_dir, f) for f in file_list]
    return get_image_paths(file_paths)

def get_image_paths_from_stdin():
    file_list = sys.stdin.readlines()
    base_dir = os.getcwd()  # Get the current working directory

    # Validate and convert paths to full paths if necessary
    image_paths = [get_valid_image_path(base_dir, path.strip()) for path in file_list]

    return get_image_paths(image_paths)

def get_image_paths_from_file(file_path):
    with open(file_path, 'r') as file:
        file_list = file.readlines()

    base_dir = os.path.dirname(file_path)  # Get the directory containing the file

    # Validate and convert paths to full paths if necessary
    image_paths = [get_valid_image_path(base_dir, path.strip()) for path in file_list]

    return get_image_paths(image_paths)

def sort_image_paths_by_date_created(reverse=False):
    global image_index, image_paths
    image_paths.sort(key=lambda x: os.path.getctime(x), reverse=reverse)
    image_index = image_paths.index(image_filename)

def sort_image_paths_by_alpha(reverse=False):
    global image_index, image_paths
    image_paths.sort(key=str.lower, reverse=reverse)
    image_index = image_paths.index(image_filename)
    
def goto_start():
    global image_index, image_filename, img
    image_index = -1
    nav_next()

def is_landscape(width, height):
    return width > height

def is_larger(width, height, window):
    return width > window.width and height > window.height

def get_oversize_scale(window, image):
    scale = get_fit_scale(window, image)
    return scale * 1.2

def get_width_height(image):
    if is_gif_animation(image):
        return (image.get_max_width(), image.get_max_height())
    else:
        return (image.width, image.height)

def get_fit_scale(window, image):
    image_width, image_height = get_width_height(image)

    if is_landscape(image_width, image_height):
        if is_larger(image_width, image_height, window):
            scale = window.height / image_height
        else:
            scale = window.width / image_width
        if (image_height * scale) > window.height:
            scale = window.height / image_height
    else:
        scale = window.height / image_height
        if (image_width * scale) > window.width:
            scale = window.width / image_width

    return scale

def reset_clock(show_message=True):
    if show_message:
        osd(f"Interval: {update_interval_seconds:.2f}")

    if not paused:
        pyglet.clock.unschedule(update_image)
        pyglet.clock.schedule_interval(update_image, update_interval_seconds)

def pause(osd_message=False):
    if osd_message:
        osd("Paused")
    pyglet.clock.unschedule(update_image)

def resume(osd_message=False):
    if osd_message:
        osd("Resume")
    pyglet.clock.schedule_interval(update_image, update_interval_seconds)

def toggle_ken_burns():
    global ken_burns
    ken_burns = not ken_burns
    if ken_burns:
        osd(f"Ken Burns Effect: On")
    else:
        osd(f"Ken Burns Effect: Off")

def toggle_pause():
    global paused
    paused = not paused
    if paused:
        pause(True)
    else:
        resume(True)

def toggle_random_image():
    global random_image, image_paths, image_index
    random_image = not random_image
    if random_image:
        random.shuffle(image_paths)  # Shuffle the original list for random mode
        image_index = 0  # Reset image index to start from the beginning
        osd(f"Random")
    else:
        image_paths = saved_image_paths.copy()  # Use sequential list
        image_index = saved_image_paths.index(image_filename)  # Restore the original index
        osd(f"Sequence")

def resize_window_to_screen():
    screen = window.display.get_default_screen()
    width = screen.width
    height = screen.height

    window.set_location(0,0)
    window.width = width
    window.height = height

def progress_bar_draw():
    progress_bar.width = window.width * ((image_index + 1) / len(image_paths))
    background_bar.draw()
    progress_bar.draw()

def draw_rect(x, y, width, height, stroke_width=2, color=(0,0,0)):
    pyglet.shapes.Line(x, y, x + width, y, width=stroke_width, color=color).draw()
    pyglet.shapes.Line(x + width, y, x + width, y + height, width=stroke_width, color=color).draw()
    pyglet.shapes.Line(x + width, y + height, x, y + height, width=stroke_width, color=color).draw()
    pyglet.shapes.Line(x, y + height, x, y, width=stroke_width, color=color).draw()

@window.event
def on_draw():
    window.clear()
    slide.draw()
    draw_rect(slide.x, slide.y, slide.width, slide.height)

    status_label.draw()
    status_label_small.draw()
    banner_label.draw()

    if len(image_paths) > 0:
        progress_bar_draw()

@window.event
def on_key_release(symbol, modifiers):
    global update_interval_seconds
    key = pyglet.window.key

    if key.Q == symbol or key.ESCAPE == symbol:
        window.close()
        sys.exit()

    elif key.SPACE == symbol:
        toggle_pause()

    elif key.R == symbol:
        toggle_random_image()

    elif key.F == symbol:
        resize_window_to_screen()

    elif key.K == symbol:
        toggle_ken_burns()

    elif key.I == symbol:
        osd(f"{image_filename} [to clipboard]")
        pyperclip.copy(image_filename)

    elif key.LEFT == symbol:
        nav_prevous()

    elif key.RIGHT == symbol:
        nav_next()
        
    elif key.S == symbol:
        goto_start()

    elif key.O == symbol:
        osd("Sort created asc")
        sort_image_paths_by_date_created(reverse=False)

    elif key.N == symbol:
        osd("Sort created desc")
        sort_image_paths_by_date_created(reverse=True)

    elif key.A == symbol:
        osd("sort alpha asc")
        sort_image_paths_by_alpha(reverse=False)

    elif key.Z == symbol:
        osd("sort alpha desc")
        sort_image_paths_by_alpha(reverse=True)

    elif key.SLASH == symbol:
        osd_banner(help_osd)

    elif key.BRACKETLEFT == symbol:
        update_interval_seconds = max(update_interval_seconds - 0.5, 0.5)
        reset_clock()

    elif key.BRACKETRIGHT == symbol:
        update_interval_seconds = max(update_interval_seconds + 0.5, 0.5)
        reset_clock()

    elif symbol in [key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9]:
        update_interval_seconds = float(symbol - 48) * 2
        reset_clock()

@window.event
def on_mouse_release(x, y, button, modifiers):
    global drag_pan
    if drag_pan:
        drag_pan = False
        return

    width = window.width
    if button == pyglet.window.mouse.LEFT:
        if x < width * 0.5:
            nav_prevous()
        elif x > width * 0.5:
            nav_next()

    elif button == pyglet.window.mouse.RIGHT:
        if x < width * 0.3:
            toggle_random_image()
        elif x > width * 0.6:
            toggle_ken_burns()
        else:
            toggle_pause()

@window.event
def on_mouse_scroll(x, y, scroll_x, scroll_y):
    global slide

    # Calculate the zoom factor based on scroll direction
    zoom_factor = 0.98 if scroll_y < 0 else 1.01

    # Calculate the new pan coordinates based on the current pan and zoom factor
    new_pan_x = slide.x + (slide.width / 2) * (1 - zoom_factor)
    new_pan_y = slide.y + (slide.height / 2) * (1 - zoom_factor)

    # Update the pan coordinates
    slide.x = new_pan_x
    slide.y = new_pan_y

    # Apply the zoom factor to the image
    slide.scale *= zoom_factor

    # Redraw the image
    window.clear()

@window.event
def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
    global slide, drag_pan
    slide.x += dx
    slide.y += dy
    drag_pan = True

    # Redraw the image
    window.clear()

@window.event
def on_mouse_motion(x, y, dx, dy):
    window.set_mouse_visible(visible=True)
    show_progress_bar()
    pyglet.clock.unschedule(hide_mouse)
    pyglet.clock.schedule_once(hide_mouse, mouse_hide_delay)

@window.event
def on_resize(width,height):
    setup_slide()

if __name__ == '__main__':
    try:
        args_dir = None
        if len(sys.argv) > 1:
            args_dir = sys.argv[1]


        if args_dir and args_dir == '-h' or args_dir == '--help;':
            print(help_usage, file=sys.stderr)
            sys.exit(0)


        if args_dir:
            if os.path.isdir(args_dir):
                image_paths = get_image_paths_from_directory(args_dir)
            elif os.path.isfile(args_dir):
                image_paths = get_image_paths_from_file(args_dir)
        else:
            image_paths = get_image_paths_from_stdin()

        if len(image_paths) < 1:
          print(f"No images found in source", file=sys.stderr)
          sys.exit(1)
        else:
          saved_image_paths = image_paths.copy()
          image_filename = image_paths[image_index]
          img = load_image(image_filename)

          slide = pyglet.sprite.Sprite(img)

          background_bar = pyglet.shapes.Rectangle(0, 0, window.width, progress_bar_height, color=(50,50,50))
          progress_bar = pyglet.shapes.Rectangle(0, 0, 0, progress_bar_height, color=(255, 255, 255))
          hide_progress_bar()

          status_label = ShadowLabel(
              '',
              x=10,
              y=10,
              anchor_x='left',
              anchor_y='bottom'
          )

          status_label_small = ShadowLabel(
              '',
              x=10,
              y=10,
              anchor_x='right',
              anchor_y='bottom',
              font_size=12
          )

          banner_label = ShadowLabel(
              "",
              10,
              10,
              anchor_x='center',
              anchor_y='center',
              font_size=15,
              font_name="Monaco",
              width=window.width,
              multiline=True
          )

          setup_slide()

          pyglet.clock.schedule_interval(update_image, update_interval_seconds)
          pyglet.clock.schedule_interval(update_pan, 1/60.0)
          pyglet.clock.schedule_interval(update_zoom, 1/60.0)
          pyglet.clock.schedule_once(hide_mouse, mouse_hide_delay)

          pyglet.app.run()

    except Exception as e:
        print("There was an error")
        print(e)

        sys.exit()
