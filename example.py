# encoding: utf-8
from modules.site import Site

site = Site("http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/")

from datetime import datetime

for meeting in site.meetings("Kaupunginhallitus", after_date="2016-01-01"):
    print meeting
    for doc in meeting.minutes():
        print doc
        print "Parent: " + str(doc.parent_paragraph)
        #doc.download()
