# Slideshow

Python / OpenGL image slideshow


##### License: GNU GPLv3

###  Requirements

- pyglet

(Built with Python 3.11)

### Usage

    # from the repo dir
    python3 slideshow.py <image_dir>
    
`slideshow.py` can also be placed in your `$PATH` and run standalone:

    slideshow.py <image_dir>

### Keyboard controls

| key            | description                                  |
|----------------|----------------------------------------------|
| `Q` or `Esc`   | Quit                                         |
| `Space`        | Pause                                        |
| `Left`/`Right` | Prev/Next image or Random Image              |
| `R`            | Random order on/off                          |
| `K`            | Ken Burns effect on/off                      |
| `1`-`9`        | 1 sec intervals from 1-9                     |
| `[` and `]`    | decrease interval / increase interval by 0.5 |

### Installation

No packaging, this is a standalone script, clone the repo and run as per usage above.

    git clone https://github.com/ocodo/slideshow 
