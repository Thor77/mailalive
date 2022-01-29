#!/usr/bin/env python3
import argparse
import sys
import time
import imaplib
import re

status_msg = {
    0: 'OK',
    1: 'WARNING',
    2: 'CRITICAL',
    3: 'UNKNOWN'
}

subject_alive_re = re.compile(r'Subject: Alive check (\d+)')


def main(host, port, username, password, warning, critical):
    # establish imap connection
    rtcode = 0
    conn = imaplib.IMAP4_SSL(host, port)
    try:
        conn.login(username, password)
    except Exception as e:
        return 2, 'login failed - {}'.format(str(e))
    conn.select()

    # fetch num of latest message
    _, msgnums = conn.sort('REVERSE ARRIVAL', 'UTF-8', 'ALL')
    extracted_msgnums = msgnums[0].decode().split(' ')
    single_msgnum = extracted_msgnums[0].encode()
    if not single_msgnum:
        return 2, 'alive message missing'

    # fetch subject of latest message
    rtcode, msg = conn.fetch(
        single_msgnum,
        '(FLAGS BODY[HEADER.FIELDS (SUBJECT)])'
    )
    if rtcode != 'OK':
        return 2, 'fetching message failed {}'.format(rtcode)

    # extract timestamp from message
    match = subject_alive_re.findall(msg[0][1].decode())
    if not match:
        return 2, 'latest message doesn\'t match alive header regex'
    age = time.time() - int(match[0])
    age_msg = 'alive message age {:.1f}s'.format(age)

    # remove all other messages
    for num in extracted_msgnums[1:]:
        conn.store(num, '+FLAGS', '\\Deleted')
    conn.expunge()

    # return corresponding status
    if age > warning:
        if age > critical:
            return 2, age_msg
        return 1, age_msg
    return 0, age_msg


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', help='imap host', required=True)
    parser.add_argument('-p', '--port', help='imap port', default=993)
    parser.add_argument(
        '-u', '--username', help='username for auth', required=True
    )
    parser.add_argument(
        '-pw', '--password', help='password for auth', required=True
    )
    parser.add_argument('-w', '--warning', help='warning threshold', type=int)
    parser.add_argument(
        '-c', '--critical', help='critical threshold', type=int
    )
    args = parser.parse_args()
    try:
        status, msg = main(
            args.host, args.port, args.username, args.password,
            args.warning, args.critical
        )
    except Exception as e:
        status, msg = (3, str(e))
    print('MAILALIVE {}: {}'.format(status_msg[status], msg))
    sys.exit(status)
