# -*- coding: utf-8 -*-
"""BD HW3 S2.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1rwL9W-_QaJSKZvtGV4cNi0198RDrbF8X

# Step 2 (Web Server Log File Analysis)

## Environment Setup

### Install requirements
"""

!apt-get install openjdk-8-jdk-headless -qq > /dev/null
!wget -q http://archive.apache.org/dist/spark/spark-3.1.1/spark-3.1.1-bin-hadoop3.2.tgz
!tar xf spark-3.1.1-bin-hadoop3.2.tgz
!pip install -q findspark

"""### Set environment variables"""

import os
os.environ["JAVA_HOME"] = "/usr/lib/jvm/java-8-openjdk-amd64"
os.environ["SPARK_HOME"] = "/content/spark-3.1.1-bin-hadoop3.2"

"""### Import libraries"""

import findspark
findspark.init()
from pyspark.sql import SparkSession
spark = SparkSession.builder.master("local[*]").getOrCreate()
spark.conf.set("spark.sql.repl.eagerEval.enabled", True) # Property used to format output tables better
spark

import re
import datetime
import matplotlib.pyplot as plt
from google.colab import drive
from pyspark.sql import Row

"""### Mount drive for log file"""

drive.mount('/content/drive')

"""### Get spark context"""

sc = spark.sparkContext

"""## Get Data Ready

### Extract fields from data funciton
"""

MONTH_NUMBER_MAPPING = {'Jan': 1, 'Feb': 2, 'Mar':3, 'Apr':4, 'May':5, 'Jun':6, 'Jul':7,
                        'Aug':8,  'Sep': 9, 'Oct':10, 'Nov': 11, 'Dec': 12}
LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+) (\S+)" (\d{3}) (\S+)'


def parse_log_time(time):
    return datetime.datetime(int(time[7:11]),
                             MONTH_NUMBER_MAPPING[time[3:6]],
                             int(time[0:2]),
                             int(time[12:14]),
                             int(time[15:17]),
                             int(time[18:20]))


def parse_single_log(log):
    match = re.search(LOG_PATTERN, log)
    if match is None:
        return (log, 0)
    size_field = match.group(9)
    if size_field == '-':
        size = 0
    else:
        size = int(match.group(9))
    return (Row(
        host          = match.group(1),
        client_identd = match.group(2),
        user_id       = match.group(3),
        date_time     = parse_log_time(match.group(4)),
        method        = match.group(5),
        endpoint      = match.group(6),
        protocol      = match.group(7),
        response_code = int(match.group(8)),
        content_size  = size
    ), 1)

"""### Read web server log file"""

log_file_path = '/content/drive/MyDrive/BD Logs/Log'
pure_logs = sc.textFile(log_file_path)
print("First line of log:")
print(pure_logs.first())

"""### Extract fields from data"""

parsed_logs = (pure_logs
              .map(parse_single_log))
print("First parsed log:")
print(parsed_logs.first())
print("Paresed Logs Count: {}".format(parsed_logs.count()))

successful_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 1)
                     .map(lambda record: record[0]))
print("First successfully parsed:")
print(successful_parsed.first())
print("Successful Parse Count: {}".format(successful_parsed.count()))

failed_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 0)
                     .map(lambda record: record[0]))
print("First fail parsed:")
print(failed_parsed.first())
print("Failed Parse Count: {}".format(failed_parsed.count()))

"""### Improve log pattern"""

LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)" (\d{3}) (\S+)'
parsed_logs = (pure_logs
              .map(parse_single_log))
print("First parsed log:")
print(parsed_logs.first())
print("Paresed Logs Count: {}".format(parsed_logs.count()))

successful_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 1)
                     .map(lambda record: record[0]))
print("First successfully parsed:")
print(successful_parsed.first())
print("Successful Parse Count: {}".format(successful_parsed.count()))

failed_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 0)
                     .map(lambda record: record[0]))
print("First fail parsed:")
print(failed_parsed.first())
print("Failed Parse Count: {}".format(failed_parsed.count()))

"""### More improvement for log pattern :D"""

LOG_PATTERN = '^(\S+) (\S+) (\S+) \[([\w:/]+\s[+\-]\d{4})\] "(\S+) (\S+)\s*(\S*)\s*" (\d{3}) (\S+)'
parsed_logs = (pure_logs
              .map(parse_single_log))
print("First parsed log:")
print(parsed_logs.first())
print("Paresed Logs Count: {}".format(parsed_logs.count()))

successful_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 1)
                     .map(lambda record: record[0])
                     .cache())
print("First successfully parsed:")
print(successful_parsed.first())
print("Successful Parse Count: {}".format(successful_parsed.count()))

failed_parsed = (parsed_logs
                     .filter(lambda record: record[1] == 0)
                     .map(lambda record: record[0])
                     .cache())
print("First 10 fail parsed:")
print(failed_parsed.take(10))
print("Failed Parse Count: {}".format(failed_parsed.count()))

"""## Part 1"""

unique_hosts = (successful_parsed
                .map(lambda log: log.host)
                .distinct())
print("First 5 hosts:")
print(unique_hosts.take(5))
unique_hosts_count = unique_hosts.count()
print("Unique hosts count: {}".format(unique_hosts_count))

"""## Part 2

### Average daily requests for each day
"""

daily_hosts = (successful_parsed
               .map(lambda log: (log.date_time.date(), log.host))
               .groupByKey()
               .sortByKey()
               .cache())
print("First 5 daily hosts:")
print(daily_hosts.take(5))

average_daily_requests = (daily_hosts
                          .map(lambda dh: (dh[0], len(dh[1])/len(set(dh[1])))))
print("Daily average reuests on each host:")
print(average_daily_requests.collect())

"""### Average request on each host"""

host_requests = (successful_parsed
               .map(lambda log: (log.host, log.date_time.date()))
               .groupByKey()
               .cache())
print("First 5 host request dates:")
print(host_requests.take(5))

average_host_daily_requests = (host_requests
                              .map(lambda dh: (dh[0], len(dh[1])/len(set(dh[1])))))
print("Daily average reuests per host:")
print(average_host_daily_requests.collect())

"""### Number of daily request per host"""

daily_requests = (successful_parsed
               .map(lambda log: ((log.host, log.date_time.date()), 1))
               .reduceByKey(lambda a, b: a + b))
print("First 5 daily request dates:")
print(daily_requests.take(5))

"""### Calculate daily average"""

average_daily = (daily_requests
               .map(lambda record: (record[0][0], record[1]))
               .groupByKey()
               .mapValues(lambda reqs: sum(reqs) / len(reqs)))
print("First 5 average daily requests:")
print(average_daily.collect())

"""## Part 3"""

gif_request = (successful_parsed
               .filter(lambda log: log.endpoint.endswith('.gif')))
print("First 5 gif requests:")
print(gif_request.take(5))
gif_requests_count = gif_request.count()
print("GIF requests count: {}".format(gif_requests_count))

"""## Part 4

### Most requested domains
"""

IP_STARTS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
domains_request_count = (successful_parsed
                         .filter(lambda log: log.endpoint[0] not in IP_STARTS)
                         .map(lambda log: (log.endpoint, 1))
                         .reduceByKey(lambda a, b : a + b)
                         .cache())

top_domains = domains_request_count.takeOrdered(10, lambda record: -1 * record[1])
print("Top 10 domains:")
print(top_domains)

more_than_three_domains = (domains_request_count
                           .filter(lambda record: record[1]>3))
print("More than 3 requests domains:")
more_three_count = more_than_three_domains.count()
print(more_than_three_domains.takeOrdered(more_three_count, lambda record: -1 * record[1]))

"""### Most requested domains in each day"""

IP_STARTS = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
daily_domain_requests = (successful_parsed
                         .filter(lambda log: log.endpoint[0] not in IP_STARTS)
                         .map(lambda log: ((log.date_time.date(), log.endpoint), 1))
                         .reduceByKey(lambda a, b : a + b)                         
                         .cache())

top_domains = daily_domain_requests.takeOrdered(10, lambda record: -1 * record[1])
print("Top 10 domains:")
print(top_domains)

daily_top_domain = (daily_domain_requests
                    .map(lambda log: (log[0][0], (log[1], log[0][1])))
                    .groupByKey()
                    .map(lambda x : (x[0], sorted(list(x[1]), reverse=True)))
                    .cache())

print(daily_top_domain.take(5))

top_domains = (daily_top_domain
               .map(lambda day_record: (day_record[0], day_record[1][0])))

print("Daily top domain:")
top_domains.collect()

"""## Part 5

### Find Error Logs
"""

http_errors = (successful_parsed
               .filter(lambda log: log.response_code!=200)
               .map(lambda log: (log.response_code, 1))
               .cache())
print("First 5 errors:")
print(http_errors.take(5))

"""### Count errors"""

error_counts = (http_errors
                .reduceByKey(lambda a, b: a + b))
print("Error counts:")
print(error_counts.collect())

"""### Draw status code frequency bar plot"""

status_codes = []
code_frequencies = []
for error, count in error_counts.collect():
  status_codes.append(str(error))
  code_frequencies.append(count)

plt.title("Error codes frequencies")
plt.xlabel("Error codes")
plt.ylabel("Count")
plt.bar(status_codes, code_frequencies)
plt.show()