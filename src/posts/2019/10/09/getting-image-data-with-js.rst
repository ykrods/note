.. post:: 2019-10-09
  :tags: JavaScript, Canvas, CORS, 同一オリジンポリシー
  :category: JavaScript

===========================================================================
[覚書き] JavaScript で img 要素の画像データを取得する方法とCanvas汚染
===========================================================================

MDNに解説があるので基本はそちらを参照されると良いと思う。

`Allowing cross-origin use of images and canvas - HTML: Hypertext Markup Language | MDN <https://developer.mozilla.org/en-US/docs/Web/HTML/CORS_enabled_image>`_

やりたいこと
==============================================

JavaScript で img 要素の画像のデータを取得する。

ユースケースとしては、以下が考えられる。

- フロント側の実装でなんらかの画像加工処理を行う
- 複数の画像データをzipにまとめてダウンロード
- dataURL に変換して localStorage に保存

方法
======

canvas に一度画像を描写し、 ``toDataURL`` または ``toBlob`` を呼び出すことでデータの取得ができる。

.. code-block:: javascript

  const img = document.querySelector('img');
  const canvas = document.createElement('canvas');
  canvas.width = img.width;
  canvas.height = img.height;
  canvas.getContext('2d').drawImage(img, 0, 0);

  // dataURL を取得
  const dataUrl = canvas.toDataURL('image/png');
  // blob を取得
  canvas.toBlob((b) => { console.log(b); }, 'image/jpeg', 1.0);

ただし、これができるのはキャンバスが汚染されていない場合に限られる。

汚染されたキャンバス( Tainted canvas )
==========================================

キャンバスにオリジン間のアクセスを禁止されている画像を ``drawImage`` で描画した場合、そのキャンバスは「汚染された」状態になる。

- 汚染されたキャンバスでもブラウザ上には表示される
- 汚染されたキャンバスに対して ``toDataURL`` や ``toBlob`` でデータを取得しようとすると、 ``SecurityError`` が発生する。

キャンバス汚染の回避
===================================

前提として、画像を配信しているサーバ側で CORS (オリジン間リソース共有) が有効になっている必要がある。ここではクライアント・サーバ双方でどういった対応が必要かを記載する。

また、サーバが認証を必要とするかしないかでも対応は変わってくるため、それぞれ分けて説明する（認証を必要としない場合がほとんどだと思われるが）。

認証を必要としない画像の場合
------------------------------------------------------

クライアント側は ``img`` 要素に ``crossOrigin="anonymous"`` 属性を設定する。

.. code-block:: html

  <img crossOrigin="anonymous" src="http://example.org/some.image.png" />

これにより画像のリクエストが CORS リクエストになり、サーバ側でアクセス許可されていればキャンバス汚染を回避できる。

サーバ側は ``Access-Control-Allow-Origin:`` ヘッダをレスポンスに付与し、アクセスを許可する対象のオリジンを示す。

- 特別な理由がなければ ``Access-Control-Allow-Origin: *`` で全てのオリジンに対してアクセス許可して良いと思われる。詳しくは `Access-Control-Allow-Origin - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Access-Control-Allow-Origin>`_ を参照いただきたいが、許可するオリジンをリスト管理するような細かい制御はサーバ側でなんらかのコードを書く必要がありそうに見える。

Canvas汚染の回避、というだけの話なら余談になるが、anonymous の場合はブラウザは画像を配信しているドメインの cookie を持っていても、リクエストにそれを付与しない。また、レスポンスで ``Set-Cookie`` が返ってきても、ブラウザはそれを無視する。 [1]_

- ただし、同一オリジンのリクエストの場合は cookie を付与し、レスポンスの ``Set-Cookie`` も受け付ける

認証を必要とする画像の場合
------------------------------------------------------

ここでいう「認証」は Cookie を使った認証、HTTP認証、TLS クライアント認証のいずれかを指す。

この場合、クライアント側は img 要素に ``crossOrigin="use-credentials"`` 属性を設定する。

.. code-block:: html

  <img crossOrigin="use-credentials" src="http://example.org/some.image.png" />

ブラウザは 画像を配信しているドメインの cookie を持っていた場合、リクエストにそれを付与する。

- ただし cookie に ``SameSite`` 属性がついている場合は付与されない。
- ブラウザのプライバシー機能で Third-Party Cookie がブロックされる可能性もある。

サーバ側は anonymous と異なる対応が必要になる。

- ``Access-Control-Allow-Origin:`` ヘッダは呼び出し元のオリジンを明示する必要がある

  - credentials フラグ付きの場合、 ``Access-Control-Allow-Origin: *`` だとブラウザ側で読み込みブロックされる [2]_

- ``Access-Control-Allow-Credentials: true`` ヘッダを返す [3]_

use-credentials は例えば認証付きのCDNのコンテンツをデータ処理するときなどに利用できそうだが、コンテンツのリクエストをする前に別オリジンの認証を行う（Cookieを受け取る）必要があり、使い道は限定されそうなイメージ。

以下余談
===========================

そもそも、なんの対策なの？
----------------------------

例えば個人資産の推移グラフなど、画像自体に機密情報が含まれる場合に第三者に画像データが送信されることを防ぐ。

現代ではブラウザでグラフ表示する場合、 WebAPI で json のデータを取得してクライアントサイドでレンダリングという実装方法が一般的に思われるが、サーバ側で画像を生成して返すという方法も可能である（昔はこちらの手法がよく使われていた）。

機密が含まれる画像のデータが簡単に取れてしまうとそのままリクエストで外部に飛ばされてしまうので、Canvas汚染によってそういった攻撃を防ぐ。

ちなみに
-----------

imgの ``crossOrigin`` が未指定の場合、画像取得のリクエストにcookieは付与される。

- ``img.src`` にユーザが任意のURLを入力できる場合(そんなんやらん方がいいと思うが)、 ``crossorigin="anonymous"`` にしないと CSRF攻撃の攻撃用Webページとして利用される可能性がある(実際のところ攻撃対象が相当脆弱じゃないと問題にはならないと思われるが)。
- 外部の画像サーバがレスポンスに ``Set-Cookie`` を乗っけてきた場合この「Third-Party Cookie は何？」と言うのをGDPR対応としてユーザに説明する責任が発生する（ハズな）ので、可能なら ``crossorigin="anonymous"``  にしておいた方がユーザのプライバシー守っている感が出る。ただしCDNなどはCookieを最適化に利用していたりするので、配信元のポリシー・仕様など確認して判断する必要はある。

検証コード
=============

- https://github.com/ykrods/note/tree/master/src/posts/2019/10/09/

参考
=====

- `Get image data url in JavaScript? - Stack Overflow <https://stackoverflow.com/questions/934012/get-image-data-url-in-javascript>`_
- `Access-Control-Allow-Origin - HTTP | MDN <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Origin>`_
- `Access-Control-Allow-Credentials - HTTP | MDN <https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Access-Control-Allow-Credentials>`_

.. rubric:: Footnotes

.. [1] https://www.w3.org/TR/cors/#omit-credentials-flag
.. [2] `Reason: Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*' - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials>`_
.. [3] `Reason: expected ‘true’ in CORS header ‘Access-Control-Allow-Credents' - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/CORS/Errors/CORSMissingAllowCredentials>`_
