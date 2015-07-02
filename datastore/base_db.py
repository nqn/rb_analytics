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

"""Base classes and utilities for all DB abstraction classes/modules.

The exceptions are split into 2 categories - errors due to client (bad) data and internal
database errors.

Client errors raise exceptions subclassed from SlNotification, errors we don't expect are
derived from AdminError.

The distinction will bubble back up to the API responses - exceptions derived from AdminError
will cause a traceback to be logged and a 500 error to be returned.

"""


import abc
import contextlib
import logging

import pymongo
import pymongo.errors


LATEST = -1


class DBError(Exception):
    pass


class DBUnsupportedTypeError(DBError):
    pass


class DBUninitializedError(DBError):
    pass


class DBDuplicateKeyError(DBError):
    pass


class DBNoRecordFound(DBError):
    pass


class DBIllegalRequestError(DBError):
    """Raised when a request to the DB layer is either incomplete or disallowed"""
    pass


class MongoDB(object):
    """This class abstracts the actual application logic from the underlying database.  There is
    somewhat of an underlying assumption that the database is document based.

    It allows a basic connection to localhost or a replica set, authenticated or unauthenticated
    as set in the sentinel properties file."""

    __metaclass__ = abc.ABCMeta

    def __init__(self, conf, max_pool_size=10, refresh=False, safe=True):
        """ Initializes the Database and prepares the client for queries.

        :param conf: a dict-like object that has the following properties to configure the connection::

                db.name
                dg.host
                db.port

            and, optionally, a `db.replicaset` field (for the name of the ``ReplicaSet``).
        :type conf: dict
        :param max_pool_size:
        :param refresh:
        :param safe:
        :return:
        """
        self._log = logging.getLogger(self.__class__.__name__)
        self.db_name = conf['db.name']
        self.db_host = conf['db.host']
        self.db_port = conf['db.port']
        self._log.info('Creating a database connection on %s:%d/%s',
                self.db_host, self.db_port, self.db_name)
        # the pymongo.ReplicaSetConnection will connect to the entire replica set
        # in case one server fails, another will take the connection.
        if 'db.replicaset' in conf:
            raise NotImplementedError("ReplicaSet are not supported yet in rb-analytics")
            # self.connection = pymongo.replica_set_connection.ReplicaSetConnection(
            #     host=self.db_host,
            #     port=self.db_port, max_pool_size=max_pool_size,
            #     replicaSet=conf['db.replicaset'],
            #     safe=safe)
        else:
            client = pymongo.MongoClient(host=self.db_host, port=self.db_port)
            self.db = client[self.db_name]
        # Authenticates to the database: this is optional for standalone instances,
        # and mandatory for replica sets.
        if 'db.user' in conf:
            self._log.debug('Authenticating %s user onto database %s', conf['db.user'],
                self.db_name)
            try:
                self.db.authenticate(name=conf['db.user'], password=conf['db.passwd'])
            except pymongo.errors.PyMongoError as e:
                self._log.error('Unable to authenticate to backend database server %s. %s',
                    self.db_host, e)
                raise DBError('Failed to connect to DB')
        self._ensure_indexes()

    @abc.abstractmethod
    def _ensure_indexes(self):
        """Override this method to provide indexes on the collections used.

        For example:

            with self.context('users') as col:
                col.ensure_index('user_id')
                col.ensure_index([('subscriber_id', pymongo.ASCENDING),
                                  ('environment', pymongo.ASCENDING)])
        """
        pass

    @contextlib.contextmanager
    def context(self, collection_name):
        """A simple context manager which wraps pymongo requests.  This just makes sure that we
        release connections back into the pool.

        @param collection_name: The MongoDB collection name.

        @yields: A MongoDB collection.
        """
        if not self.db:
            raise DBUninitializedError('The MongoDB must be instantiated before it can be used.')
        collection = self.db[collection_name]
        yield collection

    def drop_collection(self, collection_name):
        """Drops the named collection

        @param collection_name: the collection to drop
        """
        if not self.db:
            raise DBUninitializedError('The MongoDB must be instantiated before it can be used.')
        try:
            self._log.warn('Dropping Collection %s', collection_name)
            self.db.drop_collection(collection_name)
        except pymongo.errors.PyMongoError, ex:
            self._log.error('Could not drop collection {}. Reason was: {}'.format(
                collection_name, ex.message))

    @abc.abstractmethod
    def drop(self):
        """ Drops the collection that is managed by the concrete class.

            Every collection class must implement this method by calling
            `MongoDb.drop_collection(collection_name)` where `collection_name` is the name of the
            managed collection
        """
        pass
