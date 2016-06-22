# encoding: utf-8

import requests
from tqdm import tqdm
import os


class Document(object):
    """Represents a single, downloadable document
    """

    name = None
    url = None
    meeting = None
    site = None
    agenda_or_minutes = None  # 'agenda' or 'minutes'
    paragraph_or_attachment = None  # 'paragraph' or 'attachment'
    paragraph_number = None
    parent_paragraph = None # Document instance with parent (for attachments) 

    def __init__(self, name=None,
                 url=None, meeting=None,
                 site=None, agenda_or_minutes=None,
                 parent_paragraph=None,
                 paragraph_or_attachment=None, paragraph_number=None):
        self.name = name
        self.url = url.replace(" ", "%20")
        self.meeting = meeting
        self.site = site
        self.agenda_or_minutes = agenda_or_minutes
        self.paragraph_or_attachment = paragraph_or_attachment
        self.paragraph_number = paragraph_number

    def __repr__(self):
        return (u'<Document (%s): %s (%s)>' % (
            self.agenda_or_minutes,
            self.name,
            self.paragraph_or_attachment
        )).encode('utf8')

    def download(self, file_name=None, directory="tmp"):
        if not file_name:
            file_name = self.generate_file_name()

        if not os.path.exists(directory):
            os.makedirs(directory)

        r = requests.get(self.url, stream=True)

        with open(directory + "/" + file_name, "wb") as handle:
            for data in tqdm(r.iter_content()):
                handle.write(data)

    def generate_file_name(self):
        """ Generates a file name
        """
        name_parts = [
            self.meeting.site.name,
            self.meeting.body.id,
            self.meeting.date.strftime("%Y-%m-%d %H:%M"),
            self.name,
            self.paragraph_or_attachment,
        ]
        return "|".join(name_parts) + ".pdf"
