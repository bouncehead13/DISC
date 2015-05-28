import os
import sys
import threading
import numpy as np
from skimage import io
from skimage import transform
from moviepy.editor import VideoFileClip
from moviepy.editor import CompositeVideoClip

class UserPolicies:
	# private function
	def __saveFile(self, image, fileLocation, start, numSplits):
		imageData = []

		for row in range(0, len(image)):
			imageData.append(image[row][start::numSplits])

		newImage = np.array(imageData)
		io.imsave(fileLocation, newImage)

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

		image = io.imread(fileLocation)
		image = transform.rescale(image, 0.75)

		newPath = name + "-scaled" + extension
		io.imsave(newPath, image)

		return [newPath]

	def scaleVideo(self, fileLocation):
		(name, extension) = self.__removeExtension(fileLocation)

		clip = VideoFileClip(fileLocation)
		currentFPS = clip.fps
		# clip = clip.resize(0.75)
		final = CompositeVideoClip([clip])

		newPath = name + "-scaled" + extension
		final.write_videofile(newPath, fps=currentFPS/2, codec='libx264')

	def splitFile(self, fileLocation, numSplits):
		"""split file based on every ith index"""
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

		data = []
		lengths = []
		for i in range(0, len(fileNames)):
			# read in file
			from_file = open(fileNames[i][0], "rb")
			inputData = from_file.read()
			data.append(inputData)
			lengths.append(len(inputData))
			from_file.close()

		newData = ""
		dataLength = len(data[0])
		numProviders = len(data)
		for i in range(0, dataLength):
			for inner in range(0, numProviders):
				if i < lengths[inner]:
					newData += data[inner][i]

		to_file.write(newData)
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
			t = threading.Thread(target=self.__saveFile, args=(image, newPath, i, numSplits,))
			threads.append(t)
			t.start()			

		for t in threads:
			t.join()

		return fileNames

	def combineAvailable(self, fileNames, fileLocation):
		data = {}

		for i in range(0, len(fileNames)):
			# read in file
			image = io.imread(fileNames[i][0])
			data[i] = image

		imageData = []
		# do rows
		for i in range(0, len(data[0])):
			row = []
			# do columns
			for j in range(0, len(data[0][0])):
				for k in range(0, len(fileNames)):
					if j < len(data[k][i]):
						row.append(data[k][i][j])
			imageData.append(row)

		io.imsave(fileLocation, imageData)