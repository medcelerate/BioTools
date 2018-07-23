#psrser and total splicing calculator for Majiq
import csv, sys

firstline = True

with open(sys.argv[1]) as tsv:
	for line in csv.reader(tsv, dialect="excel-tab"):
		if firstline:    #skip first line
			print("\t".join(line))
			firstline = False
			continue
		E = line[3].split(';')
		total = 0
		for val in E:
			total = total + abs(float(val))
		line.append(str(total))
		sts = "\t".join(line)
		print(sts)
	#	exit()
