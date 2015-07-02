import logging
import re

import base_db

__author__ = 'marco'


REVIEWS_COLLECTION = 'reviews'

SUBMITTER_REGEX = re.compile(r'https://reviews.apache.org/api/users/(\w+)/')
RR_ID_REGEX = re.compile(r'https://reviews.apache.org/api/review-requests/(\d+)/')


class Reviews(base_db.MongoDB):

    FIELDS_TO_REMOVE = ['links',
                        'target_groups',
                        'target_people',
                        'description_text_type',
                        'close_description_text_type',
                        'testing_done_text_type',
                        'testing_done',
                        'text_type',
                        'changenum',
                        'branch',
                        'approval_failure',
                        'extra_data',
                        'depends_on',
                        'public',
                        'blocks',
                        'target_people'
                        ]

    def __init__(self, conf):
        super(Reviews, self).__init__(conf, safe=True)
        self._log = logging.getLogger(self.__class__.__name__)

    def _cleanup(self, review):
        for field in Reviews.FIELDS_TO_REMOVE:
            # We will ignore already missing field; please keep default None
            review.pop(field, None)
        return review

    @staticmethod
    def _replace_submitter(review):
        if 'submitter' in review.get('links'):
            sub = review['links']['submitter']['href']
            # TODO(marco): should we just use the 'title' field?
            m = re.match(SUBMITTER_REGEX, sub)
            if m and m.groups() > 0:
                review['submitter'] = m.group(1)
        return review

    @staticmethod
    def _extract_reviewers(review):
        tp = review.get('target_people')
        reviewers = []
        for target in tp:
            reviewers.append(target.get('title'))
        review['reviewers'] = reviewers
        return review

    @staticmethod
    def _extract_deps(review):
        depends_on = []
        blocked_by = []
        for depends in review.get('depends_on', None):
            m = re.match(RR_ID_REGEX, depends.get('href'))
            if m:
                depends_on.append(int(m.group(1)))
        for blocks in review.get('blocks', None):
            m = re.match(RR_ID_REGEX, blocks.get('href'))
            if m:
                blocked_by.append(int(m.group(1)))
        review['dependencies'] = {
            'depends_on': depends_on,
            'blocked_by': blocked_by
        }
        return review

    def save(self, review):
        with self.context(REVIEWS_COLLECTION) as revs:
            if 'id' in review:
                review['_id'] = review.pop('id')
            review = Reviews._replace_submitter(review)
            review = Reviews._extract_reviewers(review)
            review = Reviews._extract_deps(review)
            return revs.save(self._cleanup(review))

    def get(self, review_id):
        with self.context(REVIEWS_COLLECTION) as rrs:
            result = rrs.find_one(review_id)
        if result:
            return result
        else:
            raise base_db.DBNoRecordFound("Could not find Review #{}".format(review_id))

    def get_all_ids(self):
        """ Retrieves all RRs currently in DB and returns the IDs

            :return: a list of RRs' IDs that can be used either to build the URL or
                by calling the ``get(id)`` method
            :rtype: list
        """
        with self.context(REVIEWS_COLLECTION) as revs:
            result = revs.find(filter={}, projection=['_id'])
            ids = []
            for res in result:
                ids.append(res.get('_id'))
            return ids

    def _ensure_indexes(self):
        with self.context(REVIEWS_COLLECTION) as coll:
            coll.ensure_index('last_updated')
            coll.ensure_index('time_added')
            coll.ensure_index('submitter')

    def drop(self):
        self.drop_collection(REVIEWS_COLLECTION)
