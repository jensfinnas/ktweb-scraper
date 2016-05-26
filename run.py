# encoding: utf-8

from urllib2 import urlopen, HTTPError, quote
from time import sleep

try:
    import settings
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()

from modules.site import Site

site = Site(settings.ktweb_url)


def build_path(*args):
    """ Build a urlencoded slash separated string
    """
    list_ = [quote(x.encode("utf-8")) for x in args]
    return '/'.join(list_)

for body in site.bodies():
    for meeting in site.meetings(body.name):
        for document in meeting.documents():
            sleep(settings.delay)
            try:
                response = urlopen(document.url)
            except HTTPError:
                print "failed to open %s" % document.url
                continue

            """ Include size in key, just in case """
            size = response.info()["Content-Length"]
            date_str = meeting.date.strftime("%Y-%m-%d")
            key = build_path(body.name, date_str, document.name, size)
            print key
