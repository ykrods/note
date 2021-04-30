======================================================================
[調査メモ] iframe で信頼できないリソースを表示する + Service Worker
======================================================================

Work In Progreess


モチベーション
==================

* ユーザ入力から html を生成し、それを iframe で表示したい
* ユーザには js の入力は不可能としたいが、生成された html を js で操作はしたい

  * 例) 生成された html のクリックイベントをハンドリングする

* 生成された html は画像を表示できるが、画像データは Service Worker から返させたい

調査内容
=========

* 攻撃方法を整理する
* sandboxed iframe でどのような制約が加えられるかを確認する
* iframe 内での Service Worker の動作について確認する

iframe の攻撃
==============

iframe関連の一般的な攻撃パターンとしては以下に分けられるが、今回は後者がメインになる。

* 攻撃の対象ページを iframe.src に指定して外側から攻撃を仕掛ける
* iframe を利用しているページに対して iframe.src の内側から親コンテンツに攻撃を仕掛ける

内側からの攻撃
----------------

1. window.parent

   * same-origin の場合 window.parent で親の window にアクセス可能であり、割と好き放題できる

     * 親ページ上で任意の js を実行できる
     * => 親ページから情報を取得する・親ページを改変・偽造する・別ページに飛ばす etc..

   * cross-origin の場合 window.parent への操作はブロックされる（例外がとぶ）

2. cookie

   * same-origin ならアクセスできるし、違うならできない
   * ``document.cookie`` で cookie を参照・改変する
   * iframe 関係なく httpOnly にしておけば良い

3. localStorage / indexedDB

   * same-origin ならアクセスできるし、違うならできない

4. fetch

   * iframe 内で挙動が変わることはないが、通常のように相手側で CORS が有効になっている必要がある

5. iframe

   * iframe の中で iframe を記述(入れ子)にし、src に親の URL を指定する

     * same-origin の場合 iframe.contentWindow で好き放題できる
     * そもそも iframe を書けないようにした方が良い > サニタイズが必要

   * 親側は `Content-Security-Policy` ( `X-Frame-Options` ) を指定しておく

     * これは一般的な外側からの攻撃に対しても有効

sandbox
=========

iframe には sandbox という属性があり、子のコンテンツに制約を加えることができる。

* sandbox 属性は外したい制約を値に空白区切りで書く形になる(例: ``sandbox="allow-popups"`` )
* ``sandbox="allow-scripts"`` で js の実行を許可する

  * window.parent や cookie / storage へのアクセスは制限される
  * window.location の書き換えは可能 > これサニタイズしないとダメでは

* ``sandbox="allow-same-origin"`` で cookie での認証が必要なページを表示する

  * js実行できないのでこれしかユースケースが思いつかないが、何かある？

* ``sandbox="allow-scripts allow-same-origin"`` この設定は sandbox を指定しない以上にセキュリティが緩くなるのでやってはいけない

* sandbox環境で fetch を実行した場合 origin が null になるので(レスポンス自体は返ってくるが) fetch に失敗する

  * ``TODO:`` これ ``Access-Control-Allow-Origin: *`` したらどうなる？

srcdoc
=========

また、iframe には srcdoc という属性があり、html を直接かける。

この時

* 内部的な URL は ``about:srcdoc``
* オリジンは ``null`` (名称としては opaque origin で location.origin の値が null)

となる。

親は通常 not null (まぁ ``"localhost"`` など) であり、 親オリジン !== null でアクセスできないかと思いきや、アクセス可能。

これは、HTML の仕様で sandbox が指定されていない場合は親ドキュメントと same-origin 扱いになるため( ``XXX:`` 表現が不正確感)

* ``TODO:`` browsing context (iframe の親ドキュメントや window.open など）の整理

要は srcdoc の場合 ``window.parent`` などなどにアクセス可能なので、信頼できない html を js 実行可能な状態で iframe で表示するには ``sandbox="allow-scripts"`` が必要になる

Service Worker
=================

* Service Worker はページ（クライアント）ごとに有効・無効が決まる
* 別オリジンのページで Service Worker を有効にする手段はないらしい
* Service Worker 起動中に iframe でページを開いた場合、中身が same-origin ならService Worker が有効になる
* sandbox 環境では ``allow-same-origin`` が指定されていて、中身が same-origin であれば Service Worker が有効になる

  * Service Worker を使うのに allow-same-origin が必要 = allow-script できない = sandbox化できない

* srcdoc を使った場合、仕様上は親と same-origin なので Service Worker が使えるはずだが、現状 firefox しか Service Worker が利用できない

  * chrome はバグ扱いだが、修正される見込みは結構なぞ
  * srcdoc + sandbox については、多分仕様が決まっていないしどのブラウザでも Service Worker が利用できない

    * cookie やら localStorage と同じ扱いだと sandbox 環境では使えないという整理になるが、Service Worker は保護するべき対象という感じではないので使える流れにならんかなぁ
    * (追記) Service Worker から保護するべき localStorage などへのアクセスが可能だから、手放しで許可はできないよねって感じなのかな

結論
=======

* ``sandbox="allow-scripts"`` する場合は意図してないスクリプトが入ってないか、サニタイズ必要
* 信頼できないコンテンツに対して ``sandbox="allow-scripts"`` なiframe + Service Worker という組み合わせは現状両立できない

  * sandboxしなくてもいいレベルでサニタイズできるなら iframe 自体必要ないはずなので現状では Service Worker の方を諦める判断になる？
  * DOMPurify 使っとければええねんという感も

issue と実装状況
==================

* https://github.com/w3c/ServiceWorker/issues/765

  * Firefox は srcdoc の frame (?) で親の Service Worker コントローラーを継承させている
  * 実際動かしたら動いてたが、 sandbox にすると動かなくなる ( allow-same-origin でも同様)
  * https://github.com/whatwg/html/pull/3725 これっぽい（2018年)
  * 継承の仕様を整理しているところ？

* https://github.com/w3c/ServiceWorker/issues/1390

* https://bugs.chromium.org/p/chromium/issues/detail?id=880768

  * chrome でバグ扱いなので、方向的には修正される（Firefox と同じ挙動になる？）のか？

* https://github.com/w3c/ServiceWorker/issues/612

  * https://github.com/w3c/ServiceWorker/commit/7c48f80ee1b09a5e3a11e01c44b6a5631c6ccd95

    * ここで仕様決めたっぽいが、このコミットからファイルとか mv されてるっぽくてここの記述が消滅している ( 現仕様で browsing context で説明されているのと言ってることは同じ？）

    * https://www.w3.org/TR/service-workers/
    * https://w3c.github.io/ServiceWorker/
    * 2.4.1. The window client case

後で読む

* https://lists.w3.org/Archives/Public/public-webappsec/2016Jan/0113.html
* https://github.com/cure53/DOMPurify
* https://w3c.github.io/webappsec-trusted-types/dist/spec/ trusted-types
