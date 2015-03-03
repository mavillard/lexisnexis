import csv


csvfile = open('combinations.csv', 'ab')
writer = csv.writer(
    csvfile,
    delimiter='\t',
    quotechar='"',
    quoting=csv.QUOTE_MINIMAL
)

for term in open('t.txt'):
    for source in open('s.txt'):
        writer.writerow([term.strip(), source.strip()])
