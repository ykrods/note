.. post:: 2019-05-05
  :tags: OIDC
  :category: OIDC

========================
ID Token の検証の必要性
========================

`以前の記事 <../../../04/30/pyjwt-id_token-validation/>`_ でID Token の検証をしました。これ書いた時は

「Authorization Code Flow で code と交換で取得した ID Token を検証する」

つもりで調べていたのですが、ふと「そもそもこの場合だと ID Token は Google との直接の通信で受け取るので、改竄される余地が無いのでは？」と思いました。ので少し調べました。

各仕様の記述
===============================

OpenID Connect Core 1.0 の `3.1.3.7 ID Token Validation <https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation>`_ では

::

  Clients MUST validate the ID Token in the Token Response

という書き出しで始まっているため、しのごの言わずに validation だ！というようにも受け取れるのですが、その下の6項目目に関連しそうな記述が見つけられます。

    If the ID Token is received via direct communication between the Client and the Token Endpoint (which it is in this flow), the TLS server validation MAY be used to validate the issuer in place of checking the token signature. The Client MUST validate the signature of all other ID Tokens according to JWS [JWS] using the algorithm specified in the JWT alg Header Parameter. The Client MUST use the keys provided by the Issuer.

    -- https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation

ほぼ直訳ですが「トークンエンドポイントから ID Token を直接受け取る場合、issuer を検証するため、トークンの署名の検証の代わりにSSL(TLS)証明書の検証を用いてもよい」と読めます。

で、 `Certified OpenID Provider <https://openid.net/certification/>`_ たる Google のドキュメントではどうなっているかというと

    5. Obtain user information from the ID token

    An ID Token is a JWT (JSON Web Token), that is, a cryptographically signed Base64-encoded JSON object. Normally, it is critical that you validate an ID token before you use it, but since you are communicating directly with Google over an intermediary-free HTTPS channel and using your client secret to authenticate yourself to Google, you can be confident that the token you receive really comes from Google and is valid. If your server passes the ID token to other components of your app, it is extremely important that the other components validate the token before using it.

    -- https://developers.google.com/identity/protocols/OpenIDConnect#obtainuserinfo

こちらも HTTPS で直に通信していれば信用して良い、と書いてあるように見えます。

※ `and using your client secret to authenticate yourself to Google,` の記述について

トークンを取得するAPIである Token Endpoint に渡す ``client_secret`` のことを指していると思われます。 Token Endpoint に client_secret を送る仕様は OAuth2.0 ( `RFC6749 <https://tools.ietf.org/html/rfc6749#section-3.2>`_ ) で定義されているので、(OAuth2.0に乗っている) OpenID Connect の方にはわざわざ書かれていないということなんでしょうか..?

じゃあ検証不要か？
====================

個人的な判断でいうと、とはいえ「やらなくてもいい」であって「やらない方がいい」訳ではないので、やっとこうと思います。明らかなコストになるなら考えるんですが、そうでもないですし。

ただ、何らかのSSLの脆弱性を突かれて、かつDNSまで書き換えられてる(意図しない通信相手からトークンを取得してしまう)ような状況までなってたら、公開鍵のエンドポイントも書き換えられそうなものなので、トークンの検証をしても改竄は見抜けないのでは？という気がします。このタイミングでの検証が明確に有意なパターンがあまり思いつかない（だからこそ MAY なのかもしれないが）。

まとめ
=======

専門家にご意見いただきたい（まとめになってない）。
