import urllib2
import json
import sys
import sqlite3 as lite


# TODO(nnielsen): Centralize these constants.
pending_str = "pending"
pending_int = 0

submitted_str = "submitted"
submitted_int = 1


def fetch_reviews(review_id):
    rb_url = 'https://reviews.apache.org/api/review-requests/%d/reviews/' % (review_id)
    request = urllib2.Request(rb_url)
    handler = urllib2.urlopen(request)
    raw_json = handler.read()
    json_dump = json.loads(raw_json)
    return json_dump


def add_reviews(cur):
    query = "SELECT Id FROM ReviewRequests"
    cur.execute(query)

    rows = cur.fetchall()

    total = len(rows)
    current = 0
    for row in rows:
        current += 1
        print "Processing %d/%d..." % (current, total)
        review_jsons = fetch_reviews(row)
        for review_json in review_jsons["reviews"]:
            review_id = review_json["id"]
            review_submitter = review_json["links"]["user"]["title"]
            # review_summary = review_json["body_top"]
            review_shipit = 0
            if review_json["ship_it"] == True:
                review_shipit = 1
            review_added = review_json["timestamp"]
            cur.execute("INSERT INTO Reviews(Id, Submitter, ShipIt, Added) VALUES (?,?,?,?)",
                        (review_id, review_submitter, review_shipit, review_added))


def main():
    try:
        con = lite.connect('reviews.db')
        cur = con.cursor()

        cur.execute("DROP TABLE IF EXISTS Reviews")
        cur.execute(
            "CREATE TABLE Reviews(Id INTEGER PRIMARY KEY, Summary TEXT, Submitter TEXT, ShipIt INTEGER, Added TEXT)")
        # TODO(nnielsen): Capture diff reviews and replies.

        add_reviews(cur)

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
