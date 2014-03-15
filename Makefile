all:

install-scrape:
	pip install requests
	pip install beautifulsoup4
	pip install html5lib
unpack-raw:
	tar xzvf raw.tgz
unpack-processed:
	tar xzvf processed.tgz
