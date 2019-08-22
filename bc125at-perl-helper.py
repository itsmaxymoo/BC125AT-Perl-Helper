#!/usr/bin/python3

# Imports
import sys
import json
import re

# Constants
NAME = "BC125AT-Perl Helper"
CMD = "bc125at-perl-helper"
VERSION = "1.0"
AUTHOR = "Max Loiacono"

OPERATION_TO_CSV = 0
OPERATION_TO_TXT = 1

# Basics
print(NAME + "\nVersion " + VERSION + " by " + AUTHOR + "\n")

# CliArgs handler
if len(sys.argv) != 3:
	print("ERROR: " + NAME + " requires exactly two arguments: an input file and an output file.\n")
	print("bc125at-perl text files will be converted to CSV files.")
	print("CSV files will be converted to bc125at-perl text files.\n")
	print("Example: " + CMD + " ./scanner.txt output.csv")
	print("Example: " + CMD + " ./scanner.csv output.txt")
	exit(1)
inFile = None
inFileName = sys.argv[1]
try:
	inFile = open(inFileName)
	inFile.read(4)
	inFile.seek(0)
except:
	print("ERROR: Could not read file: " + inFileName)
	exit(1)

operation = None
if inFileName.endswith('.csv'):
	operation = OPERATION_TO_TXT
else:
	operation = OPERATION_TO_CSV

# Begin conversion
print("Converting " + inFileName + " to " + "CSV" if operation == OPERATION_TO_CSV else "Text")
inData = inFile.read()
inFile.close()
outData = None

if operation == OPERATION_TO_CSV:
	# Convert text to JSON
	inData = re.sub("(\s(?=[a-z_]* => '))|(\s(?==> '))", "\"", inData)
	inData = inData.replace("=> '", ": '")
	inData = inData.replace("'", "\"")
	inData = inData.replace("\"pri\": \"0\",", "\"pri\": \"0\"")
	inData = inData.replace("\"pri\": \"1\",", "\"pri\": \"1\"")
	inData = re.sub("},\s*]", "}]", inData)

	try:
		inData = json.loads(inData)
	except:
		print("ERROR: Could not parse file. Did you modify it?")
		exit(1)

	# Write CSV
	outData = "Name,Frequency,Modulation,CTCSS Tone,Delay,Locked Out,Priority\n"
	try:
		for c in inData:
			outData += "\"" + c["name"] + "\"" + "," + "\"" + c["frq"] + "\"" + "," + "\"" + c["mod"] + "\"" + "," + "\"" + c["ctcss_dcs"] + "\"" + "," + "\"" + c["dly"] + "\"" + "," + "\"" + c["lout"] + "\"" + "," + "\"" + c["pri"] + "\"" + "\n"
	except:
		print("ERROR: Could not convert file. Did you modify it?")
		exit(1)
else:
	# Convert CSV to TXT
	print("TODO")
	
outFileName = sys.argv[2]
try:
	outFile = open(outFileName, "w")
	outFile.write(outData)
	outFile.close()
	print("Success! Wrote file to: " + outFileName)
except:
	print("ERROR: Could not write file: " + outFileName)
	exit(1)