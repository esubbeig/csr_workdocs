from cryptography.fernet import Fernet

from django.conf import settings

def encrypt_message(message):
	"""
	Encrypt a message

	"""

	key = settings.CRYPT_KEY

	key = key.encode()

	encoded_message = message.encode()

	f = Fernet(key)

	encrypted_message = f.encrypt(encoded_message)

	return encrypted_message.decode()


def decrypt_message(encrypted_message):

	"""
	Decrypt a message

	"""

	key = settings.CRYPT_KEY

	key = key.encode()

	f = Fernet(key)

	decrypted_message = f.decrypt(encrypted_message.encode())

	return decrypted_message.decode()
