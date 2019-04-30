.. post:: 2019-04-30
   :tags: OIDC, JWT
   :category: Python

==========================================================
[Python] PyJWT で Google OAuth 2.0 API の ID Token を検証
==========================================================

PyJWT を用いて、Google OAuth 2.0 API で取得した ID Token を検証する実装について。

.. note::

  - ID Token を取得する方法についてはここでは触れません。
  - Pythonで簡単な検証アプリを作る場合は `tornado <https://www.tornadoweb.org/en/stable/auth.html>`_ の組み込みのmixinを使うと割合簡単にできます。

ID Token とは
===========================

基礎的な話は今更な感もありますが、検証に必要になる知識については触れていきます。

ID Token は OpenID Connect (OIDC) に準拠した認可サーバで、認証に成功した結果得られるトークンです。

ID Token の中身は JWT ( `RFC7519 <https://tools.ietf.org/html/rfc7519>`_ ) で表される文字列データであり、大抵の場合は `ヘッダ.ペイロード.署名` の３つの部分に分けられます [1]_ 。

具体例として、実際に Google で認証して取得したトークンを以下に記載します。

::

  # 見やすさのために改行、および実データな都合上一部省略
  eyJhbGciOiJSUzI1NiIsImtpZCI6IjI2ZmM0Y2Qy
  M2QzODdjYmM0OTBmNjBkYjU0YTk0YTZkZDE2NTM5
  OTgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOi(省略).cnY5xzp(省略)

ヘッダ・ペイロードはそれぞれ base64url でエンコードされた JSON 文字列な為、デコードすることでデータを確認できます。`PyJWT <https://pyjwt.readthedocs.io/en/latest/>`_ の ``get_unverified_header`` 関数で 上記の ID Token のヘッダを取得してみます。

.. code-block:: python

  # $ pip install pyjwt # == 1.7.1
  # $ python
  Python 3.7.1 (default, Oct 24 2018, 22:35:30)
  [GCC 6.3.0 20170516] on linux
  Type "help", "copyright", "credits" or "license" for more information.
  >>> from pprint import pprint
  >>> import jwk
  >>> id_token = "eyJhbGciOiJSUzI1NiIsImtpZCI6IjI2ZmM0Y2QyM2QzODdjYmM0OTBmNjBkYjU0YTk0YTZkZDE2NTM5OTgiLCJ0eXAiOiJKV1QifQ.eyJpc3MiOi(省略).cnY5xzp(省略)"
  >>> header = jwt.get_unverified_header(id_token)
  >>> pprint(header)
  {'alg': 'RS256',
   'kid': '26fc4cd23d387cbc490f60db54a94a6dd1653998',
   'typ': 'JWT'}

これらは JWS ( `RFC7515 <https://tools.ietf.org/html/rfc7515>`_ ) でヘッダパラメータとして定義されています。 ``kid`` は署名の際にどの鍵が使われたかを示すIDです(検証で必要になります)。

同様に、ペイロードもデコードしてみましょう。PyJWT では ``jwt.decode()`` 関数に ``verify=False`` をオプションとして加えると、検証なしでデコードすることができます。

.. code-block:: python

  >>> # 個人情報的なところは適宜捏造しています
  >>> claims = jwt.decode(id_token, verify=False)
  >>> pprint(claims)
  {'iss': 'https://accounts.google.com',
   'azp': 'xxx.apps.googleusercontent.com',
   'aud': 'xxx.apps.googleusercontent.com',
   'sub': 'xxxx',
   'email': 'xxxx@example.org',
   'email_verified': True,
   'at_hash': 'xxxx',
   'name': 'Yk rods',
   'picture': 'https://example.org/photo.jpg',
   'given_name': 'Yk',
   'family_name': 'rods',
   'locale': 'ja',
   'iat': 1556240765,
   'exp': 1556244365}

これらの各属性は Claim と呼ばれます。 Claim はユーザ自身の属性、もしくは認証イベントに関する情報であり、OpenID Connect Core 1.0 の `5. Claims <https://openid.net/specs/openid-connect-core-1_0.html#Claims>`_ 以下で定義されています。

Claim のうち、検証に関係するものをピックアップして下記にまとめます。

.. list-table::
  :header-rows: 1
  :widths: 30, 70

  - - name
    - description
  - - iss
    - issuer, JWTの発行者を識別する情報。
  - - aud
    - audience, 誰に対して発行されたJWTなのかを示す。CLIENT_ID が入る
  - - exp
    - expiration time, ID トークンの有効期限。Unix time で表現される。

ID Token の検証
===========================

ID Token の検証手順は、以下で記述されています。

OpenID Connect Core 1.0

- `3.1.3.5 Token Response Validation <https://openid.net/specs/openid-connect-core-1_0-final.html#>`_
- `3.1.3.7 ID Token Validation <https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation>`_

また `Googleのドキュメント <https://developers.google.com/identity/protocols/OpenIDConnect?hl=ja>`_ にも記載があります。

Google認証の場合は以下の項目を検証すれば良いようです。

1. JWT の署名が正しいか確認する
2. claim の iss が https://accounts.google.com もしくは accounts.google.com であることを確認する
3. claim の aud が Google API Console で作成した CLIENT_ID と等しいことを確認する
4. claim の exp が 有効期間内であることを確認する

署名の検証
------------

署名の検証というと一般的に以下のような流れになります。

1. 署名者が配布している公開鍵を取得
2. メッセージ(署名されたデータ)から公開鍵を使ってダイジェストを生成
3. 署名とダイジェストの値が一致するかを確認

ここで疑問になってくるのは、「公開鍵をどうやって取得するか」です。

公開鍵の取得
---------------

Google のドキュメントには以下のように記載されています

    1. Verify that the ID token is properly signed by the issuer. Google-issued tokens are signed using one of the certificates found at the URI specified in the jwks_uri field of the discovery document.

    -- https://developers.google.com/identity/protocols/OpenIDConnect?hl=ja

ここで、 discovery document は同ページに記載されている

https://accounts.google.com/.well-known/openid-configuration

であり、実際の値は

::

  "jwks_uri": "https://www.googleapis.com/oauth2/v3/certs"

となっています。ではこのURLを curl で叩いてみましょう。

::

  # (2019-04-29 取得)
  $ curl https://www.googleapis.com/oauth2/v3/certs
  {
    "keys": [
      {
        "use": "sig",
        "kid": "26fc4cd23d387cbc490f60db54a94a6dd1653998",
        "e": "AQAB",
        "kty": "RSA",
        "alg": "RS256",
        "n": "wbRc_hVBiEGE_syqdbnkeEx-GQEAOuqBbgSIn1HgS0xaOqjk8trHi0FNTLg_Pmajo4f3rWedlh_ABGyJeNR5TphqURGemAdg51B3eANOrykzJgg9824rjWII94RxRoeLVEqdU3d0G6nPx2d7Tz2P2w9vN0CdKQTnXG1bpbtOCd4RPw_jNvNFlnnrdrYum7wE9mju4uTCVlTcUz6hZIG_wQp1uLbaWRWFxiTzYkRdQhqutBzixo9VE8eLUPotjDltnvGuQbtHOQwOXKUEWxCTXa1wT4l61YHLo2aMGxTpzC7B14G323ekY2t_24RF213ewGTzImzFvYCBoLXZEJJUwQ"
      },
      {
        "kid": "5d887f26ce32577c4b5a8a1e1a52e19d301f8181",
        "e": "AQAB",
        "kty": "RSA",
        "alg": "RS256",
        "n": "13GdrD5sfUui84PIHNURTtbu_blCXOHMg26buwcNbXWmvb9gDAT29qBrNB2MFi-YAi04mgEj2so9sF-u1oiha8iJbzn8FZaJ76WPyfE4SaPhy9FSin569Yx3wPoZYVKRoFc5ZU4h_qjYRKO_Jx7_uyoHam8-El07DmsDJnzs00VjU1NTiHZz1PwrjOZslYJChHU9AwM_NcInB2pPGFm3eFetLDkkTOH-Tt27TCeIr_bUp09dCIGcdDwcY9wRknqlKXatgF3Ec9SmGCIb9uJKTM-_O9pOmRz4sVAlx9bA01xIkWELAZd8VhEtogzEkIYOtKdQTheRqky54hNPtWMu1Q",
        "use": "sig"
      }
    ]
  }

さて、 ``"kty": "RSA"`` の部分からRSAアルゴリズムなのはわかりますが、普段見る PEM 形式の公開鍵ではありません( ``-----BEGIN PUBLIC KEY-----`` で始まるもの)。なんなんでしょうかこれは...?

実は先ほど登場した discovery document は OpenID Connect Discovery 1.0 という仕様に従っており、 `OpenID Provider Metadata <https://openid.net/specs/openid-connect-discovery-1_0.html#ProviderMetadata>`_ にてそれぞれのメタ情報が説明されています。この中で `jwks_uri` は「JWK Set のURL」と記述されています。

JWK (JWK Set)
---------------

JWK ( `RFC7517 <https://tools.ietf.org/html/rfc7517>`_ ) は暗号鍵をJSONで表現する仕様です。

JWK Set は JWK の集合であり、 ``keys: [ jwk1, jwk2, ...]`` というフォーマットになります。

google の場合、上述したように JWK が二つ定義されていますが、これは JWTのヘッダに含まれる kid と同じ JWK を選べば OK です。

PyJWT でRSA公開鍵を扱う場合、 ``jwt.algorithms.RSAAlgorithm`` を使います。

また、PyJWT で公開鍵を扱う際は cryptography のインストールも必要になります。

::

  pip install cryptography # == 2.6.1

.. code-block:: python

  >>> from jwt.algorithms import RSAAlgorithm
  >>>
  >>> jwk_json = """{
  ...         "use": "sig",
  ...         "kid": "26fc4cd23d387cbc490f60db54a94a6dd1653998",
  ...         "e": "AQAB",
  ...         "kty": "RSA",
  ...         "alg": "RS256",
  ...         "n": "wbRc_hVBiEGE_syqdbnkeEx-GQEAOuqBbgSIn1HgS0xaOqjk8trHi0FNTLg_Pmajo4f3rWedlh_ABGyJeNR5TphqURGemAdg51B3eANOrykzJgg9824rjWII94RxRoeLVEqdU3d0G6nPx2d7Tz2P2w9vN0CdKQTnXG1bpbtOCd4RPw_jNvNFlnnrdrYum7wE9mju4uTCVlTcUz6hZIG_wQp1uLbaWRWFxiTzYkRdQhqutBzixo9VE8eLUPotjDltnvGuQbtHOQwOXKUEWxCTXa1wT4l61YHLo2aMGxTpzC7B14G323ekY2t_24RF213ewGTzImzFvYCBoLXZEJJUwQ"
  ...       }"""
  >>>
  >>> public_key = RSAAlgorithm.from_jwk(jwk_json)
  >>> public_key
  <cryptography.hazmat.backends.openssl.rsa._RSAPublicKey object at 0x7fd3f79024a8>

少し脱線しますが 「JWK が公開鍵を表しているなら、 PEM に変換可能なはず」というのは自然な発想ですが、これを自前で実装しようとするとそれなりに大変です。しかし PyJWT (cryptography) を使えば以下のコードで変換できます。

.. code-block:: python

  >>> from cryptography.hazmat.primitives import serialization
  >>> pem = public_key.public_bytes(encoding=serialization.Encoding.PEM, format=serialization.PublicFormat.SubjectPublicKeyInfo)
  >>> pem
  b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAwbRc/hVBiEGE/syqdbnk\neEx+GQEAOuqBbgSIn1HgS0xaOqjk8trHi0FNTLg/Pmajo4f3rWedlh/ABGyJeNR5\nTphqURGemAdg51B3eANOrykzJgg9824rjWII94RxRoeLVEqdU3d0G6nPx2d7Tz2P\n2w9vN0CdKQTnXG1bpbtOCd4RPw/jNvNFlnnrdrYum7wE9mju4uTCVlTcUz6hZIG/\nwQp1uLbaWRWFxiTzYkRdQhqutBzixo9VE8eLUPotjDltnvGuQbtHOQwOXKUEWxCT\nXa1wT4l61YHLo2aMGxTpzC7B14G323ekY2t/24RF213ewGTzImzFvYCBoLXZEJJU\nwQIDAQAB\n-----END PUBLIC KEY-----\n'

PyJWT で Id Token を検証する
================================

想像を超えて前置きが長くなりましたが、ようやく検証に必要な情報が揃いました。最初に検証なしで ``jwt.decode()`` を使いましたが、今度は検証ありでデコードしてみましょう。

検証する場合、引数には id_token, public_key の他、issuer に https://accounts.google.com, audience に CLIENT_ID を指定します。これは iss, aud の検証を PyJWT 側でやってくれているということですね [2]_ 。

.. code-block:: python

  GOOGLE_ISSUER = 'https://accounts.google.com'
  CLIENT_ID = 'YOUR_CLIENT_ID'

  claims = jwt.decode(id_token,
                      public_key,
                      issuer=GOOGLE_ISSUER,
                      audience=CLIENT_ID,
                      algorithms=["RS256"])

また、 https://pyjwt.readthedocs.io/en/latest/usage.html#expiration-time-claim-exp にある通り、 exp の検証もデフォルトで行ってくれるため、ID Token の検証はこの関数呼び出しで完了することになります。素晴らしい。

コード例
===============

まとめると、JWTの検証はこんな感じに書けます。

# tornado アプリを使って検証したため AsyncHTTPClient を使っていますが、requests等でも問題ないです

.. code-block:: python

  import json
  import jwt
  from jwt.algorithms import RSAAlgorithm
  from tornado.httpclient import AsyncHTTPClient

  JWKS_URI = 'https://www.googleapis.com/oauth2/v3/certs'
  GOOGLE_ISSUER = 'https://accounts.google.com'
  CLIENT_ID = 'YOUR_CLIENT_ID'

  def validate_id_token(id_token):
    header = jwt.get_unverified_header(id_token)

    http_client = AsyncHTTPClient()
    res = await http_client.fetch(JWKS_URI)
    jwk_set = json.loads(res.body)
    jwk = next(filter(lambda k: k['kid'] == header['kid'], jwk_set['keys']))

    public_key = RSAAlgorithm.from_jwk(json.dumps(jwk))

    claims = jwt.decode(id_token,
                        public_key,
                        issuer=GOOGLE_ISSUER,
                        audience=CLIENT_ID,
                        algorithms=["RS256"])
    return claims

.. rubric:: Footnotes

.. [1] ID Token は署名のみの JWS ( `RFC7515 <https://tools.ietf.org/html/rfc7515>`_ ) と、署名＋暗号化の JWE ( `RFC7516 <https://tools.ietf.org/html/rfc7516>`_ ) があり、後者の場合は5パートに分かれた文字列になる。
.. [2] https://pyjwt.readthedocs.io/en/latest/usage.html#issuer-claim-iss に記載がある
