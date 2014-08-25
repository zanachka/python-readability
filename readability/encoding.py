import re
import chardet
import logging

log = logging.getLogger('readbility.encoding')


RE_CHARSET = re.compile(r'<meta.*?charset=["\']*(.+?)["\'>]', re.I)
RE_PRAGMA = re.compile(r'<meta.*?content=["\']*;?charset=(.+?)["\'>]', re.I)
RE_XML = re.compile(r'^<\?xml.*?encoding=["\']*(.+?)["\'>]')

CHARSETS = {
    'big5': 'big5hkscs',
    'gb2312': 'gb18030',
    'ascii': 'utf-8',
    'MacCyrillic': 'cp1251',
}


def fix_charset(encoding):
    """Overrides encoding when charset declaration
       or charset determination is a subset of a larger
       charset.  Created because of issues with Chinese websites"""
    encoding = encoding.lower()
    return CHARSETS.get(encoding, encoding)


def get_encoding(page):
    declared_encodings = (RE_CHARSET.findall(page) +
                          RE_PRAGMA.findall(page) +
                          RE_XML.findall(page))

    log.debug("Document has the following encodings: %s" % declared_encodings)

    # Try declared encodings, if any
    for declared_encoding in declared_encodings:
        encoding = fix_charset(declared_encoding)
        try:
            page.decode(encoding)
            log.info('Using encoding "%s"' % encoding)
            return encoding
        except UnicodeDecodeError:
            log.info('Encoding "%s", specified in the document as "%s" '
                     'didn\'t work' % (encoding, declared_encoding))
            print "Content encoding didn't work:", encoding

    # Fallback to chardet if declared encodings fail
    text = re.sub('</?[^>]*>\s*', ' ', page)
    enc = 'utf-8'
    if not text.strip() or len(text) < 10:
        log.debug("Can't guess encoding because text is too short")
        return enc
    res = chardet.detect(text)
    enc = fix_charset(res['encoding'])
    log.info('Trying encoding "%s" guessed '
             'with confidence %.2f' % (enc, res['confidence']))
    #print '->', enc, "%.2f" % res['confidence']
    return enc
