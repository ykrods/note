.. post:: 2021-03-17
   :tags: mTLS, macOS
   :category: DesktopApp

.. meta::
  :description: いかにして開発を断念したか


==============================================================
pyobjc で mTLS認証付きの Electron っぽいものを途中まで作った
==============================================================

いかにして開発を断念したか

.. note::

  もしかしたら同じような発想をする人がいるかもしれないので俺の屍を越えてゆけ的な発想で記事を書いています。

モチベーション
===============

* Python で Electron-like な GUIフレームワークを作ってみたかった [1]_

  * 同じコンセプトのライブラリとして `pywebview <https://pywebview.flowrl.com/>`_ がある。

* １プロセスでサーバとWebView を立ち上げて mTLS 認証すればだいぶセキュアなのでは？という実証実験をしたかった

  * まぁ今考えると、ローカルで管理者権限取られないとキャプチャまではされないので http + なんかのトークン or ベーシック認証 でもそんなに問題ではないかもしれない

* asyncio (aiohttp) が使いたかった

  * pywebview は wsgi サーバのみ対応

実装方針
=========

* `pyobjc <https://pypi.org/project/pyobjc/>`_ でガワを作る(ので差し当たり macOS 限定)
* Python の `ssl.SSLContext <https://docs.python.org/ja/3/library/ssl.html>`_ でサーバアプリケーションを TLS 接続可能にする
* アプリ起動時に `pyca/cryptography <https://cryptography.io/en/latest/>`_ で証明書を生成し、 webview, サーバに読み込ませる

  * ``#`` macOS/iOS はキーチェーン経由で直接秘密鍵をメモリ上にロードしなくても認証できるような仕組みになっているので、セキュリティ重視にするならユーザにキーチェーンアクセスで事前に秘密鍵を生成してもらい、起動時に選ぶような形がいいかもしれない

成果物
=======

`一応動くものがこちら <https://github.com/ykrods/pyobjc-webview-mtls-example>`_

苦労した点
===========

* Cocoa のランループと asyncio のイベントループの兼ね合い

  * 最初はランループ上でイベントループを回す実装を見つけたのでそれを使っていたが、pyobjc が提供している Cocoa の API は普通の関数(not コルーチン関数) なので少々不便だった。

    * 具体的には pyobjc のコールバック関数では await が使えない(待てない)
    * ランループ(のイベントループ)は止められないので ``loop.run_until_complete`` も(ループ1個では)使えない

  * 最終的には別のスレッドで loop を生成してサーバ側はそっちを使う形にした

* そもそも keychain の操作は Objective-C でもコード例が少なかったので、まず Objective-C でコードを書いて挙動を確認してから Python (pyobjc) に書き直したりした
* openssl にバグがあったり [2]_ keychain のドキュメントがよくわかんなかったり [3]_ pyobjc にバグがあったり... [4]_

苦労しつつ作ったが..
================================

とりあえず動いたので動作確認と配布周りの調査をした結果、以下の理由により断念というかやる気が消失した

* どうやら WKWebView のバグでローカルのHTTPSサーバでは websocket が使えないらしく、そうなると aiohttp 使う意味が私の中で半減する

  * https://developer.apple.com/forums/thread/74152?answerId=216724022#216724022
  * 「WKWebView に webview-js 間でやりとりする API が提供されているのでそれを使ってね」とのこと
  * pywebview は↑の方式に対応しているので「じゃあpywebviewでいいじゃん...」となった

* 普段 macOS アプリを作っていないので全然知らなかったが、最近の macOS のアプリは 公証(Notarization) が必須になっていて、要は開発者が Apple の開発者登録をして年99ドル払わないとアプリを配布してもユーザが実行できなくなった

  * そもそも Python で GUI 作るってかなりの確率で趣味なので、趣味人が Apple の開発者登録するとは思えない。あるいは業務用のアプリで Python 使いたいから GUI を、という場合も考えられるがその場合はまぁ Windows アプリだろうし。
  * 自己署名のエンドエンティティ証明書でhttps通信するアプリが公証通るのかも怪しい（試してないが）

感想
=====

いい勉強になった（ポジティブ）

* マイナーなことをしようとするとバグに出会う確率がそれなりにあるという学びを得た

.. rubric:: Footnotes

.. [1] 余程の事情でもなければ Electron を使うのが良いのではと思いますが
.. [2] :ref:`tls-authentication` で触れているやつ
.. [3] :ref:`keychain-behavior-on-macos` よくわからなかったのでこちらの記事に整理した
.. [4] https://github.com/ronaldoussoren/pyobjc/issues/320
