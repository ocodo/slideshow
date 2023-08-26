dev_demo::
	./slideshow.py ./slides

portrait_demo::
	./slideshow.py ./portrait_slides

landscape_demo::
	./slideshow.py ./landscape_slides

stdin_demo::
	find ./slides | ./slideshow.py

slideshow_file_demo::
	./slideshow.py ./slides.slideshow

slideshow_recursive_demo::
	./slideshow.py ./recursive.slideshow

install::
	cp ./slideshow.py ~/.zsh.d/bin/slideshow

show_downloads::
	slideshow ${HOME}/Downloads

all:: install show_downloads
