import re


uids = {}
RE_COLLAPSE_WHITESPACES = re.compile('\s+', re.U)


def open_in_browser(html):
    """
    Open the HTML document in a web browser, saving it to a temporary
    file to open it.  Note that this does not delete the file after
    use.  This is mainly meant for debugging.
    """
    import os
    import webbrowser
    import tempfile
    handle, fn = tempfile.mkstemp(suffix='.html')
    f = os.fdopen(handle, 'wb')
    try:
        f.write("<meta charset='UTF-8' />")
        f.write(html.encode('utf-8'))
    finally:
        # we leak the file itself here, but we should at least close it
        f.close()
    url = 'file://' + fn.replace(os.path.sep, '/')
    webbrowser.open(url)
    return url


def describe_node(node):
    if node is None:
        return ''
    if not hasattr(node, 'tag'):
        return "[%s]" % type(node)
    name = node.tag
    if node.get('id', ''):
        name += '#' + node.get('id')
    if node.get('class', ''):
        name += '.' + node.get('class').replace(' ', '.')
    if name[:4] in ['div#', 'div.']:
        name = name[3:]
    if name in ['tr', 'td', 'div', 'p']:
        uid = uids.get(node)
        if uid is None:
            uid = uids[node] = len(uids) + 1
        name += "{%02d}" % uid
    return name


def describe(node, depth=2):
    #return repr(NodeRepr(node))
    parent = ''
    if depth and node.getparent() is not None:
        parent = describe(node.getparent(), depth=depth - 1)
    return parent + '/' + describe_node(node)


def text_content(elem, length=40):
    content = RE_COLLAPSE_WHITESPACES.sub(' ', elem.text_content().replace('\r', ''))
    if len(content) < length:
        return content
    return content[:length] + '...'
