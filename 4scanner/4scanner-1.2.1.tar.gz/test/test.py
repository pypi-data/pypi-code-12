#!/usr/bin/env python3

from scanner import scanner, download


# Test on scanner.py

# Try getting /a/ catalog as json
print("scanner.get_catalog_json test")
catalog_json = scanner.get_catalog_json("a", "4chan")

# Try getting a list of threads
print("scanner.scan_thread test")
list_of_threads = scanner.scan_thread("anime", catalog_json)
for i in list_of_threads:
    print(i)

print("scanner.folder_size_mb test")
scanner.folder_size_mb(".")

print("scanner.check_quota test")
scanner.check_quota(".", 10000)

# try writting a test log file
print("scanner.add_to_downloaded test")
scanner.add_to_downloaded("139294614", "log", ".")

# test on download.py

# Try getting a web page text
print("download.load test")
download.load("http://www.4chan.org")
