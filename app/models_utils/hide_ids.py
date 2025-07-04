
"""
Hide integer ids 

"""
import os ,string 
from hashids import Hashids

class ObfuscateId:
    """ID obfuscation using hashids with class-level configuration"""
    _SALT = os.getenv('HASH_ID_SALT')
    _MIN_LENGTH = 6
    _ALPHABET = string.ascii_letters + string.ascii_letters + string.digits
    
    _hasher = Hashids(
        min_length=_MIN_LENGTH,
        alphabet=_ALPHABET,
        salt=_SALT
    )

    @classmethod
    def set_config(cls, salt: str = None, min_length: int = None, alphabet: str = None):
        """Update configuration (call once at startup)"""
        if salt:
            cls._SALT = salt
        if min_length:
            cls._MIN_LENGTH = min_length
        if alphabet:
            cls._ALPHABET = alphabet
        
        cls._hasher = Hashids(
            salt=cls._SALT,
            min_length=cls._MIN_LENGTH,
            alphabet=cls._ALPHABET
        )

    @classmethod
    def encode(cls, id_num: int) -> str:
        """Obfuscate an integer ID to a string
        
        Args:
            id_num: Positive integer to encode
        Returns:
            Obfuscated string
        Raises:
            ValueError: If input is not a positive integer
        """
        if not isinstance(id_num, int) or id_num < 1:
            raise ValueError("ID must be a positive integer")
        return cls._hasher.encode(id_num)

    @classmethod
    def decode(cls, obfuscated: str) -> int:
        """Decode an obfuscated string back to the original ID
        
        Args:
            obfuscated: String generated by encode()
        Returns:
            Original integer ID
        Raises:
            ValueError: If input cannot be decoded
        """
        decoded = cls._hasher.decode(obfuscated)
        if not decoded:
            raise ValueError("Invalid obfuscated ID")
        return decoded[0]

    @classmethod
    def encode_many(cls, *id_numbers: int) -> str:
        """Obfuscate multiple integers into one string"""
        return cls._hasher.encode(*id_numbers)

    @classmethod
    def decode_many(cls, obfuscated: str) -> tuple:
        """Decode a string containing multiple IDs"""
        return cls._hasher.decode(obfuscated)
