from pysbdb import query
import wikipedia as w
import urllib.request as request
import argparse
from contextlib import redirect_stdout
import logging
from colorlog import ColoredFormatter
import sys

try:
    from BeautifulSoup import BeautifulSoup
except ImportError:
    from bs4 import BeautifulSoup

w.set_lang("zh")

abs_mag = 0

## parsing arugments

parser = argparse.ArgumentParser()

parser.add_argument("-f", "--start", help="from which index")
parser.add_argument(
    "-t", "--end", default=541129, help="to which index. Default is 541129"
)
parser.add_argument("-o", "--output", help="output filename")
args = parser.parse_args()

## logging to a file
formatter = ColoredFormatter(
    "%(log_color)s%(levelname)-8s%(reset)s %(log_color)s%(message)s",
    datefmt=None,
    reset=True,
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red,bg_white",
    },
    secondary_log_colors={},
    style="%",
)
formatter2 = logging.Formatter("[%(levelname)-2s] %(message)s")

rootLogger = logging.getLogger()
fileHandler = logging.FileHandler(args.output, mode="a")
fileHandler.setFormatter(formatter2)
rootLogger.addHandler(fileHandler)

## logging to stdout
consoleHandler = logging.StreamHandler(sys.stdout)
consoleHandler.setFormatter(formatter)
rootLogger.addHandler(consoleHandler)

rootLogger.setLevel(logging.INFO)

for i in range(int(args.start), int(args.end)):
    try:
        test = w.page(f"小行星{i}")
    except w.exceptions.PageError:
        logging.warning(f"ID:{i}, PageError")
        continue
    fp = request.urlopen(test.url)
    html = fp.read().decode("utf8")
    fp.close()
    parsed_html = BeautifulSoup(html)
    try:
        trs = (
            parsed_html.body.find("div", attrs={"id": "bodyContent"})
            .find("div", attrs={"id": "mw-content-text"})
            .find("div", attrs={"class": "mw-parser-output"})
            .find("table", attrs={"class": "infobox"})
            .tbody.findAll("tr")
        )
    except AttributeError:
        logging.warning(f"ID:{i}, AttributeError. Pass!")
        continue
    for tr in trs:
        if tr.a and ("絕對星等" in tr.a.text or "绝对星等" in tr.a.text):
            try:
                abs_mag = float(tr.td.text.split(".")[0])
            except ValueError:
                logging.warning(f"ID:{i}, ValueError: ID:{i} value: {tr.td.text}")
                continue
    ref = query.get_all(f"{i}")
    correct_abs_mag = float(ref["phys_par"][0]["value"])

    if abs(correct_abs_mag - abs_mag) > 5:
        logging.error(f"ID:{i} | wiki: {abs_mag} | real: {correct_abs_mag}")
    else:
        logging.info(f"ID:{i} OK")
    abs_mag = 0
