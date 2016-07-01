# encoding: utf-8
"""
Copy this file to settings.py, and make any changes there!
"""

ktweb_url = "http://ktweb.tampere.fi/ktwebbin/dbisa.dll/ktwebscr/"

s3_bucket = "ktweb.tampere"
""" Amazon S3 bucket where files should be stored """

delay = 1
""" Number of seconds to sleep between downloads """

user_agent = "Mozilla/5.0 (compatible); Alma document scraper"
""" How do we identify when visiting web pages? """

email = "stockholm@jplusplus.org"
""" Contact address, in case robot tries to take over world """

db_uri = None
""" URI for the MongoDB instance, eg mongodb://localhost:27017/ """

db_name = None
""" A MongoDB instance can have multiple databases """

db_table = None
""" The MongoDB Collection"""

max_file_size = 30
""" Size in MB. Larger files will be ignored. Use None for no limit """

start_date = None
""" Earliest date to fetch documents from. None means no filtering """
