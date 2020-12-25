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

対象のimg要素に ``crossorigin`` 属性を指定し、CORSリクエストを行い、サーバからアクセス許可をもらう。

``crossorigin`` 属性は ``anonymous`` と ``use-credential`` の属性値を持つ。

認証を必要としない画像の場合
------------------------------------------------------

``crossorigin`` 属性を ``anonymous`` に設定する。

.. code-block:: html

  <img crossOrigin="anonymous" src="http://example.org/some.image.png" />

この時、ブラウザは画像を配信しているドメインの cookie を持っていても、リクエストにそれを付与しない。また、レスポンスで ``Set-Cookie`` が返ってきても、ブラウザはそれを無視する。 [1]_

- ただし、同一オリジンのリクエストの場合は cookie を付与し、レスポンスの ``Set-Cookie`` も受け付ける

サーバ側は ``Access-Control-Allow-Origin:`` ヘッダでアクセスを許可していることを明示する。

- 特別な理由がなければ ``Access-Control-Allow-Origin: *`` で全てのオリジンに対してアクセス許可して良いと思われる。詳しくは `Access-Control-Allow-Origin - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/Headers/Access-Control-Allow-Origin>`_ を参照いただきたいが、許可するオリジンをリスト管理するような細かい制御はサーバ側でなんらかのコードを書く必要がありそうに見える。

認証を必要とする画像の場合
------------------------------------------------------

cookieを使った認証、あるいは HTTP認証  [2]_ が必要な場合、 img 要素の ``crossorigin`` 属性を ``use-credentials`` に設定する

.. code-block:: html

  <img crossOrigin="use-credentials" src="http://example.org/some.image.png" />

この時、ブラウザは 画像を配信しているドメインの cookie を持っていた場合、リクエストにそれを付与する。

- ただし cookie に ``SameSite`` 属性がついている場合は付与されない。

サーバ側は anonymous と異なる対応が必要になる。

- ``Access-Control-Allow-Origin:`` ヘッダは呼び出し元のオリジンを明示する必要がある

  - credentials フラグ付きの場合は ``*`` だとブラウザ側で読み込みブロックされるため [3]_

- ``Access-Control-Allow-Credentials: true`` ヘッダを返す [4]_

use-credentials は例えば認証付きのCDNのコンテンツを表示するときなどに利用できそうだが、コンテンツのリクエストをする前に別オリジンの認証を行う（Cookieを受け取る）必要があり、使い道は限定されそうなイメージ。

以下余談
===========================

そもそも、なんの対策なの？
----------------------------

例えば個人資産の推移グラフなど、画像自体に機密情報が含まれる場合に第三者に画像データが送信されることを防ぐ。

ブラウザでグラフ表示する場合 WebAPI で json のデータを取得してクライアントサイドでレンダリングという実装方法の方が多そうに思われるが、サーバ側で画像を生成して返すという方法もある（昔はそうだった）。そういった画像のデータが簡単に取れてしまうとそのままリクエストで外部に飛ばされてしまうので、それを攻撃を防ぐ。

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
.. [2] TSLクライアント証明書 による認証というのもあるらしいが、PWAで使うものらしいのでとりあえず割愛
.. [3] `Reason: Credential is not supported if the CORS header 'Access-Control-Allow-Origin' is '*' - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/CORS/Errors/CORSNotSupportingCredentials>`_
.. [4] `Reason: expected ‘true’ in CORS header ‘Access-Control-Allow-Credents' - HTTP | MDN <https://developer.mozilla.org/ja/docs/Web/HTTP/CORS/Errors/CORSMissingAllowCredentials>`_
