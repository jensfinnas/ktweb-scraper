#!/usr/bin/env python
# encoding: utf-8

from urllib2 import urlopen, HTTPError, quote, Request
from time import sleep
from modules.s3 import Bucket, open_s3_file
# Make sure settings.py is set up
try:
    import settings
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()
from modules.site import Site
from modules.filetype import FileType
from modules.interface import Interface


def build_path(*args):
    """ Build a urlencoded slash separated string
    """
    list_ = [quote(x.encode("utf-8")) for x in args]
    return '/'.join(list_)


cmd_args = [
]
ui = Interface("Run",
               "Scrape, extract and store documents",
               commandline_args=cmd_args)

site = Site(settings.ktweb_url)
for body in site.bodies():
    for meeting in site.meetings(body.name):
        for document in meeting.documents():

            sleep(settings.delay)

            try:
                req = Request(document.url)
                req.add_header('User-agent', settings.user_agent)
                response = urlopen(req)
            except HTTPError:
                print "failed to contact %s" % document.url
                continue

            info = response.info()
            size = info["Content-Length"]
            content_type = info["Content-Type"]
            # Get file name from `application/octet-stream; name=64248323.doc`
            try:
                file_name = content_type.split("; ")[1].split("=")[1]
            except IndexError:
                file_name = ""
            date_str = meeting.date.strftime("%Y-%m-%d")
            key = build_path(body.name, date_str,
                             document.name + "-" + file_name)

            # Check DB for key
            # TODO

            # Put file on S3
            ui.info("Putting %s on Amazon S3" % document.url)
            bucket = Bucket(settings.s3_bucket)
            if ui.args["dryrun"]:
                continue
            bucket.put_file_from_url(document.url, "files/" + key)

            # Do extraction
            with open_s3_file(bucket, "files/" + key) as file_:
                filetype = FileType()
                mimetype = filetype.get_mime_type(file_)
                ext = filetype.type_to_ext[mimetype]
                Extractor = filetype.type_to_extractor[mimetype]
                extractor = Extractor(file_.name)
                text = extractor.get_text()
                print file_.name
                print ext
                print Extractor
                print text

            exit()
            # Add text to S3
            # Add to db
