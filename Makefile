dev_demo:
	./slideshow.py ./slides

portrait_demo:
	./slideshow.py ./portrait_slides

landscape_demo:
	./slideshow.py ./landscape_slides

install:
	cp ./slideshow.py ~/.zsh.d/bin/slideshow

show_downloads:
	slideshow ${HOME}/Downloads

all: install show_downloads
