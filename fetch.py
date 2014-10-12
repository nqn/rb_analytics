import urllib2, urllib, json
import leveldb
from datetime import datetime, date, time, timedelta

chunk_size=200

def fetch_rr(start):
    rb_url = 'https://reviews.apache.org/api/review-requests/?to-groups=mesos&max-results=%d&status=submitted&start=%d' % (chunk_size, start)
    request = urllib2.Request(rb_url)
    handler = urllib2.urlopen(request)
    raw_json = handler.read()
    json_dump = json.loads(raw_json)
    return json_dump

def add_rrs(db, rrs):
    for rr in rrs["review_requests"]:
        db.Put(str(rr["id"]), json.dumps(rr))

chunk = fetch_rr(0)
total_rr = int(chunk["total_results"])
parsed = chunk_size

db = leveldb.LevelDB('./db')

add_rrs(db, chunk)

while parsed < total_rr:
    parsed += chunk_size
    chunk = fetch_rr(parsed - 1)
    add_rrs(db, chunk)
