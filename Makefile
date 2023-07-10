dev:
	./slideshow.py ./slides

install:
	cp ./slideshow.py ~/.zsh.d/bin/slideshow

run:
	slideshow ./slides

all: install run
