"""
pyasn1 でRSA公開鍵のPEMファイルを作成するサンプルスクリプト

memo
=====

公開鍵の作成と modulus/exponent の確認

::

  $ openssl genrsa 64 > private64.pem
  $ openssl rsa -pubout < private64.pem > public64.pem
  $ openssl rsa -text -pubin < public64.pem
  Public-Key: (64 bit)
  Modulus: 16355614663079414167 (0xe2fad0e15c04c997)
  Exponent: 65537 (0x10001)
  writing RSA key
  -----BEGIN PUBLIC KEY-----
  MCQwDQYJKoZIhvcNAQEBBQADEwAwEAIJAOL60OFcBMmXAgMBAAE=
  -----END PUBLIC KEY-----

xxd でのバイナリの確認

::

  $ echo 'MCQwDQYJKoZIhvcNAQEBBQADEwAwEAIJAOL60OFcBMmXAgMBAAE=' | base64 --decode | xxd
  00000000: 3024 300d 0609 2a86 4886 f70d 0101 0105  0$0...*.H.......
  00000010: 0003 1300 3010 0209 00e2 fad0 e15c 04c9  ....0........\..
  00000020: 9702 0301 0001                           ......
"""
from base64 import b64encode

from pyasn1.type.univ import (
    Integer,
    Sequence,
    BitString,
    ObjectIdentifier,
    Null,
    Any,
)
from pyasn1.type.namedtype import (
    NamedTypes,
    NamedType,
)

from pyasn1.codec.der.encoder import encode


class AlgorithmIdentifier(Sequence):
    """
    AlgorithmIdentifier  ::=  SEQUENCE  {
      algorithm               OBJECT IDENTIFIER,
      parameters              ANY DEFINED BY algorithm OPTIONAL  }
    """
    componentType = NamedTypes(
        NamedType('algorithm', ObjectIdentifier()),
        NamedType('parameters', Any()),
    )


class SubjectPublicKeyInfo(Sequence):
    """
    SubjectPublicKeyInfo  ::=  SEQUENCE  {
        algorithm            AlgorithmIdentifier,
        subjectPublicKey     BIT STRING  }
    """
    componentType = NamedTypes(
        NamedType('algorithm', AlgorithmIdentifier()),
        NamedType('subjectPublicKey', BitString()),
    )


class RSAPublicKey(Sequence):
    """
    RSAPublicKey ::= SEQUENCE {
        modulus           INTEGER,  -- n
        publicExponent    INTEGER   -- e
    }
    """
    componentType = NamedTypes(
        NamedType('modulus', Integer()),
        NamedType('publicExponent', Integer())
    )


def makeRSAPublicKey(modulus, publicExponent):

    algorithm = AlgorithmIdentifier()
    algorithm['algorithm'] = '1.2.840.113549.1.1.1' # rsaEncription
    algorithm['parameters'] = Null('')

    subjectPublicKey = RSAPublicKey()
    subjectPublicKey['modulus'] = modulus
    subjectPublicKey['publicExponent'] = publicExponent

    subjectPublicKeyInfo = SubjectPublicKeyInfo()
    subjectPublicKeyInfo['algorithm'] = algorithm
    # int.from_bytes()
    subjectPublicKeyInfo['subjectPublicKey'] = BitString(
        hexValue=encode(subjectPublicKey).hex()
    )

    return b64encode(encode(subjectPublicKeyInfo))


print('-----BEGIN PUBLIC KEY-----')
print(
    makeRSAPublicKey(
        modulus=16355614663079414167,
        publicExponent=0x010001
    ).decode(encoding='utf-8')
)
print('-----END PUBLIC KEY-----')
