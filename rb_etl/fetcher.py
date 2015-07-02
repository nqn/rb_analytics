# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests

from datastore.reviews_db import Reviews

__author__ = 'Marco Massenzio'
__email__ = 'marco@mesosphere.io'


LOG_FORMAT = '%(asctime)s [%(levelname)-5s] %(message)s'


class FetcherError(Exception):
    pass


class ReviewFetcher(object):
    """ This class encapsulates our ETL cycle from RB to Mongo
    """

    ARGS = {
        'to-groups': 'mesos',
        'status': 'pending',
        'max-results': 50,
        'start': 0
    }

    RB_URL = 'http://reviews.apache.org/api/review-requests/?'

    def __init__(self, conf):
        """ Initializes the ETL module, connects to MongoDB

        :param conf: a configuration dictionary; should include DB config too; for this
            class, the only argument will be `since` which should conform to a ISO date
            (ie, '2015-11-13')
        """
        self.reviews = Reviews(conf)
        self.args = ReviewFetcher.ARGS
        self.args['last-updated-from'] = conf.get('since')
        self.next_url = self._build_url(ReviewFetcher.RB_URL, self.args)
        self.total = 0
        self.rrs = []

    @staticmethod
    def _build_url(url, args):
        """ Builds up the URL for the initial RB request

            If there are more results to be retrieved, they will be returned in the result
            and stored in ``self.next_url``

        :param args: the arguments for the request
        :type args: dict
        """
        base = url
        for arg_name, value in args.iteritems():
            base = "{base}&{arg}={val}".format(base=base, arg=arg_name, val=value)
        return base

    def parse_results(self, results):
        """ Parses the JSON payload returned by RB and returns only the RRs

        :param results: the full response, as a parsed JSON object
        :type results: dict
        :return: the list of pending review requests
        :rtype: list
        """
        self.total = results.get('total_results', 0)
        rrs = results.get('review_requests')
        if rrs:
            # If we have exhausted the results, this will be none, otherwise it will contain the
            # URL to fetch the next batch.
            self.next_url = results.get('links').get('next', dict()).get('href')
        return rrs

    def reset(self, new_date=None):
        """ Resets this fetcher, with an optional new date to look up RRs from.

        :param new_date: optionally, specifies the date to use in the `last-updated-from` query
            argument for ReviewBoard API.
        """
        if new_date:
            self.args['last-updated-from'] = new_date
        self.next_url = self._build_url(ReviewFetcher.RB_URL, self.args)
        self.rrs = []

    def fetch_all(self, at_most=None):
        """ Retrieves all the pending Reviews from the ReviewBoard API.

        :param at_most: an optional argument, if not `None`, we retrieve at most that many RRs
        :type at_most: int
        :return: the full list of RRs since the given date; suitable to be stored in the DB
        :rtype: list
        """
        # TODO(marco): implement the at_most functionality; for now fetches all
        while self.next_url is not None:
            reviews = requests.get(self.next_url)
            if reviews.status_code == 200:
                response = reviews.json()
                for result in self.parse_results(response):
                    self.rrs.append(result)
            else:
                raise FetcherError("Could not retrieve data from ReviewBoard. "
                                   "Error was: {} - {}".format(reviews.status_code, reviews.reason))
        return self.rrs

    def store_data(self):
        for review in self.rrs:
            self.reviews.save(review)
