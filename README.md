# Event Attendees Badge Generator 

$title$

Generates PDF suitable for printing on stickers sheets

## Install

Create your virtual env so you don't bloat your dir

    python3 -m venv env

Activate it before doing anything

    source env/bin/activate

Install dependencies

    pip install -r requirements.txt

## Usage

Generate badges for the full attendees list

    python genbadge.py infile.csv outfile.pdf

Other options available with the usual help

    python genbadge.py --help

    usage: genbadges.py [-h] [--layout LAYOUT] [--layout-list] [--start START] [--csvfirst CSVFIRST] [--csvlast CSVLAST] [input.csv] [output.pdf]

    positional arguments:
      input.csv
      output.pdf

    options:
      -h, --help           show this help message and exit
      --layout LAYOUT
      --layout-list        display supported layouts
      --start START        start number of layout sticker
      --csvfirst CSVFIRST  csv entries first index to process
      --csvlast CSVLAST    csv entries last index to process


Prints the 5th and 6th entries from the CSV file starting on the 3rd sticker position

    python genbadge.py infile.csv outfile.pdf --start=3 --csvfirst=5 --csvlast=6

Note the stickers are numbered from bottom to top, from left to right. *Read it again*

## Limitations

 - If you're not happy, then deal with it or learn to code



