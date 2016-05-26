# encoding: utf-8

from urllib2 import urlopen, HTTPError
from time import sleep

try:
    import settings
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()

from modules.site import Site

site = Site(settings.ktweb_url)

for body in site.bodies():
    for meeting in site.meetings(body.name):
        for document in meeting.documents():
            sleep(settings.delay)
            print document.url
            try:
                response = urlopen(document.url)
            except HTTPError:
                print "failed to open %s" % document.url
                continue
            size = response.info()["Content-Length"]
            print size
