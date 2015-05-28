import time
import json
import threading
from dropboxStorage import *
from googleStorage import *
from policies import *

def main(arguments):
	if len(arguments) < 3:
		sys.exit('USAGE ERROR : python driver.py <num_providers> --upload --download --million --split --available --scale --low')

	numProviders = int(arguments[0])

	upload = False
	movie = False
	if arguments[1] == "--download":
		upload = False
	elif arguments[1] == "--upload":
		upload = True
	else:
		sys.exit("Must provide argument --upload or --download")

	startIndex = 2
	if arguments[2] == "--movie":
		startIndex = 3
		movie = True

	million = splitFile = available = scale = poor = False
	for i in range(startIndex, len(arguments)):
		argument = str(arguments[i])

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

	# list of storages (Google Drive & Dropbox)
	# initializing storage logins in as well
	services = []
	for i in range(1, numProviders+1):
		nameD = "Dropbox " + str(i)
		nameG = "Google " + str(i)
		services.append(DropboxStorage(nameD))
		services.append(GoogleStorage(nameG))

	# create user
	user = UserPolicies()
	fileNames = []

	start1 = time.time()
	if upload:
		if splitFile:
			fileNames = user.splitFile("uploadFiles/original.png", len(services))
		elif available:
			fileNames = user.availability("uploadFiles/original.png", len(services))
		elif scale:
			if movie:
				fileNames = user.scaleVideo("uploadFiles/100.mov")
			else:
				fileNames = user.scaleImage("uploadFiles/original.png")
				fileNames = user.splitFile(fileNames[0], len(services))
	else :
		for i in range(0, len(services)):
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
	for i in range(0, len(services)):
		if upload:
			services[i].setupProcedure(upload, [fileNames[i]])
		else:
			services[i].setupProcedure(upload, [fileNames[i][0], fileNames[i][1]])
		services[i].start()

	# wait for all threads to finish
	for service in services:
		service.join()

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