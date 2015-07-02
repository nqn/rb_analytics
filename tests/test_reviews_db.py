
import copy
import json
import unittest
from datastore import base_db

from datastore.reviews_db import (Reviews,
                                  REVIEWS_COLLECTION)

__author__ = 'marco'


JSON_DATA = 'tests/data/review.json'


class ReviewsDbTests(unittest.TestCase):

    def from_file(self):
        with open(JSON_DATA) as review:
            return json.loads(''.join(review.readlines()))

    def setUp(self):
        self.conf = {
            'db.host': 'localhost',
            'db.port': 27017,
            'db.name': 'test-rb-analytics'
        }
        self.db = Reviews(self.conf)
        self.assertIsNotNone(self.db, "This test requires a running MongoDb on localhost:27017")
        self.review = self.from_file()

    def tearDown(self):
        self.assertIsNotNone(self.db)
        self.db.drop_collection(REVIEWS_COLLECTION)

    def test_save(self):
        if self.review is not None:
            self.assertIsNotNone(self.db.save(self.review))
        else:
            self.fail("Could not parse data into a valid review object")

    def test_get(self):
        rev_id = 36037
        self.assertRaises(base_db.DBNoRecordFound, self.db.get, *[rev_id])
        self.test_save()
        self.assertIsNotNone(self.db.get(rev_id))

    def test_cleanup(self):
        clean_rev = self.db._cleanup(self.review)
        for fld in Reviews.FIELDS_TO_REMOVE:
            self.assertIsNone(clean_rev.get(fld))

    def test_replace_submitter(self):
        rev = self.db._replace_submitter(self.review)
        submitter = rev.get('submitter')
        self.assertIsNotNone(submitter)
        self.assertEqual("ijimenez", submitter)

    def test_extract_reviewers(self):
        rev = self.db._extract_reviewers(self.review)
        reviewers = rev.get('reviewers')
        self.assertIsInstance(reviewers, list)
        self.assertListEqual(["anandmazumdar","benjaminhindman",
                              "bmahler", "marco", "vinodkone"], reviewers)

    def test_extract_deps(self):
        rev = self.db._extract_deps(self.review)
        deps = rev.get('dependencies')
        self.assertIsInstance(rev, dict)
        self.assertEqual(36073, deps['depends_on'][0])
        self.assertEqual(2, len(deps['blocked_by']))
        self.assertEqual(45568, deps['blocked_by'][1])

    def test_not_found_raises(self):
        with self.assertRaises(base_db.DBNoRecordFound):
            self.db.get(99)

    def test_find_all(self):
        for rev_id in xrange(4356, 4366):
            new_rev = copy.deepcopy(self.review)
            new_rev['id'] = rev_id
            self.db.save(new_rev)
        all_revs = self.db.get_all_ids()
        self.assertIsInstance(all_revs, list)
        self.assertEqual(10, len(all_revs))
        for rev_id in xrange(4356, 4366):
            self.assertIn(rev_id, all_revs)
