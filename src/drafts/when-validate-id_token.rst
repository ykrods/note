.. post::
  :tags: OIDC
  :category: OIDC

========================
ID Token の検証の必要性
========================

`以前の記事 <../pyjwt-id_token-validation/>`_ でID Token の検証をしました。Authorization Code Flow で取得した ID Token を検証するつもりで調べていたのですが、ふと思ったのは「そもそも直接Googleにリクエストした結果のレスポンスに含まれるトークンが改竄される余地はないのでは？」ということでした。気になったので調べました。

各仕様の記述
===============================

OpenID Connect Core 1.0 の `3.1.3.7 ID Token Validation <https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation>`_ では `Clients MUST validate the ID Token in the Token Response` という書き出しで始まっているのでしのごの言わずに validate だ！というようにも受け取れるのですが、その下の6項目目に関連しそうな記述が見つけられます。

    If the ID Token is received via direct communication between the Client and the Token Endpoint (which it is in this flow), the TLS server validation MAY be used to validate the issuer in place of checking the token signature. The Client MUST validate the signature of all other ID Tokens according to JWS [JWS] using the algorithm specified in the JWT alg Header Parameter. The Client MUST use the keys provided by the Issuer.

    -- https://openid.net/specs/openid-connect-core-1_0-final.html#IDTokenValidation

「トークンエンドポイントから ID Token を直接受け取る場合、issuer を検証するため、トークンの署名の検証の代わりにSSL(TLS)証明書の検証を用いてもよい」と読めます。

Googleのドキュメントではどうなっているかというと

    5. Obtain user information from the ID token

    An ID Token is a JWT (JSON Web Token), that is, a cryptographically signed Base64-encoded JSON object. Normally, it is critical that you validate an ID token before you use it, but since you are communicating directly with Google over an intermediary-free HTTPS channel and using your client secret to authenticate yourself to Google, you can be confident that the token you receive really comes from Google and is valid. If your server passes the ID token to other components of your app, it is extremely important that the other components validate the token before using it.

    -- https://developers.google.com/identity/protocols/OpenIDConnect#obtainuserinfo


こちらも HTTPS で直に通信していれば信用して良い、と書いてあるように見えますが、 `using your client secret to authenticate yourself to Google,` の記述が若干違いがあるように思えます。

これは Google のドキュメントの `4. Exchange code for access token and ID token` の

https://www.googleapis.com/oauth2/v4/token

APIで渡している client_secret のことと思われますが、 Token Endpoint に client_secret をパラメータとして送る仕様は OAuth2.0 ( `RFC6749 <https://tools.ietf.org/html/rfc6749#section-3.2>`_ ) で定義されているので、(OAuth2.0に乗っている) OpenID Connect の方にはわざわざ書かれていないということなんでしょうか..?

何れにせよ、Authorization Code Flow のような直接の通信 + SSLによる保護という条件であれば、ID Token の検証はしなくても良さそうです。

とはいえ、専門家からご意見いただかないと無難に検証入れておこうかなという気持ちです（なんやねん）
