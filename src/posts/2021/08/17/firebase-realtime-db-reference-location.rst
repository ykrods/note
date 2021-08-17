.. post:: 2021-08-17
   :tags: Firebase, Realtime Database
   :category: JavaScript

.. meta::
  :description: 結論としてはそんなに知らなくても良かった Firebase Realtime Database の小ネタ


=======================================================================
[Firebase Realtime Database] read/write ルールの評価は参照位置が基準
=======================================================================

結論としてはそんなに知らなくても良かった Firebase Realtime Database の小ネタ

はじめに
============

Firebase Realtime Database の ``.write`` ルールが set / update 時にどのように適用されるのかを調べて、 ``.write`` をどう使うかを少し考えてみました。

基本的な API や使い方はこの記事では扱わないので前回の :ref:`comment-form-with-firebase-realtime-db` か `チュートリアル <https://firebase.google.com/docs/database/web/start>`_ を参照ください。

.. warning::

  チュートリアルに明確な記述がなさそうなので、挙動を見て多分こういうことだろうということを書いています。

set の権限の解決
===================

以下のルールがあるとします。

.. code-block:: json

  {
    "rules": {
      "themes": {
        "$theme": {
          "color": {
            ".write": true,
            ".validate": "newData.isString()"
          },
          "backgroundColor": {
            ".write": true,
            ".validate": "newData.isString()"
          }
        }
      }
    }
  }

このとき、次の操作は(それぞれのキーで書き込み許可されているにも関わらず) PERMISSION_DENIED エラーになります。

.. code-block:: javascript

  await db.ref("themes/dark").set({
    color: 'white',
    backgroundColor: 'black',
  }); // => PERMISSION_DENIED

これは、Firebase Realtime Database の読み書きの権限チェックはあくまで操作対象となる ``参照 (Reference)`` に対して行われるということだと思われます。言い換えると ``set`` されるオブジェクトのキー値にマッチする ``.read / .write`` ルールがあったとしても、そのルールは適用されません。 [1]_

おそらく内部的には以下のような流れで書き込みの可否を決定していると思われます。

1. 書き込み位置( ``/themes/dark`` )に対して root から順に ``.write`` ルールを捜索 [2]_

   ::

     /
     /themes
     /themes/$theme ( dark が変数 $theme にマッチ)

2. 最初に見つかった ``.write`` の式を評価し書き込み可能かどうかを判定
3. ``.write`` が見つからない場合は書き込み不可

この裏付けとして、参照するパスを下げて個別に set を実行すると、書き込みに成功します。

.. code-block:: javascript

  await db.ref("themes/dark/color").set("white"); // => SUCCESS
  await db.ref("themes/dark/backgroundColor").set("black"); // => SUCCESS

update の場合
=================

では次の update 操作は失敗するのかというと、これは予想に反して成功します。

.. code-block:: javascript

  await db.ref("themes/light").update({
    color: 'black',
    backgroundColor: 'white',
  });  // => SUCCESS

なぜかというと、update には multi-location updates [3]_ という、名前の通り複数の位置に一括で更新をかけることができる機能があり、内部的には update に渡すオブジェクトのキーがそれぞれ参照として扱われているためだと思われます。つまり、以下のコードと同等ということになります。

.. code-block:: javascript

  await db.ref().update({
    "themes/light/color": "black",
    "themes/light/backgroundColor": "white",
  }); // => SUCCESS

このように書くと、set を個別に実行するのと同じなので同じように成功する、ということが理解できます。

上記踏まえてどうするか
=========================

同じエンティティ（データの塊）の一部の属性のみ書き込み権限を変えたい、という場合に ``.write`` を分けて記述できるのか？ということを考えたのですが

メリット

* ルールが読みやすくなる

デメリット

* set が使えなく(使いづらく)なる
* delete が使えなく(使いづらく)なる

  * ``db.ref('themes/light').remove()`` は write 権限がないので失敗します。個別にフィールド( 例であれば color, backgrounColor ) を消していけば消せないことはないですが、確実に面倒になります。

ということでデメリットが大きいので、基本的には属性レベルでなくエンティティレベルで ``.write`` を記述する方が良さそうですね。

``#`` 非正規化データ(入れ子)を含む場合に入れ子のデータのみ書き込みを認めるとかを親の ``.write`` で管理するのは辛そうですが、そういう場合は正規化するのだろうか。

感想
========

多分こういうことだと思いますが、なにか公式の解説とかあったらコメントいただけると幸いです。

.. rubric:: Footnotes

.. [1]  ``.validate`` 場合は常に検証されます。
.. [2] Firebase Realtime Database はより浅い階層の ``.read / .write`` が優先されます
.. [3] `The Firebase Blog: Introducing multi-location updates and more <https://firebase.googleblog.com/2015/09/introducing-multi-location-updates-and_86.html>`_
