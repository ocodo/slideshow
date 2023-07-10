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
