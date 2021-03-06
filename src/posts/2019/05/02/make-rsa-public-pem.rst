.. post:: 2019-05-02
  :tags: JWK
  :category: Cryptography

=================================
RSA公開鍵のJWKをPEM形式にする
=================================

JWK を知って、これがどうやってPEMになるんだろうという疑問のもとに調べた記録です。

目的
===========

JWK が PEM 形式の公開鍵に変換可能なことを確認する。例としてRSA暗号方式を取り上げる。

前提知識・用語
===============

RSA暗号
--------

RSA暗号は、2つの素数の積n について、n のみから元の2つの素数を割り出すことが困難なことを利用した暗号技術。

背景の理論は省略して概要のみ記載すると

暗号化( 平文m から 暗号文c を生成 )は以下の式を用いる:

.. math::

  c = m^e \bmod n

復号( 暗号文c から 平文m を取得)は以下の式を用いる:

.. math::

  m = c^d \bmod n

この時、各変数の定義は

:e: 適当な大きさの整数 ( 65537 がよく使われる )
:d: :math:`ed \equiv 1 (mod (p - 1)(q - 1))` を満たすd
:n: ``n = p * q`` で :math:`0 \leq m,c \leq n - 1`
:p, q: 素数( p != q )

となる。

2つの式から、暗号化・復号の入力パラメータを整理すると以下の表になる。

.. list-table::
  :header-rows: 1

  - -
    - 必要なパラメータ
  - - 暗号化
    - ``{e, n}``
  - - 復号
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

以上のことをまとめると、RSA公開鍵は以下の構造を持つ（次の表記は RFC の example を参考にしているが、ASN.1 のヒューマンリーダブルな表記法として正確かは未確認)

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

つまり、暗号化に使用する ``{n, e}`` のパラメータが特定できればRSA公開鍵をPEM形式で表現できることがわかった。

ちなみに、RSAの秘密鍵は RSAPrivateKey として以下で表現され、復号に使用する ``{e, p, q}`` が含まれていることがわかる。 [6]_

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

なお、 Base64urlUInt-encoded は 0以上の整数を符号なし big-endian でオクテット列として表現したものを Base64url エンコードしたもの。

::

  # e=65537 の例
  65537
  => 0x10001                      ; 16進数表現
  => 00000001 00000000 00000001   ; 2進数表現 (unsigned big-endian octet sequence)
  => 000000 010000 000000 000001  ; base64変換(1) 6ビットずつ分割
  =>      A      Q      A      B  ; base64変換(2) 文字列変換
  => AQAB


実験
======

ここまでの内容から alg=RS256 の JWK から n, e のデコードした数値を使えば RSA の公開鍵は作成可能なことは自明。

(ここから実装タイムに入る予定だったがここまでまとめるので疲れたので別の機会に..

.. update:: 2020-06-18

  ASN.1 のパディングのルール等がややこしくバイナリレベルで実装するのが大変だったため `pyasn1 <https://pypi.org/project/pyasn1/>`_ の力を借りてつくったものが `こちら <https://github.com/ykrods/note/blob/master/src/posts/2019/05/02/rsa_key_pyasn1.py>`_ [8]_


結論
=====

JWK から PEM に問題なく変換できる。

参考
======

- `RSA暗号とPEM/DERの構造 - sambaiz-net <https://www.sambaiz.net/article/135/>`_
- `Where is the PEM file format specified? - stackoverflow <https://stackoverflow.com/questions/5355046/where-is-the-pem-file-format-specified>`_
- `ASN.1 データ生成/解析の事始 - SOUM/misc <https://www.soum.co.jp/misc/individual/asn1/>`_
- `整数論と代数の初歩 <http://fuee.u-fukui.ac.jp/~hirose/lectures/crypto_security/slides/01number_algebra.pdf>`_ こちらの資料のように mod は書き方(合同とコンピュータ上での二項演算)で意味が異なるが、ネットの記述だと html で数式が書きにくい都合もあり、ごっちゃになっているように思える。理論的な証明の部分は書籍などで確認したい。

  * (追記: 後で確認したら整数の合同は高校数学の範囲らしいが全く覚えていない...

.. rubric:: Footnotes

.. [1] `RFC7468: 2.  General Considerations <https://tools.ietf.org/html/rfc7468#section-2>`_
.. [2] `RFC7468: 13.  Textual Encoding of Subject Public Key Info <https://tools.ietf.org/html/rfc7468#section-13>`_
.. [3] `RFC5280: 4.1.2.7.  Subject Public Key Info <https://tools.ietf.org/html/rfc5280#section-4.1.2.7>`_
.. [4] `RFC5280: 4.1.1.2.  signatureAlgorithm <https://tools.ietf.org/html/rfc5280#section-4.1.1.2>`_
.. [5] `RFC3279: 2.3.1  RSA Keys <https://tools.ietf.org/html/rfc3279#section-2.3.1>`_
.. [6] `RFC3447: A.1.2 RSA private key syntax <https://tools.ietf.org/html/rfc3447#appendix-A.1.2>`_
.. [7] `RFC7518: 6.3.  Parameters for RSA Keys <https://tools.ietf.org/html/rfc7518#section-6.3>`_
.. [8] 既存の Python のライブラリでは `PyCryptodome <https://pycryptodome.readthedocs.io/en/latest/src/public_key/rsa.html>`_ や `pyca/cryptography <https://cryptography.io/en/latest/hazmat/primitives/asymmetric/rsa.html>`_ があるので通常はこれらを使う
