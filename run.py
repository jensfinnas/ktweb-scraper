# encoding: utf-8

try:
    import settingse
except ImportError:
    print """Create a settings.py file to get started:
cp settings.default.py settings.py"""
    exit()

print settings.ktweb_url
