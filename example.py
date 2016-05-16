# encoding: utf-8
from modules.site import Site

site = Site("http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/")

for meeting in site.meetings("Kaupunginhallitus"):
    for doc in meeting.documents():
        print doc
        doc.download()
