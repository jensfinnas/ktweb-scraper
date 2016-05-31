#!/usr/bin/env python
# encoding: utf-8

from urllib2 import urlopen, HTTPError, Request
from time import sleep
from modules.s3 import Bucket, open_s3_file
from modules.site import Site
from modules.utils import build_path, get_header_value
from modules.filetype import FileType
from modules.interface import Interface
# Show a meaningful error msg if setup is not complete
try:
    import settings
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()


ui = Interface("Run", "Scrape, extract and store documents",
               commandline_args=["dryrun"])

site = Site(settings.ktweb_url)
for body in site.bodies():
    for meeting in site.meetings(body.name):
        for document in meeting.documents():

            document_data = {}
            sleep(settings.delay)

            response = None
            try:
                req = Request(document.url)
                req.add_header('User-agent', settings.user_agent)
                req.add_header('From', settings.email)
                response = urlopen(req)
            except HTTPError:
                print "failed to contact %s" % document.url
                continue

            info = response.info()
            try:
                # Weird, but sometimes the filename has been here
                file_name = get_header_value(info["Content-Type"],
                                             "name")
            except KeyError:
                file_name = get_header_value(info["Content-Disposition"],
                                             "filename")
            except KeyError:
                file_name = None

            date_str = meeting.date.strftime("%Y-%m-%d")
            key = build_path(body.name, date_str,
                             document.name)
            document_data["key"] = key
            document_data["file_name"] = file_name
            document_data["meeting_date"] = date_str
            document_data["meeting_body"] = body.name
            document_data["document_name"] = document.name
            document_data["size_at_server"] = info["Content-Length"]
            document_data["original_url"] = document.url

            # Check DB for key and size
            # TODO

            # Put file on S3
            ui.info("Putting %s on Amazon S3" % document.url)
            bucket = Bucket(settings.s3_bucket)
            if ui.args.dryrun:
                continue
            file_path = "files/" + key
            bucket.put_file_from_url(document.url, file_path)
            document_data["file_url"] = file_path

            # Do extraction
            text = None
            with open_s3_file(bucket, "files/" + key) as file_:
                filetype = FileType()
                mimetype = filetype.get_mime_type(file_)
                Extractor = filetype.type_to_extractor[mimetype]
                extractor = Extractor(file_.name)
                document_data["file_type"] = filetype.type_to_ext[mimetype]
                text = extractor.get_text()
                document_data["text_length"] = len(text)

            text_path = "text/" + key + ".txt"
            bucket.put_file_from_string(text, text_path)

            # Add to db
            exit()