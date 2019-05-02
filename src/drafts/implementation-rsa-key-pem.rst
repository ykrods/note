
..
  2つの素数を p, q とした時、オイラーのファイ関数を使うと、以下の式が成り立つ

  .. math::

    \phi(n) = (p - 1)(q - 1)

  ここで、 :math:`\phi(n)` は

  正の整数 n と互いに素である 1 以上 n 以下の自然数の個数である

  (最大公約数 gcd(n, x) = 1 となる1 以上 n 以下の自然数xの個数と言い換えても良い)

  簡単な例

  .. math::

    \phi(15) = (3 - 1) * (5 - 1) = 8 = |\{1, 2, 4, 7, 8, 11, 13, 14\}|

  e < phi(n) である


openssl コマンドでのパラメータの確認
======================================

..
  http://www.ntt.co.jp/news2010/1001/100108a.html の記事によると2010年時点で 768ビットで素因数分解できている。

鍵の生成

::

  $ openssl genrsa 64 > private64.pem
  Generating RSA private key, 64 bit long modulus
  .++++++++++++++++++++++++++++++++++
  .++++++++++++++++++++++++++++++++++
  e is 65537 (0x10001)
  $ openssl rsa -pubout < private64.pem > public64.pem

  writing RSA key

鍵のパラメータオプションは以下で参照できる

::

  $ openssl rsa -text -pubin < public64.pem
  Public-Key: (64 bit)
  Modulus: 15053088984676071601 (0xd0e750ad47f678b1)
  Exponent: 65537 (0x10001)
  writing RSA key
  -----BEGIN PUBLIC KEY-----
  MCQwDQYJKoZIhvcNAQEBBQADEwAwEAIJANDnUK1H9nixAgMBAAE=
  -----END PUBLIC KEY-----
