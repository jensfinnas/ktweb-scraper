# encoding: utf-8

import requests
from tqdm import tqdm
import os


class Document(object):
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def __repr__(self):
        return (u'<Document: %s (%s)>' % (self.name, self.type)).encode('utf8')

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
            self.type,
        ]
        return "|".join(name_parts) + ".pdf"
