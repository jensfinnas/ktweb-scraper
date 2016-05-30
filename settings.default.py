# encoding: utf-8
"""
Use settings.py override any of these settings.
"""

ktweb_url = "http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/"

s3_bucket = "ktweb.tampere"
""" Amazon S3 bucket where files should be stored """

delay = 1
""" Number of seconds to sleep between downloads """

user_agent = "Mozilla/5.0 (compatible); Alma document scraper"
"""How do we identify when visiting web pages?"""
