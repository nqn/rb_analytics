import urllib2, urllib, json
from datetime import datetime, date, time, timedelta
import sys

import sqlite3 as lite

pending_str = "pending"
pending_int = 0

submitted_str = "submitted"
submitted_int = 1

discarded_str = "discarded"
discarded_int = 2

def fetch_rrs_chunk(start, chunk_size, status):
    # TODO(nnielsen): Get submitted review requests too.
    rb_url = 'https://reviews.apache.org/api/review-requests/?to-groups=mesos&status=%s&max-results=%d&start=%d' % (status, chunk_size, start)
    request = urllib2.Request(rb_url)
    handler = urllib2.urlopen(request)
    raw_json = handler.read()
    json_dump = json.loads(raw_json)
    return json_dump

def add_rrs(cur, rrs):
    for rr in rrs["review_requests"]:
        rr_id = rr["id"]
        rr_added = rr["time_added"]
        rr_submitter = rr["links"]["submitter"]["title"]
        rr_open_issues = rr["issue_open_count"]
        rr_summary = rr["summary"]
        rr_shipits = rr["ship_it_count"]
        rr_last_updated = rr["last_updated"]

        targets = []
        for t in rr["target_people"]:
            targets.append(t["title"])
        rr_target = ",".join(targets)

        rr_status = 0
        if rr["status"] == pending_str:
            rr_status = pending_int
        elif rr["status"] == submitted_str:
            rr_status = submitted_int
        elif rr["status"] == discarded_str:
            rr_status = discarded_int
        else:
            print "Warning: didn't encode state: '%s' correctly" % rr["status"]

        cur.execute("INSERT INTO ReviewRequests(Id, Submitter, TargetPeople, Added, OpenIssues, Summary, ShipIts, Status, LastUpdated) VALUES (?,?,?,?,?,?,?,?,?)" , (rr_id, rr_submitter, rr_target, rr_added, rr_open_issues, rr_summary, rr_shipits, rr_status, rr_last_updated))

def fetch_rrs(cur, status):
    chunk_size = 200
    chunk = fetch_rrs_chunk(0, chunk_size, status)
    total_rr = int(chunk["total_results"])
    parsed = chunk_size

    print "Fetching %s review requests (total: %d)" % (status, total_rr)

    add_rrs(cur, chunk)
    while parsed < total_rr:
        parsed += chunk_size
        chunk = fetch_rrs_chunk(parsed - 1, chunk_size, status)
        add_rrs(cur, chunk)


def main():
    try:
        con = lite.connect('reviews.db')
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS ReviewRequests")
        cur.execute("CREATE TABLE ReviewRequests(Id INTEGER PRIMARY KEY, Status INTEGER, Summary TEXT, Submitter TEXT, TargetPeople TEXT, DependsOn TEXT, OpenIssues INTEGER, ShipIts INTEGER, Added TEXT, LastUpdated TEXT)")

        if len(sys.argv) > 1 and sys.argv[1] == "full":
            print "Fetching submitted reviews"
            fetch_rrs(cur, 'all')
        else:
            fetch_rrs(cur, pending_str)

        con.commit()

    except lite.Error, e:

        if con:
            con.rollback()

        print "Error %s:" % e.args[0]
        sys.exit(1)

    finally:
        if con:
            con.close()

if __name__ == "__main__":
    main()
