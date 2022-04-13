import csv

ind = open('data/nazca_individual.csv', 'r')
ind = csv.reader(ind)

next(ind)

group = open('data/nazca_group.csv', 'r')
group = csv.reader(group)

headers = next(group)
headers[0] = 'id'

out = open('nazca.csv', 'w')
out = csv.writer(out)

out.writerow(headers)

i = 0
for line in ind:
    line[0] = i
    out.writerow(line)
    i += 1

for line in group:
    line[0] = i
    out.writerow(line)
    i += 1
