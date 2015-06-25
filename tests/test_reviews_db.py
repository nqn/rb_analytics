import unittest

from datastore.reviews_db import (Reviews,
                                  REVIEWS_COLLECTION)

__author__ = 'marco'


class ReviewsDbTests(unittest.TestCase):

    def setUp(self):
        self.conf = {
            'db.host': 'localhost',
            'db.port': 27017,
            'db.name': 'test-rb-analytics'
        }
        self.db = Reviews(self.conf)
        self.assertIsNotNone(self.db)

    def tearDown(self):
        self.assertIsNotNone(self.db)
        self.db.drop_collection(REVIEWS_COLLECTION)

    def test_save(self):
        review = {
            'submitter': 'marco',
            '_id': 27734,
            'title': 'test review'
        }
        self.assertIsNotNone(self.db.save(review))
