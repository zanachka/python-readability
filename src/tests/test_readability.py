import unittest

from readability_lxml.readability import Document


class TestReadabilityDocument(unittest.TestCase):
    """Test the Document parser."""

    def test_none_input_raises_exception(self):
        """Feeding a None input to the document should blow up."""

        doc = None
        self.assertRaises(ValueError, Document, doc)
