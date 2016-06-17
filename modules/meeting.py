# encoding: utf-8

import requests
from bs4 import BeautifulSoup
from document import Document
from itertools import chain


class Meeting(object):
    """ Represents a meeting.
        A meeting re
    """
    def __init__(self, site, body, date):
        self.site = site
        self.body = body
        self.date = date

    def __repr__(self):
        return (u'<Meeting: %s, %s>' %
                (self.body.name, self.date)).encode('utf8')

    def documents(self):
        """ Returns both agenda ("esityslista") and minutes ("pöytäkirja")
        """
        return chain(self.minutes(), self.agenda())

    def minutes(self):
        """ Returns all meeting minutes ("pöytäkirja") as list of documents.
        """
        return self._get_documents("minutes")

    def agenda(self):
        """ Returns agenda ("esityslista") as list of documents.
        """
        return self._get_documents("agenda")

    def _get_documents(self, agenda_or_minutes):
        """ Returns a list of documents related to a meeting.
            url should be "epj_asil.htm" or
            Every paragraph has an own document.
            A paragraph can have multiple attachments. These are treated as
            independent documents
        """
        if agenda_or_minutes == "agenda":
            url = self.site.url + "epj_asil.htm"
        elif agenda_or_minutes == "minutes":
            url = self.site.url + "pk_asil.htm"
        else:
            raise ValueError("Define if you want to get agenda or minutes")

        params = {
            " elin": self.body.id,
            "pvm": '{d.day}.{d.month}.{d.year} {d.hour}:{minute}'
                   .format(d=self.date, minute="{0:02d}"
                           .format(self.date.minute)),
        }
        r = requests.get(url, params=params)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all("tr", {"class": "data0"}) +\
            soup.find_all("tr", {"class": "data1"})

        for row in rows:
            cells = row.find_all("td")
            if len(cells) > 1:
                """ This is paragraph document
                """
                document_link = row.find("a")
                document_name = document_link.text
                document_url = self.site.base_url + document_link["href"]

                document = Document(
                    name=document_name,
                    url=document_url,
                    meeting=self,
                    agenda_or_minutes=agenda_or_minutes,
                    paragraph_number=cells[0].text,
                    paragraph_or_attachment="paragraph",
                )
                yield document

                attachment_link = cells[2].find("a")
                if attachment_link:
                    attachment_url = self.site.base_url + attachment_link["href"]
                    for attachment_doc in self.get_attachments(attachment_url):
                        attachment_doc.agenda_or_minutes = agenda_or_minutes
                        attachment_doc.parent_paragraph = document
                        yield attachment_doc
            else:
                """ For now we are ignoring "Kokousmateriaali" documents,
                    (collective documents containing all)
                """
                pass

    def get_attachments(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all("tr", {"class": "data0"}) +\
            soup.find_all("tr", {"class": "data1"})
        for row in rows:
            document_link = row.find("a")
            document_name = document_link.text
            document_url = self.site.base_url + document_link["href"]
            document = Document(
                name=document_name,
                url=document_url,
                paragraph_or_attachment="attachment",
                meeting=self,
            )
            yield document
