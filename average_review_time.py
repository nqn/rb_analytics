import sqlite3 as lite
import sys
from datetime import datetime, date, time, timedelta
import calendar


def main():
    try:
        con = lite.connect('reviews.db')
        cur = con.cursor() 

        query = "SELECT * FROM ReviewRequests WHERE status=1 order by Added"
        cur.execute(query)

        rows = cur.fetchall()
      
        users = {}

        sample_window = timedelta(days=180)

        with open('groups.txt') as f:
            content = f.readlines()
            for line in content:
                tup = line.split(',')
                if len(tup) != 2:
                    print "Warning: line '%s' cannot by parsed as user,org" % line
                else:
                    users[tup[0].rstrip()] = tup[1].rstrip()

        review_count = 0
        total_length = timedelta(0)

        org_review_count = {}
        org_total_length = {}

        for row in rows:
            def parse_timestamp(s):
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") 
            created = parse_timestamp(row[8])
            last_updated = parse_timestamp(row[9])
            submitter = row[3]
            reviewers = row[4]

            if created < (datetime.now() - sample_window):
                continue

            delta = last_updated - created

            total_length += delta
            review_count += 1

            if submitter not in users:
                print "No org for '%s'" % submitter
            else:
                org = users[submitter]
                if org not in org_review_count:
                    org_review_count[org] = 0
                    org_total_length[org] = timedelta(0)               

                org_review_count[org] += 1
                org_total_length[org] += delta

        print "Review requests over the last %s" % sample_window

        print "Average review time: %s" % (total_length / review_count)

        for org in org_review_count:
            avg = org_total_length[org] / org_review_count[org]
            print "Average review time for %s : %s" % (org, avg)

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
