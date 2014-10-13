import sqlite3 as lite
import sys
from datetime import datetime, date, time, timedelta
import calendar

from matplotlib import pyplot as plt

def main():
    try:
        con = lite.connect('reviews.db')
        cur = con.cursor() 

        query = "SELECT * FROM ReviewRequests WHERE status=1 order by Added"
        cur.execute(query)

        rows = cur.fetchall()
      
        monthly_submitted = {}
        monthly_added = {}

        for row in rows:
            def parse_timestamp(s):
                return datetime.strptime(s, "%Y-%m-%dT%H:%M:%SZ") 
            last_updated = parse_timestamp(row[9])

            if last_updated.year not in monthly_submitted:
                monthly_submitted[last_updated.year] = {}

            if last_updated.month not in monthly_submitted[last_updated.year]:
                monthly_submitted[last_updated.year][last_updated.month] = 1
            else:
                monthly_submitted[last_updated.year][last_updated.month] += 1

        labels = []
        x = []
        for i in range(1, 13):
          labels.append(calendar.month_name[i])
          x.append(i)
        
        plt.xticks(x, labels, rotation='vertical')

        for year in monthly_submitted:
            x = []
            y = []
            yr = monthly_submitted[year]
            for month in yr:
              m = yr[month]

              x.append(month)
              y.append(m)

            line, = plt.plot(x, y)
            line.set_label('Submitted ' + str(year))

        plt.ylabel("Patches")

        plt.margins(0.2)
        plt.subplots_adjust(bottom=0.20)
        plt.legend()
        plt.savefig("monthly.png")

        

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
