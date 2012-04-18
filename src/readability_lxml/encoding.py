import logging
import re
import chardet


LOG = logging.getLogger()


def get_encoding(page):
    LOG.info('GET ENCODING')
    LOG.info(type(page))
    text = re.sub('</?[^>]*>\s*', ' ', page)
    enc = 'utf-8'
    if not text.strip() or len(text) < 10:
        return enc  # can't guess
    try:
        diff = text.decode(enc, 'ignore').encode(enc)
        sizes = len(diff), len(text)
        # 99% of utf-8
        if abs(len(text) - len(diff)) < max(sizes) * 0.01:
            return enc
    except UnicodeDecodeError:
        pass
    res = chardet.detect(text)
    enc = res['encoding']
    # print '->', enc, "%.2f" % res['confidence']
    if enc == 'MacCyrillic':
        enc = 'cp1251'
    return enc
