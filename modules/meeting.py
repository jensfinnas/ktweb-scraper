# encoding: utf-8

import requests
from bs4 import BeautifulSoup
from document import Document
import pdb 


class Meeting(object):
    """ Represents a meeting
    """
    def __init__(self, site, body, date):
        self.site = site
        self.body = body
        self.date = date

    def __repr__(self):
        return (u'<Meeting: %s, %s>' % (self.body.name, self.date)).encode('utf8')

    def documents(self):
        """ Returns a list of documents related to a meeting.
            Every paragraph has an own document.
            A paragraph can have multiple attachments. These are treated as
            independent documents
        """
        url = self.site.url + "pk_asil.htm"
        params = {
            " elin": self.body.id,
            "pvm": '{d.day}.{d.month}.{d.year} {d.hour}:{minute}'.format(d=self.date, minute="{0:02d}".format(self.date.minute)),
        }
        r = requests.get(url, params=params)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all("tr", { "class": "data0" }) + soup.find_all("tr", { "class": "data1" })
        documents = []
        for row in rows:
            document_link = row.find("a")
            document_name = document_link.text
            document_url = self.site.base_url + document_link["href"]
            document = Document(document_name, document_url)
            document.meeting = self

            cells = row.find_all("td")
            if len(cells) > 1:
                """ This is paragraph document
                """
                document.paragraph_number = cells[0].text
                document.type = "paragraph"
                documents.append(document)

                attachment_link = cells[2].find("a")
                if attachment_link:
                    attachment_url = self.site.base_url + attachment_link["href"]
                    for attachment_doc in self.get_attachments(attachment_url):
                        attachment_doc.parent_paragraph = document
                        documents.append(attachment_doc)
            else:
                """ For now we are ignoring "Kokousmateriaali" documents,
                    (collective documents containing all )
                """ 
                pass

        return documents

    def get_attachments(self, url):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        rows = soup.find_all("tr", { "class": "data0" }) + soup.find_all("tr", { "class": "data1" })
        attachments = []
        for row in rows:
            document_link = row.find("a")
            document_name = document_link.text
            document_url = self.site.base_url + document_link["href"]
            document = Document(document_name, document_url)
            document.type = "attachment"
            document.meeting = self
            attachments.append(document)
        return attachments