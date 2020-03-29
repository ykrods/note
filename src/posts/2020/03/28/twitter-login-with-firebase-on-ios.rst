.. post:: 2020-03-28
   :tags: iOS, Firebase, OAuth2
   :category: iOS

.. meta::
  :description: TwitterKit (2018年10月末サポート終了)をつかったまま長いこと更新していなかったアプリを更新した時のメモ

===============================================================
iOSアプリで Firebase/Auth によるツイッターログイン
===============================================================

TwitterKit (2018年10月末サポート終了)をつかったまま長いこと更新していなかったアプリを更新した時のメモ

やり方
=========

ログイン以外のTwitter 機能を利用しないのであれば、SDK等は必要ない。

Firebase のドキュメントに従えば概ね良い。

https://firebase.google.com/docs/auth/ios/twitter-login?hl=ja

Firebase 公式の実装例もこちらに公開されている。

https://github.com/firebase/quickstart-ios/tree/master/authentication

以上終わり！だと味気ないので以下にポイントを少々記載。

APIの変更
===============

この記事を書いている時点の Firebase のドキュメントでは ``Auth().signIn`` と記載されているが、最新のSDK (6.20.0 で確認) ではAPIが変わっており ``Auth.auth().signIn`` と書く。 [1]_

provider の定義位置
=====================

provier は viewController などのプロパティとして定義する。

検証のつもりでうっかり provider をボタンなどのハンドラ内で定義してしまうと、ボタンを押しても何も起きなくなる。これはローカル変数である provider が関数呼び出しが終わった時点で消滅する為なよう。 [2]_

再認証のための小技
====================

現状の Firebase/Auth では、Twitter側で認証する際に SafariViewController を利用している。このため、ログイン済みの状態で再度認証を実行すると id/password の入力をスキップして credential が取得される。

この時困るのは別のアカウントで認証し直したい場合で、セキュリティ上(プライバシー上?)の理由で SafariViewController のセッション(cookie) を外からどうこうできないし [3]_ 、iOS 11 以降では SafariViewController はアプリごとに独立したセッションを保持するため [4]_ 、ブラウザ側でログアウトしても意味がない。SafariViewController で Twitter を開いてユーザにログアウトしてもらうのはユーザも実装者も面倒。

どうするかというと、Twitter の認証オプションの ``force_login`` 使う。これにより認証済みの状態でもid/passwordを入力画面が表示される。 [5]_

上記踏まえた実装例
-------------------

.. code-block:: swift

  import UIKit
  import FirebaseAuth

  class ViewController: UIViewController {
      var provider: OAuthProvider?

      @IBAction func buttonDidPush() {
          print("buttonDidPush")
          self.provider = OAuthProvider(providerID: TwitterAuthProviderID)

          guard let provider = self.provider else { return }

          provider.customParameters = [
              "force_login": "true",
          ]

          provider.getCredentialWith(nil) { credential, error in
              guard let credential = credential, error == nil else {
                  print("Error: \(error as Optional)")
                  return
              }
              Auth.auth().signIn(with: credential) { (result, error) in
                  // signIn後の処理
              }
          }
      }
  }


おわり
=======

TwitterKit、いうても Twitter の iOS アプリを Twitter が出してるんだから結局何かしら中の人はメンテしてるんじゃないかとは思うんだけど、どう言うことなんやろなぁ。

.. rubric:: Footnotes

.. [1] `Migrate to the latest Firebase SDK for Swift (v4.0.0) <https://firebase.google.com/docs/reference/swift/naming-migration-guide>`_ この辺で変わった？と思われるが細かくは追っていない
.. [2] `#` 当たり前といえば当たり前なのだが、設定のせいかも？と思うのでログ出力するなり例外飛ばしてくれてもいいのよとは思う。
.. [3] https://developer.apple.com/documentation/safariservices/sfsafariviewcontroller
.. [4] https://takasfz.hatenablog.com/entry/2017/09/22/160617
.. [5] https://developer.twitter.com/ja/docs/basics/authentication/api-reference/authenticate
