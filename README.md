# A scraper for a KT Web interface for documents

Tested on City of Tampere.

## Install

    sudo apt-get install python-pip python git abiword tesseract-ocr tesseract-ocr-fin wv ghostscript python-imaging python-dev libxml2-dev libxslt1-dev zlib1g-dev libjpeg62 libjpeg62-dev
    git clone https://github.com/jensfinnas/ktweb-scraper
    cd ktweb-scraper
    pip install -r requirements.txt

You will also need to put your Amazon AWS credentials in `~/.aws`, as per https://aws.amazon.com/developers/getting-started/python/


## Command line usage

To start scraping:

    python run.py

To get help:

    python run.py --help

## Using the scraper as a Python module

Basic initialization.

``` python
from modules.site import Site

site = Site("http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/")
```

Get a list of all available decision-making bodies.

``` python
print site.bodies()
```

Get a list of all upcoming or past (or both) meetings from a given body.

``` python
print site.upcoming_meetings("Kaupunginhallitus")
print site.past_meetings("Kaupunginhallitus")
print site.meetings("Kaupunginhallitus")
```

You can also choose to only get meetings after a specific date.

``` python
print site.meetings("Kaupunginhallitus", after_date="2016-06-01")
```

Meetings have two kind of documents: agendas ("esityslista") and minutes ("pöytäkirja"). 
You can get those using `meeting.agenda()` and `meeting.minutes()`. Or both  using `meeting.documents()`

``` python
for meeting in site.meetings("Kaupunginhallitus"):
    for doc in meeting.documents():
    	print doc
```

Documents can also be downloaded.

``` python
doc.download()
```

By default documents are downloaded to a `tmp` folder with an autogenerated file name. Override these defaults with: 

```python
doc.download(file_name="my_file.pdf", folder="myfolder")
```
