from baseStorage import *
from dropbox import client, rest, session

class DropboxStorage(BaseStorage):
	def run(self):
		# these must be obtained from your personal account
		self._app_key = 'xyz'
		self._app_secret = 'xyz'
		
		self._api_client = None
		self._TOKEN_FILE = 'keys/token_store.txt'
		self._loginEvent = threading.Event()

		start = time.time()
		self.login()
		end = time.time()
		print self._name, "> Logged In (s): \t", (end-start)
		self.executeProcedure()

	def login(self):
		"""login user based on previous credentials"""
		try:
			serialized_token = open(self._TOKEN_FILE).read()
			if serialized_token.startswith('oauth1:'):
				access_key, access_secret = serialized_token[len('oauth1:'):].split(':', 1)

				# create a session used to create a client
				sess = session.DropboxSession(self._app_key, self._app_secret)
				sess.set_token(access_key, access_secret)
				self._api_client = client.DropboxClient(sess)
				# print ("Dropbox > [loaded OAuth 1 access token]")
			elif serialized_token.startswith('oauth2:'):
				access_token = serialized_token[len('oauth2:'):]
				self._api_client = client.DropboxClient(access_token)
				# print ("Dropbox > [loaded OAuth 2 access token]")
			else:
				print ("Malformed access token in %r." % (self._TOKEN_FILE,))
		except IOError:
			self.setupLogin()

	def setupLogin(self):
		"""request user to accept access"""
		flow = client.DropboxOAuth2FlowNoRedirect(self._app_key, self._app_secret)
		authorize_url = flow.start()
		sys.stdout.write("1. Go to: " + authorize_url + "\n")
		sys.stdout.write("2. Click \"Allow\" (you might have to log in first).\n")
		sys.stdout.write("3. Copy the authorization code.\n")
		code = raw_input("Enter the authorization code here: ").strip()

		try:
			access_token, user_id = flow.finish(code)
		except rest.ErrorResponse as e:
			self.stdout.write('Error: %s\n' % str(e))
			return

		with open(self._TOKEN_FILE, 'w') as f:
			f.write('oauth2:' + access_token)
			self._api_client = client.DropboxClient(access_token)

	def upload(self):
		while len(self._files) > 0:
			fileLocation = self._files.pop(0)

			start = time.time()
			from_file = open(fileLocation, "r")
			self._api_client.put_file(fileLocation, from_file)
			end = time.time()

			self.updateManager(end-start)
			print self._name, "Uploaded ", fileLocation, ":", (end-start), "(s)"

	def download(self, fileLocation, remoteLocation):
		start = time.time()
		to_file = open(os.path.expanduser(fileLocation), "wb")
		f, metadata = self._api_client.get_file_and_metadata(remoteLocation)
		to_file.write(f.read())
		to_file.close()
		end = time.time()

		print self._name, "> Download ", fileLocation, ":", (end-start), "(s)"

	def downloadAllFiles(self):
		# download entire directory
		print "Downloading Dropbox files now..."