#!/usr/bin/env python
#
# @copyright: AlertAvert.com (c) 2015. All rights reserved.
#
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

"""
========
Overview
========

TODO: enter overview here

configuration
-------------

TODO: enter a description of the command-line arguments

usage
-----

TODO: describe script usage here

"""

__author__ = 'Marco Massenzio'
__email__ = 'marco@alertavert.com'

import argparse
import logging
import os

LOG_FORMAT = '%(asctime)s [%(levelname)-5s] %(message)s'


def parse_args():
    """ Parse command line arguments and returns a configuration object.

    @return: the configuration object, arguments accessed via dotted notation
    @rtype: dict
    """
    parser = argparse.ArgumentParser()
    # TODO(marco): update the CLI args and the WORKDIR location
    parser.add_argument('--workdir', default=os.getenv('WORKDIR', os.getcwd()),
                        help="Root of the direcory tree for Mesos code, defaults to ")
    parser.add_argument('--logdir', default=None,
                        help="The direcory to use for the log files, if none give, uses stdout")
    parser.add_argument('--debug', '-v', default=False, action='store_true')
    return parser.parse_args()


def main(cfg):
    logging.debug("Description goes here ({})".format(cfg.workdir))
    # TODO(marco): script code goes here
    logging.info("Finished")


if __name__ == '__main__':
    config = parse_args()
    logfile = None
    if config.logdir:
        logfile = os.path.join(os.path.expanduser(config.logdir), 'messages.log')
    level = logging.INFO
    if config.debug:
        level = logging.DEBUG
    if logfile:
        print("All logging going to {} (debug info {})".format(
            logfile, 'enabled' if config.debug else 'disabled'))

    logging.basicConfig(filename=logfile, level=level, format=LOG_FORMAT,
                        datefmt="%Y-%m-%d %H:%M:%S")
    main(config)
