import sqlite3 as lite
import sys
import operator
from datetime import datetime, date, time, timedelta

def time_filter(time, max_age):
       age = datetime.now() - time

       if age < timedelta(days=max_age):
           return True

       return False

class review:
    def __init__(self, row):
        def parse_timestamp(s):
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

        self.review_id = row[0]
        self.submitter = row[2]
        self.shipit = row[3]
        self.added = parse_timestamp(row[4])

def table_header():
    return """\
<table>
  <thead>
    <th>Submitter</th>
    <th>Reviews</th>
  </thead>
"""

def table_footer():
    return """\
</table>
"""


def reviews_from(reviews, days):
    ret = {}
    for r in reviews:
        if time_filter(r.added, days) == True:
            if r.submitter in ret:
                ret[r.submitter] += 1
            else:
                ret[r.submitter] = 1

    return ret


def format_users(users):
    ret = table_header()
    sorted_keys = sorted(users.items(), key=operator.itemgetter(1), reverse=True)
    for user in sorted_keys:
        user_link = "https://reviews.apache.org/users/" + user[0]
        ret += "<tr><td><a href=\"%s\">%s</a></td><td>%s</td></tr>" % (user_link, user[0], user[1])
    ret += table_footer()
    return ret

def main():
    f = open('mail_reviews.html', 'w')

    try:
        con = lite.connect('reviews.db')
        cur = con.cursor()

        query = "SELECT * FROM Reviews"
        cur.execute(query)

        rows = cur.fetchall()

        reviews = []
        for row in rows:
            reviews.append(review(row))

        # Reviews from last 7 days
        f.write("<h1>Reviews given last 7 days</h1>")
        f.write(format_users(reviews_from(reviews, 7)))

        # Reviews from last 30 days
        f.write("<h1>Reviews given last 30 days</h1>")
        f.write(format_users(reviews_from(reviews, 30)))

        # Total reviews per week from last 6 months
        f.close()

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
