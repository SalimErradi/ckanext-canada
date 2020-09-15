#!/usr/bin/env python3
"""
Gets broken links from url_database.csv and fetches corresponding metadata from
od-do-canada.jsonl.
Gets content-type of active links and compares to format of metadata.

Arguments:
fileinput - metadata file to be read ('od-do-canada.jsonl')
url_database - url_database report generated by url_database.py

Output:
broken_links_report.csv
incorrect_file_types_report.csv
"""
import sys
import fileinput
import json
import csv
import codecs

metadata = sys.argv[1]
url_database = sys.argv[2]

broken_links = {}
file_types = {}
file_sizes = {}

with open(url_database, "rb") as csvfile:
    reader = csv.reader(csvfile)
    next(reader)
    for row in reader:
        url = row[0]
        date = row[1]
        response = row[2]
        content_type= row[3]
        content_length = row[4]
        if 'N/A' in response:
            broken_links[url] = [date, response]
        else:
            response_int = int(response.split('[')[1].split(']')[0])
            if response_int == 404 or response_int > 405:
                broken_links[url] = [date, response]
        file_sizes[url] = [date, content_length]


# For each resource in each dataset
# check if url is in broken links of url_database
# Get metadata
print("Matching URLs with Metadata")
broken_links_data = []
file_length_data = []
broken_links_flag = 0
file_length_flag = 0


for dataset in open(metadata):
    line = json.loads(dataset)
    resources = line["resources"]
    for l, x in enumerate(resources):
        file_url = resources[l]["url"]
        if file_url in broken_links:
            data = broken_links.pop(file_url)
            broken_links_data.append(
                [file_url.strip(), data[0].strip(), data[1].strip(),
                 line["organization"]["title"].strip(),
                 line["organization"]["name"].strip(),
                 line["title"].strip(), line["id"].strip(),
                 resources[l]["name_translated"]["en"].strip(), resources[l]["id"].strip()])
            if len(broken_links) == 0:
                broken_links_flag = 1
            continue
        if file_url in file_sizes:
            data = file_sizes.pop(file_url)
            if not resources[l].has_key("size") or resources[l]["size"] != data[1]:
                file_length_data.append(
                    [file_url, data[0], line["organization"]["title"],
                    line["title"], line["id"], resources[l]["id"],
                    data[1]])
                if len(file_sizes) == 0:
                    file_length_flag = 1
            continue

    if broken_links_flag == 1 and file_length_flag == 1:
        # stop searching when all broken links and incorrect filetypes are found
        break


print("Exporting to csv...")
# Export tp CSV
with open('reports/broken_links_report.csv', "w") as f:
    writer = csv.writer(f)
    writer.writerow(("url", "date", "response", "organization_name", "org_code", "title", "uuid", "resource_name", "resource_id"))
    for row in broken_links_data:
        try:
            row = [str(x.encode('utf-8')) for x in row]
            writer.writerow(row)
        except:
            row = [str(x.encode('utf-8')) for x in row]
            print row
            sys.exit(1)
f.close()

with open('reports/incorrect_file_size_report.csv', "w") as f:
    writer = csv.writer(f)
    writer.writerow(("url", "date", "organization", "title", "uuid", "resource_id",
                     "found_file_size"))
    for row in file_length_data:
        row = [str(x.encode('utf-8')) for x in row]
        writer.writerow(row)
f.close()
print("Done.")

