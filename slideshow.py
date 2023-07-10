#!/usr/bin/env python3

# Copyright (C) 2023 by Jasonm23 / ocodo
# Licenced under GPL v3 see LICENSE
# See README.md for more info

help_usage = """
Slideshow will look for valid jpg, jpeg, png & gif image filenames in stdin,
or from a directory and display them.

Usage:
    slideshow [directory]
or
    slideshow < list_of_filenames_via_stdin

Keyboard Controls:
  Esc,q - quit
  [, ] - change image delay time
  1-9 - change image delay time (number to seconds)
  f - maximize window (fullscreen)
  r - random toggle
  k - Ken Burns effect toggle
  i - Copy image filename to clipboard
  SPACE - pause/resume
  left, right - move between images

Mouse Controls:
  Left click - move between images (click on left or right side)
  Right click
    left side (1/3) - random/ordered
    middle (1/3) - pause/resume
    right side (1/3) - Ken Burns effect toggle

"""
import os
import sys
import argparse
import random
import pyglet
import pyperclip

import pyglet

class ShadowLabel:
    def __init__(self, text, x, y, font_name='Arial', font_size=14,
                 opacity=255, color=(255,255,255,255), shadow_color=(0,0,0,127),
                 offset_x=2, offset_y=-2,
                 anchor_x='center', anchor_y='center'):
        self._text = text
        self._x = x
        self._y = y
        self._offset_x = offset_x
        self._offset_y = offset_y
        self._opacity = opacity
        self.main_label = pyglet.text.Label(
            self._text,
            font_name=font_name,
            font_size=font_size,
            x=self._x,
            y=self._y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color = color
        )
        self.shadow_label = pyglet.text.Label(
            self._text,
            font_name = font_name,
            font_size = font_size,
            x = self._x + self._offset_x,
            y = self._x + self._offset_y,
            anchor_x = anchor_x,
            anchor_y = anchor_y,
            color=shadow_color
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
        self.shadow_label.x = value + self._x_offset

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        self._y = value
        self.main_label.y = value
        self.shadow_label.y = value + self._y_offset

    def draw(self):
        self.shadow_label.draw()
        self.main_label.draw()

pan_speed_slowest = 20
pan_speed_fastest = 40
pan_speed_alt_axis = 3
update_interval_seconds = 6.0
progress_bar_height = 2
mouse_hide_delay = 4.0
pan_speed_x = 10
pan_speed_y = 10
zoom_speed = 0
image_paths = []
saved_image_paths = []
image_random_viewed = []
image_index = 0
image_filename = ""
img = None
sprite = None
ken_burns = True
random_image = False
status_label = None
status_label_hide_delay = 2
paused = False
window = pyglet.window.Window(resizable=True,style='borderless')
progress = 0

def osd(message):
    pyglet.clock.unschedule(hide_status_message)
    status_label.show(message)
    pyglet.clock.schedule_once(hide_status_message, status_label_hide_delay)

def osd_small(message):
    pyglet.clock.unschedule(hide_small_status_message)
    status_label_small.x = window.width - 10
    status_label_small.show(message)
    pyglet.clock.schedule_once(hide_small_status_message, status_label_hide_delay)

def is_gif_animation(image):
    return isinstance(image, pyglet.image.Animation)

def hide_small_status_message(dt):
    status_label_small.hide()

def hide_status_message(dt):
    status_label.hide()

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
        sprite.x += dt * pan_speed_x
        sprite.y += dt * pan_speed_y

        # debug panning
        # osd(f"Pan {pan_speed_y > 0 and 'up' or 'down'}:{pan_speed_y:.2f} {pan_speed_x > 0 and 'right' or 'left'}:{pan_speed_x:.2f} [x:{sprite.x:.2f} y:{sprite.y:.2f}]")

def update_zoom(dt):
    if ken_burns:
        sprite.scale -= dt * zoom_speed

def load_image(image):
    if image.endswith('gif'):
        image = pyglet.image.load_animation(image)
    else:
        image = pyglet.image.load(image)
    return image

def setup_sprite():
    width, height = get_width_height(img)
    if ken_burns:
        randomize_pan_zoom_speeds(img)
        sprite.scale = get_oversize_scale(window, img)
        if is_landscape(width, height):
            sprite.y = (window.height - sprite.height) / 2
            if pan_speed_x > 0:
                sprite.x = window.width - sprite.width
            else:
                sprite.x = 0
        else:
            sprite.x = (window.width - sprite.width) / 2
            if pan_speed_y > 0:
                sprite.y = window.height - sprite.height
            else:
                sprite.y = 0

    else:
        sprite.scale = get_fit_scale(window, img)
        sprite.x = (window.width - width) / 2
        sprite.y = (window.height - height) / 2

def get_random_image():
    global image_filename, image_index, random_image, img, image_random_viewed, image_paths

    if len(image_paths) > 0:
        image_filename = random.choice(image_paths)
        image_index = image_paths.index(image_filename)
        image_paths.pop(image_index)
        image_random_viewed.append(image_filename)
        img = load_image(image_filename)
        return img
    else:
        image_paths = saved_image_paths.copy()
        image_random_viewed = []
        return get_random_image()

def nav_next():
    if not paused:
        pause()
        update_image(0)
        resume()
    else:
        update_image(0)

def nav_prevous():
    if not paused:
        pause()
        previous_image()
        resume()
    else:
        previous_image()

def previous_image():
    global random_image, image_index, image_filename, img
    if random_image:
        return
    else:
        if image_index > 0:
            image_index -= 1
        else:
            image_index = len(image_paths) - 1

    image_filename = image_paths[image_index]
    img = load_image(image_filename)
    sprite.image = img

    setup_sprite()

    window.clear()

def next_image():
    global image_index, image_filename, img
    if random_image:
        return get_random_image()
    else:
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
    sprite.image = img

    setup_sprite()

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

def get_image_paths(input_dir='.'):
    paths = []
    for f in os.listdir(input_dir):
        if f.endswith(('jpg', 'jpeg', 'png', 'gif')):
            path = os.path.abspath(os.path.join(input_dir, f))
            paths.append(path)

    paths.sort(key=str.lower)
    return paths

def get_image_paths_from_stdin():
    paths = []
    for f in sys.stdin:
        f = f.rstrip()
        if f.endswith(('bmp', 'dds', 'exif', 'gif', 'jpg', 'jpeg', 'jp2', 'jpx', 'pcx', 'png', 'pnm', 'ras', 'tga', 'tif', 'tiff', 'xbm', 'xpm')):
            paths.append(f)

    return paths

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
    else:
        scale = window.height / image_height

    return scale

def reset_clock():
    osd(f"Interval: {update_interval_seconds:.2f}")
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
    global random_image, image_paths, image_random_viewed
    random_image = not random_image
    image_paths = saved_image_paths.copy()
    image_random_viewed = []
    if random_image:
        osd(f"Random")
    else:
        osd(f"Sequence")

def window_max_size():
    screen = window.display.get_default_screen()
    width = screen.width
    height = screen.height

    window.set_location(0,0)
    window.width = width
    window.height = height

def progress_bar_draw():
    if random_image:
        if len(image_random_viewed) > 0:
            progress_bar.width = window.width * (len(image_random_viewed) / len(saved_image_paths))
        else:
            progress_bar.width = 0
    else:
        progress_bar.width = window.width * ((image_index + 1) / len(image_paths))

    background_bar.draw()
    progress_bar.draw()

@window.event
def on_draw():
    window.clear()
    sprite.draw()

    status_label.draw()
    status_label_small.draw()

    progress_bar_draw()

@window.event
def on_key_release(symbol, modifiers):
    global update_interval_seconds
    key = pyglet.window.key

    if key.Q == symbol or key.ESCAPE == symbol:
        pyglet.app.exit()

    elif key.SPACE == symbol:
        toggle_pause()

    elif key.R == symbol:
        toggle_random_image()

    elif key.F == symbol:
        window_max_size()

    elif key.K == symbol:
        toggle_ken_burns()

    elif key.I == symbol:
        osd(f"Filename copied to clipboard...")
        pyperclip.copy(image_filename)

    elif key.LEFT == symbol:
        nav_prevous()

    elif key.RIGHT == symbol:
        nav_next()

    elif key.BRACKETLEFT == symbol:
        update_interval_seconds = max(update_interval_seconds - 0.5, 0.5)
        reset_clock()

    elif key.BRACKETRIGHT == symbol:
        update_interval_seconds = max(update_interval_seconds + 0.5, 0.5)
        reset_clock()

    elif symbol in [key._1, key._2, key._3, key._4, key._5, key._6, key._7, key._8, key._9]:
        update_interval_seconds = float(symbol - 48)
        reset_clock()

@window.event
def on_mouse_release(x, y, button, modifiers):
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
    global update_interval_seconds
    if scroll_y < 0:
        update_interval_seconds = max(update_interval_seconds + 0.5, 0.5)
    else:
        update_interval_seconds = max(update_interval_seconds - 0.5, 0.5)

    reset_clock()

@window.event
def on_mouse_motion(x, y, dx, dy):
    window.set_mouse_visible(visible=True)
    show_progress_bar()
    pyglet.clock.schedule_once(hide_mouse, mouse_hide_delay)

@window.event
def on_resize(width,height):
    setup_sprite()

if __name__ == '__main__':
    args_dir = None
    if len(sys.argv) > 1:
        args_dir = sys.argv[1]

    if args_dir and args_dir == '-h' or args_dir == '--help;':
        print(help_usage, file=sys.stderr)
        exit(0)

    if args_dir:
        image_paths = get_image_paths(args_dir)
    else:
        image_paths = get_image_paths_from_stdin()

    if len(image_paths) < 1:
      print(f"No images found in source", file=sys.stderr)
      exit(1)
    else:
      saved_image_paths = image_paths.copy()
      image_filename = image_paths[image_index]
      img = load_image(image_filename)
      sprite = pyglet.sprite.Sprite(img)

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
          anchor_x='left',
          anchor_y='bottom'
      )

      setup_sprite()

      pyglet.clock.schedule_interval(update_image, update_interval_seconds)
      pyglet.clock.schedule_interval(update_pan, 1/60.0)
      pyglet.clock.schedule_interval(update_zoom, 1/60.0)
      pyglet.clock.schedule_once(hide_mouse, mouse_hide_delay)

      pyglet.app.run()
