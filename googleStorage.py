import httplib2

from baseStorage import *
from apiclient import errors
from apiclient.discovery import build
from apiclient.http import MediaFileUpload
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage

class GoogleStorage(BaseStorage):
	def __init__(self, name):
		super(GoogleStorage, self).__init__()
		self._name = name

	def __getName(self, fileLocation):
		name = fileLocation.split('/')[1]
		name = name.split('.')[0]

		return name

	def run(self):
		# these must be obtained from your personal account
		self._clientId = 'xyz'
		self._clientSecret = 'xyz'
		
		self._drive_service = None
		self._TOKEN_FILE = 'keys/googleKey.txt'
		self._oauthScope = 'https://www.googleapis.com/auth/drive'
		self._redirctURI = 'urn:ietf:wg:oauth:2.0:oob'

		start = time.time()
		self.login()
		end = time.time()
		print self._name, "> Logged In (s): \t", (end-start)
		super(GoogleStorage, self).executeProcedure()

	def login(self):
		# Run through the OAuth flow and retrieve credentials
		if os.path.exists(self._TOKEN_FILE) is False:
		   	code = self.setupLogin()

		   	credentials = flow.step2_exchange(code)
		   	storage = Storage(self._TOKEN_FILE)
		   	storage.put(credentials)
		else:
		    storage = Storage(self._TOKEN_FILE)
		    credentials = storage.get()

		# Create an httplib2.Http object and authorize it with our credentials
		http = httplib2.Http()
		http = credentials.authorize(http)

		self._drive_service = build('drive', 'v2', http=http)

	def setupLogin(self):
		flow = OAuth2WebServerFlow(self._clientId, self._clientSecret, self._oauthScope, self._redirctURI)
		authorize_url = flow.step1_get_authorize_url()
		print 'Go to the following link in your browser: ' + authorize_url
		code = raw_input('Enter verification code: ').strip()

		print self._name, "> Setup complete"
		return code

	def upload(self, fileLocation):
		name = self.__getName(fileLocation)

		start = time.time()
		media_body = MediaFileUpload(fileLocation, mimetype='application/octet-stream', resumable=False)
		body = {
		 'title': name
		}
		returnFile = self._drive_service.files().insert(body=body, media_body=media_body).execute()
		end = time.time()

		print self._name, "> Uploaded", fileLocation, ":", (end-start), "(s)"

	def download(self, fileLocation, remoteLocation):
		start = time.time()

		name = self.__getName(remoteLocation)
		try:
			param = {}
			param['q'] = 'trashed=false'
			files = self._drive_service.files().list(**param).execute()

			for file in files['items']:
				if file['title'] == name:
					url = file['downloadUrl']
					break
		except errors.HttpError, error:
			print 'An error occurred: %s' % error

		to_file = open(os.path.expanduser(fileLocation), "wb")
		resp, content = self._drive_service._http.request(url)
		to_file.write(content)
		to_file.close()
		end = time.time()

		print self._name, "> Download ", fileLocation, ":", (end-start), "(s)"

	def downloadAllFiles(self):
		# download entire directory
		print "Downloading Google files now..."