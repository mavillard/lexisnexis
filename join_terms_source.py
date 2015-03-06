import csv
import sys


num_files = sys.argv[1]

all_files = {}
for i in range(num_files + 1):
    filename = 'combinations_{}.csv'.format(i)
    csvfile = open(filename, 'ab')
    writer = csv.writer(
        csvfile,
        delimiter='\t',
        quotechar='"',
        quoting=csv.QUOTE_MINIMAL
    )
    all_files[i] = [filename, csvfile, writer]

index = 0
for term in open('terms.txt'):
    for source in open('sources.txt'):
        all_files[0][2].writerow([term.strip(), source.strip()])
        all_files[index % num_files + 1][2].writerow([term.strip(), source.strip()])
        index += 1
