readability_lxml
================

This is a python port of a ruby port of `arc90's readability`_ project

Given a html document, it pulls out the main body text and cleans it up.
It also can clean up title based on latest readability.js code.


Inspiration
-----------
- Latest readability.js ( https://github.com/MHordecki/readability-redux/blob/master/readability/readability.js )
- Ruby port by starrhorne and iterationlabs
- Python port by gfxmonk ( https://github.com/gfxmonk/python-readability , based on BeautifulSoup )
- Decruft effort to move to lxml ( http://www.minvolai.com/blog/decruft-arc90s-readability-in-python/ )
- "BR to P" fix from readability.js which improves quality for smaller texts.
- Github users contributions.


Try it out!
-----------
You can try out the parser by entering your test urls on the following test
service.

http://readable.bmark.us


Installation
-------------
::

    $ easy_install readability-lxml
    # or
    $ pip install readability-lxml


Usage
------

Command Line Client
~~~~~~~~~~~~~~~~~~~
::

    $ readability http://pypi.python.org/pypi/readability-lxml
    $ readability /home/rharding/sampledoc.html

As a Library
~~~~~~~~~~~~
::

    from readability.readability import Document
    import urllib
    html = urllib.urlopen(url).read()
    readable_article = Document(html).summary()
    readable_title = Document(html).short_title()

You can also use the `get_summary_with_metadata` method to get back other
metadata such as the confidence score found while processing the input.

::

    doc = Document(html).summary_with_metadata()
    print doc.html
    print doc.confidence


Optional `Document` keyword argument:

- attributes:
- debug: output debug messages
- min_text_length:
- multipage: should we try to parse and combine multiple page articles?
- retry_length:
- url: will allow adjusting links to be absolute


Test and BUild Status
---------------------
Tests are run against the package at:

http://build.bmark.us/job/readability-lxml/

You can view it for build history and test status.


History
-------

- `0.2.5` Update setup.py for uploading .tar.gz to pypi


.. _arc90's readability: http://lab.arc90.com/experiments/readability/
