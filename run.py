# encoding: utf-8

from urllib2 import urlopen, HTTPError, quote
from time import sleep
from modules.s3 import Bucket, open_s3_file
from textract import process
try:
    import settings
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()
from modules.site import Site
import magic


class FileType(object):
    UNKNOWN = 0
    PDF = 1
    DOC = 2
    DOCX = 3
    ODT = 4
    RTF = 5
    TXT = 6
    HTML = 7

    mime_to_type = {
        'application/pdf': PDF,
        'application/x-pdf': PDF,
        'application/msword': DOC,
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': DOCX,
        'application/vnd.oasis.opendocument.text': ODT,
        'application/rtf': RTF,
        'application/x-rtf': RTF,
        'text/richtext': RTF,
        'text/rtf': RTF,
        'text/plain': TXT,
        'text/html': HTML,
        'text/x-server-parsed-html': HTML,
        'application/xhtml+xml': HTML
    }

    type_to_ext = {
        UNKNOWN: None,
        PDF: "pdf",
        DOC: "doc",
        DOCX: "docx",
        ODT: "odt",
        RTF: "rtf",
        TXT: "txt",
        HTML: "html"
    }

    def get_mime_type(self, file_):
        with magic.Magic(flags=magic.MAGIC_MIME_TYPE) as m:
            # mimetype = m.id_buffer(file_)
            mimetype = m.id_filename(file_.name)
        try:
            file_type = self.mime_to_type[mimetype]
        except KeyError:
            file_type = self.UNKNOWN

        return file_type


def build_path(*args):
    """ Build a urlencoded slash separated string
    """
    list_ = [quote(x.encode("utf-8")) for x in args]
    return '/'.join(list_)


site = Site(settings.ktweb_url)
for body in site.bodies():
    for meeting in site.meetings(body.name):
        for document in meeting.documents():

            sleep(settings.delay)

            # Get headers
            try:
                response = urlopen(document.url)
            except HTTPError:
                print "failed to contact %s" % document.url
                continue

            info = response.info()
            size = info["Content-Length"]
            content_type = info["Content-Type"]
            # Get file name from `application/octet-stream; name=64248323.doc`
            file_name = content_type.split("; ")[1].split("=")[1]
            date_str = meeting.date.strftime("%Y-%m-%d")
            key = build_path(body.name, date_str,
                             document.name + "-" + file_name)

            # Check DB for key
            # TODO

            # Put file on S3
            bucket = Bucket(settings.s3_bucket)
            bucket.put_file_from_url(document.url, "files/" + key)

            # Extract mimetype, text and metadata
            with open_s3_file(bucket, "files/" + key) as file_:
                filetype = FileType()
                mimetype = filetype.get_mime_type(file_)
                ext = filetype.type_to_ext[mimetype]
                print ext

                exit()
                print process(file_.name)

            exit()
            # Add text to S3
            # Add to db
