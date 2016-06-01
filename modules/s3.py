# encoding: utf-8
""" Tiny S3 wrapper """

from boto3 import resource
from botocore.exceptions import ClientError
from tempfile import NamedTemporaryFile
from os import unlink
import requests


MEGABYTE = 1048576


class UploadError(Exception):
    """ S3 returned an error"""
    pass


class FileTooLarge(Exception):
    """ Use multipart upload instead """
    pass


class Bucket(object):
    """represents a connection to a bucket"""

    bucket_name = None
    bucket = None
    chunk_size = 1024 * 1024  # 1 MB

    def __init__(self, bucket_name):
        self.s3 = resource('s3')
        self.bucket_name = bucket_name
        self.bucket = self.s3.Bucket(self.bucket_name)

    def put_file_from_string(self, text, key):
        """ Put text in a public file on S3.
            Obviously not suitable for very large objects.
        """
        if len(text) > (50 * MEGABYTE):
            raise FileTooLarge("Please use multipart upload")
        self.bucket.put_object(ACL="public-read",
                               Body=text,
                               Key=key
                               )

    def put_file_from_url(self, url, key):
        """ Fetch and upload a file from the internet to S3.
            Will upload in chunks, to handle (very, very) large files
        """
        remote_file = self.bucket.Object(key)
        uploader = remote_file.initiate_multipart_upload()

        part_num = 0
        parts = []
        response = requests.get(url, stream=True)
        for block in response.iter_content(self.chunk_size):
            if block:
                part_num += 1
                part = uploader.Part(part_num)
                res = part.upload(Body=block)
                part_info = {
                    'PartNumber': part_num,
                    'ETag': res['ETag']
                }
                parts.append(part_info)

        parts_info = {
            "Parts": parts
        }
        try:
            uploader.complete(MultipartUpload=parts_info)
        except ClientError as error:
                raise UploadError(error)

    def get_file(self, key, file):
        """Download file"""
        return self.bucket.download_file(key, file)

    def get_file_content(self, key):
        """Return file content"""
        pass


class open_s3_file(object):
    """ Usage:
        `with open_s3_file(bucket, key) as file:`
    """
    def __init__(self, bucket, key):
        self.bucket = bucket
        self.key = key

    def __enter__(self):
        self.tmpfile = NamedTemporaryFile(delete=False)
        self.bucket.get_file(self.key, self.tmpfile.name)
        return self.tmpfile

    def __exit__(self, type, value, traceback):
        self.tmpfile.close()
        unlink(self.tmpfile.name)
