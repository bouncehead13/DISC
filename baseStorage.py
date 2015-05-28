import os
import sys
import time
import threading
from abc import ABCMeta, abstractmethod

class BaseStorage(threading.Thread):
    __metaclass__ = ABCMeta

    def __init__(self):
    	# init the thread
    	super(BaseStorage, self).__init__()

    def setupProcedure(self, upload, args):
		self._upload = upload
		self._args = args

    def executeProcedure(self):
    	if self._upload:
    		self.upload(self._args[0])
    	else:
			self.download(self._args[0], self._args[1])

	@abstractmethod
	def login(self):
		pass

	@abstractmethod
	def setupLogin(self):
		pass

    @abstractmethod
    def upload(self, fileLocation):
    	pass

    @abstractmethod
    def download(self, fileLocation, remoteLocation):
    	pass

    @abstractmethod
    def downloadAllFiles(self):
		pass