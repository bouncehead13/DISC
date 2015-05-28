import os
import sys
import time
import math
import threading
import subprocess
import numpy as np
from PIL import Image
from skimage import io
from skimage import transform
from moviepy.editor import VideoFileClip
from moviepy.editor import CompositeVideoClip

class UserPolicies:
	def __init__(self):
		self.COMPRESSION = 4

	# save availability files
	def __splitFile(self, image, fileLocation, start, numSplits):
		column = image[0][start::numSplits]
		imageData = np.empty([len(image), len(column), 3], np.uint8)
		imageData[0] = column

		for row in range(1, len(image)):
			imageData[row] = image[row][start::numSplits]

		# io.imsave(fileLocation, imageData)
		newImage = Image.fromarray(imageData)
		newImage.save(fileLocation, compress_level=self.COMPRESSION)

	# save file for availability
	def __saveFile(self, imageData, startIndex, fileName, totalFiles):
		image = io.imread(fileName)
		image = np.transpose(image, axes=(1, 0, 2))
		numRows = len(image)
		imageRow = startIndex

		for row in range(0, numRows):
			imageData[imageRow] = image[row]
			imageRow += totalFiles

	# save file for security
	def __saveSplitFile(self, outputData, fileData, startIndex, totalFiles):
		outputData[startIndex::totalFiles] = fileData


	# private function
	def __removeExtension(self, fileLocation):
		"""return tuple with filename and file extension"""
		index = fileLocation.rfind('.')
		name = fileLocation[0:index]
		extension = fileLocation[index:]
		return (name, extension)

	def scaleImage(self, fileLocation):
		"""scales the image to a lower resolution and save space"""
		(name, extension) = self.__removeExtension(fileLocation)

		# image = io.imread(fileLocation)
		# image = transform.rescale(image, 0.75)
		image = Image.open(fileLocation)
		size_x = int(image.size[0] * 0.75)
		size_y = int(image.size[1] * 0.75)
		image = image.resize((size_x, size_y))
		newPath = name + "-scaled" + extension

		# io.imsave(newPath, image)
		image.save(newPath, compress_level=self.COMPRESSION)

		return [newPath]

	def scaleVideo(self, fileLocation):
		(name, extension) = self.__removeExtension(fileLocation)
		handBrake = '~/Documents/RPI/Research/DISC/HandBrakeCLI'

		clip = VideoFileClip(fileLocation)
		currentFPS = int(math.ceil(clip.fps))
		# clip = clip.resize(0.75)
		# final = CompositeVideoClip([clip])

		newPath = name + "-scaled" + extension
		# final.write_videofile(newPath, fps=currentFPS/2, codec='libx264')
		command = handBrake + ' -i ' + fileLocation + ' -o ' + newPath + ' -e x264 -r ' + str(currentFPS/2)
		os.system(command)

		return [newPath]

	def splitFile(self, fileLocation, numSplits):
		"""split file based on every ith index"""

		if numSplits == 1:
			return [fileLocation]

		(name, extension) = self.__removeExtension(fileLocation)

		# read in file
		from_file = open(fileLocation, "rb")
		data = from_file.read()
		from_file.close()

		# create all files
		fileNames = []
		files = []
		for i in range(0, numSplits):
			newPath = name + "-" + str(i+1)
			fileNames.append(newPath)
			newFile = open(newPath, "wb")
			newFile.write(data[i::numSplits])
			newFile.close()

		return fileNames

	def combineSplit(self, fileNames, fileLocation):
		to_file = open(fileLocation, "wb")

		numProviders = len(fileNames)
		counter = 0
		totalLength = 0
		data = []

		for i in range(0, numProviders):
			# read in file
			from_file = open(fileNames[i][0], "rb")
			inputData = from_file.read()
			totalLength += len(inputData)
			data.append(inputData)

		outputData = [''] * totalLength
		threads = []
		for i in range(0, numProviders):
			t = threading.Thread(target=self.__saveSplitFile, args=(outputData, data[i], i, numProviders,))
			threads.append(t)
			t.start()			

		for t in threads:
			t.join()

		outputData = ''.join(outputData)
		to_file.write(outputData)
		to_file.close()

	def availability(self, fileLocation, numSplits):
		(name, extension) = self.__removeExtension(fileLocation)

		# read in file
		image = io.imread(fileLocation)

		# create all fileNames
		fileNames = []
		threads = []

		for i in range(0, numSplits):
			newPath = name + "-" + str(i+1) + extension
			fileNames.append(newPath)
			t = threading.Thread(target=self.__splitFile, args=(image, newPath, i, numSplits,))
			threads.append(t)
			t.start()			

		for t in threads:
			t.join()

		return fileNames

	def __checkExistingFile(self, fileName, currentIndex, fileNames):
		# find next closest file in the list of files
		numFiles = len(fileNames)
		if os.path.exists(fileName):
			return fileName
		else:
			for i in range(currentIndex, numFiles):
				return self.__checkExistingFile(fileNames[i][0], i+1, fileNames)

	def combineAvailable(self, fileNames, fileLocation):
		threads = []
		fileName = self.__checkExistingFile(fileNames[0][0], 1, fileNames)

		image = io.imread(fileName)
		numRows = len(image)
		numColumns = len(image[0])
		numFiles = len(fileNames)
		totalColumns = numColumns * numFiles

		# create transpose image
		imageData = np.empty([totalColumns, numRows, 3], np.uint8)

		t1 = time.time()
		for i in range(0, numFiles):
			fileName = self.__checkExistingFile(fileNames[i][0], i+1, fileNames)

			t = threading.Thread(target=self.__saveFile, args=(imageData, i, fileName, numFiles,))
			threads.append(t)
			t.start()

		for t in threads:
			t.join()

		# transpose image
		imageData = np.transpose(imageData, axes=(1, 0, 2))
		t2 = time.time()

		# io.imsave(fileLocation, imageData)
		newImage = Image.fromarray(imageData)
		newImage.save(fileLocation, compress_level=self.COMPRESSION)
		t3 = time.time()

		print "Array:", (t2-t1)
		print " Save:", (t3-t2)