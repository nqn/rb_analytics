import leveldb

import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from datetime import datetime, date, time, timedelta
import json

class review_request:
    def __init__(self, rr_id, added, last_updated):
        self.rr_id = rr_id
        self.added = datetime.strptime(added, "%Y-%m-%dT%H:%M:%SZ")
        self.last_updated = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%SZ")

    def duration(self):
        return self.last_updated - self.added

    def start_month(self):
        return self.added.month

    def start_year(self):
        return self.added.year

    def end_month(self):
        return self.last_updated.month

    def end_year(self):
        return self.last_updated.year

class review_aggregate:
    def __init__(self):
        pass

db = leveldb.LevelDB('./db')

min_duration = timedelta.max
max_duration = timedelta.min
sum_duration = 0
count_duration = 0

duration_q = []

review_requests = {}
for key, chunk_raw in db.RangeIter():

    rr = json.loads(chunk_raw)

    review_request_ = review_request(rr["id"], rr["time_added"], rr["last_updated"])
    review_requests[rr["id"]] = review_request_

    duration = review_request_.duration()

    sum_duration += duration.total_seconds()
    count_duration += 1

    min_duration = min(min_duration, duration)
    max_duration = max(max_duration, duration)


avg_duration = sum_duration / count_duration
# Create buckets for add and close count per month
# Compute average, max, min, stddev for durations.
print "Average review time: %s" % timedelta(seconds=avg_duration)
print "Minimum review time: %s" % min_duration
print "Maximum review time: %s" % max_duration
