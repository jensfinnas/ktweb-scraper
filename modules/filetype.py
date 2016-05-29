# encoding: utf-8
import magic

from modules.extractors.pdf import PdfExtractor
from modules.extractors.ooxml import DocxExtractor
from modules.extractors.doc import DocExtractor
from modules.extractors.rtf import RtfExtractor
from modules.extractors.html import HtmlExtractor


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

    type_to_extractor = {
        PDF: PdfExtractor,
        DOCX: DocxExtractor,
        DOC: DocExtractor,
        RTF: RtfExtractor,
        HTML: HtmlExtractor
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
