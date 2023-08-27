# Slideshow

Python / OpenGL image slideshow

##### License: GNU GPLv3

###  Requirements

- pyglet
- pyperclip

(Built with Python 3.11)

### Usage

    # from the repo dir
    pip install -r requirements.txt
    python slideshow.py <image_dir>

    # stdin
    # slideshow.py is executable
    find images/ | ./slideshow.py

    # .slideshow file
    ./slideshow myslides.slideshow

### As an executable
    
`slideshow.py` can also be placed in your `$PATH` and run standalone:

    slideshow.py <image_dir>

I symlink it as `slideshow` for convenience.

### Image list in `.slideshow` file

You can list image path names in a .slideshow file.  I recommend absolute path names, although relative pathnames to the `.slideshow` file, are recognized.

You can also nest `.slideshow` files so `slides.slideshow` could contain:

```
slides01.slideshow
slides02.slideshow
```

Which will load the slides from both `slides01.slideshow` and `slides02.slideshow` with:

```
./slideshow.py slides.slideshow
```

### Keyboard controls

| Key            | Command                                      |
|:---------------|:---------------------------------------------|
| `q` or `Esc`   | Quit                                         |
| `Space`        | Pause                                        |
| `Left`/`Right` | Prev/Next image or Random Image              |
| `r`            | Random order on/off                          |
| `k`            | Ken Burns effect on/off                      |
| `1`-`9`        | 1 sec intervals from 1-9                     |
| `[` and `]`    | Decrease interval / increase interval by 0.5 |
| `i`            | Copy current image filename to clipboard     |
| `a` (or `z`)   | Sort images alphabetically (or reverse)      |
| `n` (or `o`)   | Sort images by newest date (or oldest)       |


### Mouse controls

| Mouse action                     | Command                                  |
|:---------------------------------|:-----------------------------------------|
| Left click, right half of window | Next Image                               |
| Left click, left half of window  | Prev Image                               |
| Right click, right 3rd of window | Ken Burns Effect Toggle                  |
| Right click, left 3rd of window  | Random Toggle                            |
| Right click, Middle of window    | Pause                                    |
| Scroll wheel                     | Zoom                                     |
| Drag                             | Pan                                      |
|                                  |                                          |

### Installation

No packaging, this is a standalone script, clone the repo and run as per usage above.

    git clone https://github.com/ocodo/slideshow 

### 
