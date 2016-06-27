from os import urandom
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from pwgen import pwgen
import re


def _generatesalt():
    """
    Generates a 32 bytes random salt used for hashing.
    :return: the generated salt
    """
    return bytes(urandom(32))


def _generate_random_iteration():
    """
    Generates a 3 byte integer number which is used as an iteration for hashing.
    :return: the 3 byte random iteration value.
    """
    return int.from_bytes(urandom(2), byteorder="big")


def __generate_random_password():
    """
    Generates a random password that does not violate the password password and complex, hashes the password
    with a generated salt and number of iteration.
    :return: the hashed password, the salt and number of iterations
    """
    _salt = _generatesalt()
    _number_iterations = _generate_random_iteration()

    # Generate password using random information
    password_gen = bytes(pwgen(capitalize=True, pw_length=8, symbols=True, numerals=True), encoding='utf-8')
    digest = operation(password=password_gen, salt=_salt, iterations=_number_iterations)

    return dict(password=password_gen, password_digest=digest, salt=_salt, iterations=_number_iterations)


def operation(**kwargs):
    """
    Performs the hash operation using sha 256
    :param kwargs: contains the salt and number of iterations as keyword arguments
    :return: the hashed password
    """
    digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
    for i in range(kwargs['iterations']):
        digest.update(kwargs['password'] + kwargs['salt'])
    return digest.finalize()


class ViolatesPolicy(Exception):
    pass


class NoPolicy(Exception):
    pass


class Password(object):
    def __init__(self, password, history=[]):
        self.password = password
        self.policy = {
            'num_characters': 8,
            'password_history': True,
            'alphanumeric': True
        }
        self.password_history = history

        if not isinstance(password, bytes):
            raise TypeError('Password must be a byte value.')

        # Check if the password violates policy
        self._enforce_policy()

    def encrypt(self):
        """
        Generates the hash of the password using sha 512, a salt and number of iterations to make the hash
        generation computationally expensive and harder for an attacker.
        :return: the generated hashed password, the generated salt and the number of iterations
        """
        _salt = _generatesalt()
        _number_iterations = _generate_random_iteration()

        password_digest = operation(password=self.password, salt=_salt, iterations=_number_iterations)

        # Perform hash using iterations and salt.
        return dict(password_digest=password_digest, salt=_salt, iterations=_number_iterations)

    def verify(self, _salt, _iterations):
        """
        Verifies a password by hashing the password with the given salt and number of iterations.
        :param _salt: the salt used for hashing
        :param _iterations: the number of iterations used for hashing
        :return: the hashed password (message digest)
        """
        return operation(password=self.password, salt=_salt, iterations=_iterations)

    def _enforce_policy(self):
        if self.policy is None:
            raise NoPolicy('No password policy found. Please specify one.')

        # Decode the byte string for comparison
        pass_word = str(self.password, encoding='utf-8')
        print(pass_word)

        regex = re.compile(r'((?=.*\d)(?=.*[a-zA-Z])(?=.*[!/\-$%^&*()_+|~=`{}\[\]:";\'<>?,.@#\\/]).{8,20})')
        match = regex.match(pass_word)

        if match is None or match.group() != pass_word or pass_word in self.password_history:
            raise ViolatesPolicy('Password did not meet requirements.')
