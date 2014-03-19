# CMU course graph visualizer

## Scraping course information
Note: You do not need to do this to run the site! The data is already stored in `processed.tgz`. To get the pregenerated data, just run `make unpack-processed`.

This relies on CMU's new schedule of classes site at `https://enr-apps.as.cmu.edu/open/SOC/SOCServlet/search`. This works as of March 2014.

First, install the necessary packages into your Python 3 installation. You can use `make install-scrape` to do so. You may end up installing them into Python 2, in which case, use `pip3` manually.

Second, are you sure you really want to redownload all the data? You can try the pre-downloaded data stored in `raw.tgz` by running `make unpack-raw`. Afterward, to select only the pages you want to redownload, delete the relevant files.

Third, scrape the data by running `python3 pipeline.py`. If you are editing the scraper, you may want to set `force_scrape=True` in `get_all()` so you can test it on all the courses.

You should end up with a folder `processed` with a bunch of `.json` files. If there are any errors, you may review them in `pipeline.log`.

## Running the website
Install the necessary packages with `make install-site`.

If you want, set a port number with `export PORT=<number>`. The default port is `8080`.

For development, just run `python site/main.py` and go to `http://localhost:<port number>`.

Sometimes, on a force quit with <kbd>Ctrl</kbd><kbd>C</kbd>, the bottle server doesn't release its port. On Mac OS X, you can run `lsof -i :<port number>` and `kill <pid>` to kill the python process.
