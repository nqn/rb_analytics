import sqlite3 as lite
import sys
from datetime import datetime, date, time, timedelta

def parse_developer_file(filename):
    core_developers = []
    f = open(filename)
    for line in f:
        core_developers.append(line[:-1])
    f.close()
    return core_developers

class review_request:
    def __init__(self, row):
        def parse_timestamp(s):
            return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ")

        self.rr_id = row[0]
        self.summary = row[2]
        self.submitter = row[3]
        self.target = row[4]
        self.open_issues = row[6]
        self.shipits = row[7]
        self.added = parse_timestamp(row[8])

    def html_row(self):
        age = datetime.now() - self.added
        severity = ""

        # Filter out young reviews
        if age < timedelta(days=10):
            return ""

        if age > timedelta(days=30):
            severity = " style=\"color: #B20000;\""

        rr_id_link = "https://reviews.apache.org/r/" + str(self.rr_id)
        return "<tr><td%s>%s</td><td><a href=\"%s\">%s</a></td><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>" % (severity, age, rr_id_link, self.rr_id, self.summary, self.submitter, self.target, self.open_issues, self.shipits)

# Example rows:
#  <tr class="danger">
#    <td>10 days</td>
#    <td>#1235</td>
#    <td>adam-mesos</td>
#    <td>tillt</td>
#    <td>3</td>
#    <td>0</td>
#  </tr>
#  <tr class="warning">
#    <td>4 days</td>
#    <td>#1234</td>
#    <td>nnielsen</td>
#    <td>benh</td>
#    <td>0</td>
#    <td>1</td>
#  </tr>


def html_header():
    return """\
<h1>Core Reviews</h1>
<table class="table table-striped">
  <thead>
    <th>Time in review</th>
    <th>Review</th>
    <th>Summary</th>
    <th>Submitter</th>
    <th>Reviewers</th>
    <th>Outstanding issues</th>
    <th>Ship-its</th>
  </thead>
"""

def html_footer():
    return """\
</table>
"""

def main():
    core_developers = parse_developer_file('core.txt')

    f = open('mail.html', 'w')

    try:
        con = lite.connect('reviews.db')
        cur = con.cursor()

        #
        # Construct OR clauses to get RR's for developer list.
        #
        submitter_queries = []
        for developer in core_developers:
            submitter_queries.append(" submitter='%s' " % developer)
        submitter_query = ""
        if len(submitter_queries) > 0:
          submitter_query = " AND ("+ " OR ".join(submitter_queries) + ")"

        query = "SELECT * FROM ReviewRequests WHERE status=0 %s order by Added" % submitter_query
        cur.execute(query)

        rows = cur.fetchall()

        f.write(html_header())

        for row in rows:
            rr = review_request(row)
            f.write(rr.html_row())

        f.write(html_footer())
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
