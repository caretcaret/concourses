all:

install-scrape:
	pip install -r scrape-req.txt
install-site:
	pip install -r requirements.txt
unpack-raw:
	tar xzvf raw.tgz
unpack-processed:
	tar xzvf processed.tgz
