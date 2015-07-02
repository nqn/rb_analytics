#!/usr/bin/env python
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

# Created by M. Massenzio, 2014-05-04

import argparse
import logging
import mandrill
import socket

FORMAT = '%(asctime)-15s [%(levelname)s] %(message)s'
DATE_FMT = '%m/%d/%Y %H:%M:%S'


def parse_args():
    """ Parse command line arguments and returns a configuration object
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--api-key-file', required=True,
                        help="The file containing the API key")
    parser.add_argument('-m', '--msg', required=True,
                        help="The file containing the body of the message in HTML format")
    parser.add_argument('-d', dest='dest', help="The recipient of the email")
    parser.add_argument('-s', '--subject', help='The subject for the email',
                        default='Alert from {hostname}'.format(hostname=socket.gethostname()))
    parser.add_argument('-v', '--verbose', action='store_true', help='Enables debug logging')
    return parser.parse_args()


def post_mail(to, subj, msg, **kwargs):
    """ Sends the message by posting to Mandrill API

        @param to: the recipient for the message
        @type to: str

        @param subj: the subject for the email
        @type subj: str

        @param msg: the body of the message, in plain text
        @type msg: str

        @param kwargs: other settings, compliant with Mandrill API; these may be::

            reply_to        which email to Reply-to:, if available
            from_email      the From: field to appear in the email headers
            recipient       name of the recipient

        @type kwargs: dict

        @see: https://mandrillapp.com/api/docs/
    """
    # TODO: use Jinja templates for the HTML body
    msg = {
        'from_email': kwargs.get('from_email'),
        'from_name': 'AutoAlert',
        'html': msg,
        'headers': {'Reply-To': kwargs.get('reply_to')},
        'subject': subj,
        'to': [
            {'email': to,
             'name': kwargs.get('recipient'),
             'type': 'to'
             }
        ]
    }
    mc = mandrill.Mandrill(kwargs.get('api_key'))
    try:
        res = mc.messages.send(msg, async=kwargs.get('async', False))
        if res and not res[0].get('status') == 'sent':
            logging.error('Could not send email to {to}; status: {status}, reason: {reason}'
                          .format(to=to, status=res.get('status', 'unknown'),
                                  reason=res.get('reject_reason')))
            raise RuntimeError("Could not send email: {}".format(res.get('reject_reason')))
    except mandrill.Error, e:
        # Mandrill errors are thrown as exceptions
        err_msg = 'A mandrill error occurred: {} - {}'.format(e.__class__.__name__, e)
        logging.error(err_msg)
        raise RuntimeError(err_msg)
    logging.info('Message sent to {to}'.format(to=to))


def read_api_key(filename):
    with open(filename, 'r') as key_file:
        api_key = key_file.readline().rstrip('\n')
    return api_key


def read_content(filename):
    lines = []
    with open(filename, 'r') as html_file:
        lines.append(html_file.readline())
    return ''.join(lines)


def main():
    config = parse_args()
    loglevel = logging.DEBUG if config.verbose else logging.INFO
    logging.basicConfig(format=FORMAT, datefmt=DATE_FMT, level=loglevel)
    logging.info('Mailer Auto Script starting...')
    try:
        api_key = read_api_key(config.api_key_file)
    except IOError:
        logging.error("API Key file {} could not be found".format(config.api_key_file))
        exit(1)

    kwargs = {'api_key': api_key,
              'reply_to': 'noreply@mesosphere.io',
              'recipient': 'Core Mesos Team',
              'from_email': 'noreply@mesosphere.io'
              }
    try:
        post_mail(to=config.dest, msg=read_content(config.msg), subj=config.subject, **kwargs)
    except RuntimeError, ex:
        logging.info("Could not send email: {}".format(ex.message))
        exit(1)
    except IOError:
        logging.error("Content file {} could not be found".format(config.msg))
        exit(1)

if __name__ == "__main__":
    main()
