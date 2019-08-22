#!/usr/bin/python3

# Imports
import sys
import io
import json
import re
import csv

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
print("Converting " + inFileName + " to " + ("CSV" if operation == OPERATION_TO_CSV else "Text"))
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
	inData = inData.replace("Name,Frequency,Modulation,CTCSS Tone,Delay,Locked Out,Priority\n", "")
	# Read CSV
	inData = csv.reader(io.StringIO(inData))
	inData = list(inData)

	if len(inData) != 500:
		print("ERROR: Total channels does not equal 500! (" + str(len(inData)) + ")")
		exit(1)

	# Setup output file
	outData = "[\n"

	# Generate output data
	ind = 1
	for c in inData:
		outData += "{\n"
		outData += "cmd => 'CIN',\n"
		outData += "index => '" + str(ind) + "',\n"
		if len(c[0]) > 16:
			print("ERROR: \"" + c[0] + "\" is longer than 16 characters!")
			exit(1)
		outData += "name => '" + c[0] + "',\n"
		outData += "frq => '" + c[1] + "',\n"
		if c[2] not in ["FM", "NFM", "AM", "AUTO"]:
			print("ERROR: Unknown modulation: \"" + c[2] + "\"")
			exit(1)
		outData += "mod => '" + c[2] + "',\n"
		outData += "ctcss_dcs => '" + c[3] + "',\n"
		if int(c[4]) < 0:
			print("ERROR: Delay must be >=0!")
			exit(1)
		outData += "dly => '" + c[4] + "',\n"
		if c[5] != "0" and c[5] != "1":
			print("ERROR: Lockout must be either 0 or 1!")
			exit(1)
		outData += "lout => '" + c[5] + "',\n"
		if c[6] != "0" and c[6] != "1":
			print("ERROR: Priority must be either 0 or 1!")
			exit(1)
		outData += "pri => '" + c[5] + "',\n"
		outData += "},\n"

		ind += 1
	outData += "]\n"
	
outFileName = sys.argv[2]
try:
	outFile = open(outFileName, "w")
	outFile.write(outData)
	outFile.close()
	print("Success! Wrote file to: " + outFileName)
except:
	print("ERROR: Could not write file: " + outFileName)
	exit(1)