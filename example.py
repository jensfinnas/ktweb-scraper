# encoding: utf-8
from modules.site import Site

site = Site("http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/")

from datetime import datetime

for meeting in site.meetings("Kaupunginhallitus", after_date="2016-06-01"):
    print meeting
    for doc in meeting.documents():
        print doc
        doc.download()
