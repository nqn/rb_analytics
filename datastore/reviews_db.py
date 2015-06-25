import logging
from base_db import MongoDB

__author__ = 'marco'


REVIEWS_COLLECTION = 'reviews'


class Reviews(MongoDB):

    def __init__(self, conf):
        super(Reviews, self).__init__(conf, safe=True)
        self._log = logging.getLogger(self.__class__.__name__)

    def save(self, review):
        with self.context(REVIEWS_COLLECTION) as revs:
            return revs.save(review)

    def _ensure_indexes(self):
        with self.context(REVIEWS_COLLECTION) as coll:
            coll.ensure_index('submitter')
