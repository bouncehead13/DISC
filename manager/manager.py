import time
import threading
from baseStorage import *
from googleStorage import *
from dropboxStorage import *
from operator import itemgetter

TOLERANCE = 1.5
UPPER_TIME = 4000

class Manager():

	def __init__(self, upload, numProviders, files):
		self._upload = upload
		self._numProviders = numProviders
		self._files = files
		self._services = []

		# list of storages (Google Drive & Dropbox)
		# initializing storage logins in as well
		for i in range(1, numProviders+1):
			nameD = "Dropbox " + str(i)
			nameG = "Google " + str(i)
			self._services.append(DropboxStorage(nameD, self))
			self._services.append(GoogleStorage(nameG, self))

		# initialize their execute commands
		for i in range(0, len(files)):
			index = i % len(self._services)
			if upload:
				self._services[index].setupProcedure(upload, files[i])
			# else:
				# services[index].setupProcedure(upload, [files[i][0], files[i][1]])

	def startServices(self):
		# start all services
		for service in self._services:
			service.start()

		# wait for all threads to finish
		for service in self._services:
			service.join()

	def __migrateHelper(self, taking, minStorage, fromStorage):
		# taking the file for myself
		if taking is True and minStorage.getReaminingFiles() > 0:
			returnFile = minStorage.removeFile()
			fromStorage.addFile(returnFile)

			print "Moved from", minStorage.getName(), "to", fromStorage.getName()
		# giving the file away
		elif taking is False and fromStorage.getReaminingFiles() > 0:
			returnFile = fromStorage.removeFile()
			minStorage.addFile(returnFile)

			print "Gave from", fromStorage.getName(), "to", minStorage.getName()

	def __migrate(self, minimum, filesProcessed, fromStorage):
		minIndex = minimum[0] # ratio index
		minValue = minimum[1] # ratio value
		selfRatio = fromStorage.getRatio()
		selfProcessed = fromStorage.getFilesProcessed()

		# we are the same, nothing to do
		if self._services[minIndex] == fromStorage:
			print ">>> I am the lowest value"
			return

		# too little data, nothing to do
		if filesProcessed[minIndex] == 0 and selfProcessed == 1:
			print ">>> Too little data"
			return

		print "Tolerance:", (selfRatio - minValue)

		if filesProcessed[minIndex] == 0 and selfProcessed > 1:
			print ">>> I have more processed"
			self.__migrateHelper(True, self._services[minIndex], fromStorage)
		elif selfRatio - minValue > TOLERANCE:
			print ">>> They have better ratio"
			self.__migrateHelper(False, self._services[minIndex], fromStorage)

	def finishedFile(self, fromStorage):
		ratios = []
		filesProcessed = []
		for i in range(0, len(self._services)):
			if self._services[i].getReaminingFiles() == 0:
				ratios.append(UPPER_TIME)
			else:
				ratios.append(self._services[i].getRatio())

			filesProcessed.append(self._services[i].getFilesProcessed())

		minimum = min(enumerate(ratios), key=itemgetter(1))

		print "\n\n", filesProcessed
		print ratios

		self.__migrate(minimum, filesProcessed, fromStorage)
