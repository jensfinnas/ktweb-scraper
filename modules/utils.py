# encoding: utf-8


def parse_int(string):
    return int(float(string))

python_encodings = ["ascii",
                    "cp037",
                    "cp437",
                    "cp500",
                    "cp775",
                    "cp850",
                    "cp857",
                    "cp858",
                    "cp861",
                    "cp863",
                    "cp865",
                    "cp1026",
                    "cp1250",
                    "cp1252",
                    "cp1257",
                    "latin_1",
                    "iso8859_1",
                    "iso8859_4",
                    "iso8859_9",
                    "iso8859_13",
                    "iso8859_14",
                    "iso8859_15",
                    "mac_latin2",
                    "mac_roman"]
"""Subset of standard encodings supported by Python, that occurs in
   Scandinavian documents. For use with encoding guessing algorithms, etc.

   Basically any encoding that contains å,ä and ö seem to have been used by
   someone, at some point. Collection based on experience from Protokollen.
"""


def make_unicode(str_):
    """This method will try to convert any string to a unicode object,
       using whatever encoding works. This is a last resort, when we
       have no ideas about encodings.

       This method is used when storing metadata, that can be heavily
       messed-up as files are abused by ill-behaved software
    """
    output = u""
    if str_ is None:
        return output
    try:
        output = unicode(str_, 'utf-8')
    except TypeError:
        # Already unicode
        output = str_
    except UnicodeDecodeError:
        # At this point we have no idea of knowing what encoding
        # this might be. Let try a few
        for encoding in python_encodings:
            try:
                output = str_.decode(encoding, "ignore")
                break
            except UnicodeDecodeError:
                continue
    # remove null character
    output = output.replace(u"\u0000", u"")
    return output
