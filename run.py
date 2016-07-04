#!/usr/bin/env python
# encoding: utf-8

from urllib2 import urlopen, HTTPError, URLError, Request
from time import sleep
from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError
from modules.s3 import Bucket, open_s3_file, UploadError
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

MEGABYTE = 1048576
GIGABYTE = 1073741824
TERABYTE = 1099511627776

ui = Interface("Run", "Scrape, extract and store documents",
               commandline_args=["dryrun", "overwrite"])

ui.info("Setting up database connection")
client = MongoClient(settings.db_uri)
db = client[settings.db_name]
collection = db[settings.db_table]
try:
    ui.info("Database has %s documents" % collection.count())
except ServerSelectionTimeoutError:
    ui.error("""MongoDB server timed out.
This is most likely due to your IP address not being whitelisted.""")
    ui.exit()

ui.info("Setting up scraper")
site = Site(settings.ktweb_url)

ui.info("Setting up Amazon S3 connection")
bucket = Bucket(settings.s3_bucket)

for body in site.bodies():
    for meeting in site.meetings(body.name, after_date=settings.start_date):
        for document in meeting.documents():

            ui.debug("Processing document: %s" % document)
            document_data = {}
            sleep(settings.delay)

            response = None
            try:
                req = Request(document.url)
                req.add_header('User-agent', settings.user_agent)
                req.add_header('From', settings.email)
                response = urlopen(req)
            except HTTPError, URLError:
                ui.warning("Failed to contact %s. Skipping." % document.url)
                continue

            info = response.info()
            try:
                # Weird, but sometimes the filename has been here
                file_name = get_header_value(info["Content-Type"],
                                             "name")
            except KeyError:
                try:
                    file_name = get_header_value(info["Content-Disposition"],
                                                 "filename")
                except KeyError:
                    file_name = None

            date_str = meeting.date.strftime("%Y-%m-%d")
            key = build_path(body.name, date_str,
                             document.agenda_or_minutes, document.name)
            document_data["document_type"] = document.agenda_or_minutes
            document_data["key"] = key
            document_data["created_date"] = datetime.utcnow()
            document_data["file_name"] = file_name
            document_data["meeting_date"] = date_str
            document_data["meeting_body"] = body.name
            document_data["document_name"] = document.name
            document_data["size_at_server"] = info["Content-Length"]
            document_data["original_url"] = document.url
            if document.parent_paragraph:
                # Fro attachments
                document_data["parent_paragraph_url"] = document.parent_paragraph.url
            else:
                document_data["parent_paragraph_url"] = None                

            # Check DB for key and size
            ui.debug("Checking database for key %s" % key)
            if collection.find_one({"key": key}):
                if ui.args.overwrite:
                    ui.info("Key already in database. Overwriting %s." % key)
                else:
                    ui.debug("Key already in database. Skipping.")
                    continue
            else:
                ui.info("Key not in database. Adding %s." % key)

            if ui.args.dryrun:
                continue

            if settings.max_file_size is not None \
                    and int(document_data["size_at_server"]) > \
                    settings.max_file_size * MEGABYTE:
                ui.warning("Skipping large file: %s" % key)
                continue

            # Put file on S3
            ui.debug("Copying file to Amazon S3 from %s (%s bytes)" %
                     (document.url, document_data["size_at_server"]))
            file_path = "files/" + key
            if int(document_data["size_at_server"]) < (10 * MEGABYTE):
                ui.debug("Using simple upload")
                bucket.put_file_from_string(response.read(), file_path)
            else:
                ui.debug("Using multipart upload")
                try:
                    bucket.put_file_from_url(document.url, file_path)
                except UploadError:
                    # ui.debug("Multipart upload failed, trying in one chunk.")
                    # bucket.put_file_from_string(response.read(), file_path)
                    ui.debug("Multipart upload failed, giving up.")
                    continue

            document_data["file_url"] = file_path

            # Do extraction
            ui.debug("Opening file for extraction.")
            text = None
            with open_s3_file(bucket, "files/" + key) as file_:
                filetype = FileType()
                mimetype = filetype.get_mime_type(file_)
                try:
                    Extractor = filetype.type_to_extractor[mimetype]
                except KeyError:
                    ui.warning("No extractor available for filetype %s in %s" %
                               (mimetype, document.url))
                    continue
                extractor = Extractor(file_.name)
                document_data["file_type"] = filetype.type_to_ext[mimetype]
                try:
                    text = extractor.get_text()
                except Exception as error:
                    ui.warning("Failed to extract text from %s. %s" %
                               (document.url, error))
                    continue
                document_data["text_length"] = len(text)

            text_path = "text/" + key + ".txt"
            bucket.put_file_from_string(text, text_path)
            document_data["text_url"] = text_path

            # Add content-type to S3
            ui.debug("Setting content-type at S3")
            bucket.set_content_type(file_path, filetype.type_to_mime[mimetype])

            # Add to db
            ui.debug("Putting data in database")
            result = collection.replace_one({"key": key},  # Replace if exists
                                            document_data,
                                            upsert=True)
