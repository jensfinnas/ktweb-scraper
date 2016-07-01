# encoding: utf-8
from modules.site import Site

site = Site("http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/")

from datetime import datetime

for meeting in site.meetings("Kaupunginhallitus", after_date="2016-07-01"):
    print meeting
    for doc in meeting.minutes():
        print doc
        #doc.download()
