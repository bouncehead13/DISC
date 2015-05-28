import os
import sys
import time
import threading
from abc import ABCMeta, abstractmethod

class BaseStorage(threading.Thread):
	__metaclass__ = ABCMeta

	def __init__(self, name, manager):
		self._name = name
		self._files = []
		self._manager = manager

		self._filesProcessed = 0
		self._previousTime = 0

		# initialize the thread
		super(BaseStorage, self).__init__()

	def setupProcedure(self, upload, arg):
		self._upload = upload
		self.addFile(arg)

	def executeProcedure(self):
		start = time.time()
		if self._upload:
			self.upload()
		else:
			self.download(self._args[0], self._args[1])
		end = time.time()

		print self._name, "Uploaded All:", (end-start), "(s)\n"

	def getName(self):
		return self._name

	def getFilesProcessed(self):
		return self._filesProcessed

	def getReaminingFiles(self):
		return len(self._files)

	def getRatio(self):
		if self._filesProcessed == 0:
			return 0

		# return 1/self._previousTime
		return self._previousTime

	def addFile(self, fileName):
		self._files.append(fileName)

	def removeFile(self):
		return self._files.pop()

	def updateManager(self, time):
		self._filesProcessed += 1
		self._previousTime = time

		self._manager.finishedFile(self)

	@abstractmethod
	def login(self):
		pass

	@abstractmethod
	def setupLogin(self):
		pass

	@abstractmethod
	def upload(self):
		pass

	@abstractmethod
	def download(self, fileLocation, remoteLocation):
		pass

	@abstractmethod
	def downloadAllFiles(self):
		pass