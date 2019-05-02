.. post:: 2019-05-02
  :tags: JWK
  :category: Cryptography

=================================
RSA公開鍵のJWK をPEM形式にする
=================================

JWK を知って、これがどうやってPEMになるんだろうという疑問のもとに調べた記録です。

目的
===========

JWK が PEM 形式の公開鍵に変換可能なことを確認する。例としてRSA暗号方式を取り上げる。

前提知識・用語
===============

RSA暗号
--------

RSA暗号は、2つの素数の積n について、n のみから2つの素数を割り出すことが困難なことを利用した暗号技術。

背景の理論は省略して概要のみ記載すると

暗号化( 平文m から 暗号文c を生成 )は以下の式を用いる:

.. math::

  c = m^e \bmod n

複合( 暗号文c から 平文m を取得)は以下の式を用いる:

.. math::

  m = c^d \bmod n

この時、各変数の定義は

:e: 適当な大きさの整数 ( 65537 がよく使われる )
:d: :math:`d = e^{-1} (mod (p - 1)(q - 1))`
:p, q: ``n = p * q`` となる素数( p != q )

となる。

2つの式から、暗号化・複合の入力パラメータを整理すると以下の表になる。

.. list-table::
  :header-rows: 1

  - -
    - 必要なパラメータ
  - - 暗号化
    - ``{e, n}``
  - - 複合
    - ``{e, p, q}``


RSA公開鍵ファイル
-------------------

PEM形式のRSA公開鍵ファイルについて、構成要素と必要なパラメータについてまとめる。

まず、 RFC7468 で証明書や公開鍵のフォーマットが定められており、それら共通のフォーマットとして以下の構造を持つ [1]_ 。

::

  -----BEGIN {label}-----
  {base64 エンコードされたデータ}
  -----END {label}-----

公開鍵の場合、 ``label`` は ``PUBLIC KEY`` であり、データの内容は

「DER(BER)エンコードされた ASN.1 の SubjectPublicKeyInfo 構造」 [2]_

とされている。

ここで、 ASN.1 はデータ構造の記法の一つであり、DER は ASN.1 で記述されたデータの符号化規則である。以後 ``SEQUENCE`` や ``BIT STRING`` などの ASN.1 の型が出てくるが、ここでは詳細に触れず、構成要素として何が含まれるかを把握する。

SubjectPublicKeyInfo は以下の構造を持つ [3]_

::

  SubjectPublicKeyInfo  ::=  SEQUENCE  {
        algorithm            AlgorithmIdentifier,
        subjectPublicKey     BIT STRING  }

:algorithm: アルゴリズムの識別子
:subjectPublicKey: 鍵の内容。アルゴリズムによって含まれる内容が異なる。

さらに、 AlgorithmIdentifer はアルゴリズムの識別子とオプションからなる [4]_

::

  AlgorithmIdentifier  ::=  SEQUENCE  {
       algorithm               OBJECT IDENTIFIER,
       parameters              ANY DEFINED BY algorithm OPTIONAL  }

アルゴリズムがRSAである場合、その識別子(OID)は rsaEncription と表記され、以下のデータで表現される [5]_

::

  pkcs-1 OBJECT IDENTIFIER ::= { iso(1) member-body(2) us(840)
                 rsadsi(113549) pkcs(1) 1 }

  rsaEncryption OBJECT IDENTIFIER ::=  { pkcs-1 1}

また、パラメータは必ず `NULL` になる。

RSA公開鍵は RSAPublicKey という型で表現される

::

  RSAPublicKey       ::= SEQUENCE {
      modulus            INTEGER,    -- n
      publicExponent     INTEGER  }  -- e

RSAPublicKey は DERエンコードされ、subjectPublicKey の BIT STRING型の値となる。

以上のことをまとめると、RSA公開鍵は以下の構造を持つ（表記は RFC の example に合わせているが、ASN.1 の文法として正しいかイメージ図のようなものなのかは未確認)

::

  SEQUENCE  {            # SubjectPublicKeyInfo
    SEQUENCE  {          # AlgorithmIdentifier
      OBJECT IDENTIFIER
        rsaEncryption (1 2 840 113549 1 1 1)
      NULL               # OPTION
    }
    BIT STRING 0 unused bits, encapsulates { # subjectPublicKey = RSAPublicKey
      SEQUENCE {
        INTEGER        # -- n, modulus
        INTEGER 65537  # -- e, publicExponent
      }
    }
  }

つまり、RSA公開鍵は暗号化に使用する ``{n, e}`` のパラメータが特定できれば作成することが可能と言える。

補足すると、RSAの秘密鍵は RSAPrivateKey として以下で表現され、複合に使用する ``{e, p, q}`` が含まれていることがわかる。 [6]_

::

  RSAPrivateKey ::= SEQUENCE {
      version           Version,
      modulus           INTEGER,  -- n
      publicExponent    INTEGER,  -- e
      privateExponent   INTEGER,  -- d
      prime1            INTEGER,  -- p
      prime2            INTEGER,  -- q
      exponent1         INTEGER,  -- d mod (p-1)
      exponent2         INTEGER,  -- d mod (q-1)
      coefficient       INTEGER,  -- (inverse of q) mod p
      otherPrimeInfos   OtherPrimeInfos OPTIONAL
  }

JWK (Json Web Key)
--------------------

JWK は暗号鍵をJSONで表現する規格であり、アルゴリズムごとのパラメータは JWA (Json Web Algorithm) RFC7518 に定義されている。

RSA の場合、以下のパラメータが定義されている [7]_

.. list-table::
  :header-rows: 1
  :widths: 25,25,50

  - - key
    - name
    - description
  - - n
    - Modulus
    - Base64urlUInt-encoded された modulus
  - - e
    - Exponent
    - Base64urlUInt-encoded された expornent。 よく使われる ``e=65537`` の場合、 ``AQAB`` という値になる

なお、 Base64urlUInt-encoded は 符号なしの 0以上の整数を big-endian で Base64url エンコードしたもの。

実験
======

(ここから実装タイムに入る予定だったがここまでまとめるので疲れたので別の機会に..

alg=RS256 の JWK から n, e のデコードした数値を使えば RSAの公開鍵は作成可能。

結論
=====

「論理上」JWKからPEMに問題なく変換できる。

参考
======

- `RSA暗号とPEM/DERの構造 - sambaiz-net <https://www.sambaiz.net/article/135/>`_
- `Where is the PEM file format specified? - stackoverflow <https://stackoverflow.com/questions/5355046/where-is-the-pem-file-format-specified>`_
- `ASN.1 データ生成/解析の事始 - SOUM/misc <https://www.soum.co.jp/misc/individual/asn1/>`_
- `整数論と代数の初歩 <http://fuee.u-fukui.ac.jp/~hirose/lectures/crypto_security/slides/01number_algebra.pdf>`_ ここだと明らかにmodは書き方(合同と二項演算)で意味違うように見えるが、ネットの記述だとなんかごっちゃになっているように見えるので書籍などで確認したい

.. rubric:: Footnotes

.. [1] `RFC7468: 2.  General Considerations <https://tools.ietf.org/html/rfc7468#section-2>`_
.. [2] `RFC7468: 13.  Textual Encoding of Subject Public Key Info <https://tools.ietf.org/html/rfc7468#section-13>`_
.. [3] `RFC5280: 4.1.2.7.  Subject Public Key Info <https://tools.ietf.org/html/rfc5280#section-4.1.2.7>`_
.. [4] `RFC5280: 4.1.1.2.  signatureAlgorithm <https://tools.ietf.org/html/rfc5280#section-4.1.1.2>`_
.. [5] `RFC3279: 2.3.1  RSA Keys <https://tools.ietf.org/html/rfc3279#section-2.3.1>`_
.. [6] `RFC3447: A.1.2 RSA private key syntax <https://tools.ietf.org/html/rfc3447#appendix-A.1.2>`_
.. [7] `RFC7518: 6.3.  Parameters for RSA Keys <https://tools.ietf.org/html/rfc7518#section-6.3>`_
