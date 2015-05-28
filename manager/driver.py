import time
import json
from policies import *
from manager import *

NUM_PROVIDERS = 2
MAX_DUP = 3

def main(arguments):
	if len(arguments) < 3:
		sys.exit('USAGE ERROR : python driver.py <num_providers> --upload --download --million --split --available --scale --low')

	providers = int(arguments[0])
	filesToCreate = providers*MAX_DUP*NUM_PROVIDERS

	upload = False
	if arguments[1] == "--download":
		upload = False
	elif arguments[1] == "--upload":
		upload = True
	else:
		sys.exit("Must provide argument --upload or --download")

	million = splitFile = available = scale = poor = False
	for i in range(2, len(arguments)):
		argument = str(arguments[i])

		print "Got argument:", argument

		if argument == "--million":
			million = True
		elif argument == "--split":
			splitFile = True
		elif argument == "--available":
			available = True
		elif argument == "--scale":
			scale = True
		elif argument == "--low":
			poor = True
		else:
			sys.exit("Must provide argument --million or --split or --available or --scale or --low")

	# data = json.load(open('profile.json', 'r'))
	# profile = data['profile']

	# create user
	user = UserPolicies()
	fileNames = []

	start1 = time.time()
	if upload:
		if splitFile:
			fileNames = user.splitFile("uploadFiles/original.png", filesToCreate)
		elif available:
			fileNames = user.availability("uploadFiles/original.png", filesToCreate)
		elif scale:
			fileNames = user.scaleImage("uploadFiles/original.png")
			fileNames = user.splitFile(fileNames[0], filesToCreate)
	else :
		for i in range(0, filesToCreate):
			newPath = "uploadFiles/download-" + str(i+1)
			name = "uploadFiles/original-" + str(i+1)
			if scale:
				name = "uploadFiles/original-scaled-" + str(i+1)
			if available:
				newPath += ".png"
				name += ".png"
			fileNames.append([newPath, name])
	end1 = time.time()

	start2 = time.time()
	# start all services
	manager = Manager(upload, providers, fileNames)
	manager.startServices()

	end2 = time.time()

	# combine files after downloading
	start3 = time.time()
	if upload != True:
		if splitFile or scale:
			user.combineSplit(fileNames, "uploadFiles/originalCombined.png")
		elif available:
			user.combineAvailable(fileNames, "uploadFiles/originalCombined.png")
	end3 = time.time()

	# print any timing information
	if upload:
		print "User Policy Finished:", (end1-start1), "(s)"
		print "Finished all Upload:", (end2-start2), "(s)"
	else:
		print "Finished all Download:", (end2-start2), "(s)"
		print "Finished Combining:", (end3-start3), "(s)"

	print "Exiting Main Thread:", (end3-start1), "(s)"

if __name__ == '__main__':
    main(sys.argv[1:])