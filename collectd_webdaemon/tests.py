# coding: utf-8
from django.utils import unittest
import random
import base64
import lxml
from collectd_webdaemon.utils import generate_chart


class MetricsTestCase(unittest.TestCase):
    def test_generate_chart(self):
        N = 100
        data = {
            "dataset1": [
                # 0-ed values
                {"label": "DS1", "data": [0 for i in range(N)]},
            ],
            "dataset2": [
                # small random values and 0-ed values
                {"label": "DS1", "data": [random.random() for i in range(N)]},
                {"label": "DS2", "data": [0 for i in range(N)]},
            ],
            "dataset3": [
                # huge random values and small random values and the same name
                {"label": "DS1", "data": [(10 ** 6) * random.random() for i in
                    range(N)]},
                {"label": "DS1", "data": [random.random() for i in range(N)]},
            ],
        }
        result = generate_chart(data)
        decoded = base64.b64decode(result)
        for key, row in data.items():
            for series in row:
                self.assertGreaterEqual(decoded.find(series["label"]), 0)
                # I wanted to check for existance of every value from data in
                # generated output.  However, pygal is changing values so that
                # they are "scaled". So if MAX is 10 ** 6 * 1, then value 0.1
                # will become simply 0 in the output. Thus I'm only checking
                # for labels.

        # this will throw exceptions if XML is not right
        lxml.etree.fromstring(decoded)
