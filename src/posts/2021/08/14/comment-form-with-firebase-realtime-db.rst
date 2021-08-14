.. post:: 2021-08-14
   :tags: Firebase, Realtime Database
   :category: JavaScript

.. meta::
  :description: ちょっとした認証不要のコメント欄のようなものを Firebase Realtime Database を使ってつくってみたところ、場末な感じのサイト上ではこれでもいいのでは？というものになった。


================================================================================
認証不要のコメントフォームを Firebase Realtime Database でつくる場合のルール例
================================================================================

ちょっとした認証不要のコメント欄のようなものを Firebase Realtime Database を使ってつくってみたところ、場末な感じのサイト上ではこれでもいいのでは？というものになった。

つくるもの
=============

ブログのコメントフォーム（のようなもの）

* 認証不要でコメントでき、コメントに対していいね的なこともできる
* 仕事ではなく趣味的なもので利用する

データとルールのポリシー
===============================

* 趣味的なものなので個人情報を扱いたくはないしdbにも入れたくない
* 誰が見ても問題ないデータしかいれないので、 read は基本許可でよい
* 第三者が他人のコメントを書き換えたり、消せたりするのはまずいので write は制限したい

ルール設定(1)
=========================

既にデータがある場合に上書き禁止にする場合は以下のように書く

.. code-block:: json

  {
    "rules": {
      ".read": true,
      "comments": {
        "$comment": {
          ".write": "!data.exists()"
        }
      }
    }
  }

$comment
-----------

まず Realtime Database では通常以下のような key-value 形式で同種のデータを管理する。key の値は `push() <https://firebase.google.com/docs/reference/js/firebase.database.Reference#push>`_ で生成される値を使うか、外部からIDが渡されるようなデータではそれを使うなどする。

::

  "comments": {
    "-XXXXXXXXXXXXXXXXXX1": {
      { "name": "setsuko", "body": "nandehotarusugusindesimaun" }
    },
    "-XXXXXXXXXXXXXXXXXX2": {
      { "name": "seita", "body": "soreohazikiya" }
    },
    ...
  }

``$comment`` はこの任意の key へのマッチャーとなる変数を表す。（変数名は ``$come`` でもなんでもよい

.write ( .read )
---------------------

``.write`` は書き込み許可のルールを記述する特別なキー。上記ルールのように値に式を入れることができ、その評価結果が true なら書き込みを許可する、といったことができる。

* 同じように ``.read`` は読み取り許可のルールを記述する。

data
----------

data は .write / .read (と後述する .validate ) の式で利用できる変数であり、書き込む位置( ``/comments/-XXXXXX1`` など) に保存されているデータを参照できる。

.exists()
-------------

`.exists() <https://firebase.google.com/docs/reference/js/firebase.database.DataSnapshot#exists>`_ は data が何らかの値を持っていれば true を返す

例
-------------

.. code-block:: javascript

  // OK (push は都度新しいkeyを生成する)
  const ref = await db.ref("comments").push({ name: "foo", body: "bar" });

  // 上書き、削除は PERMISSION_DENIED
  ref.set({ name: "hoge", body: "huga" })
  ref.remove();

ルール設定(2): バリデーションの追加
=====================================

\(1\) で上書きは防げるが、データの中身は何でも受け付ける状態になっている

\(1\) にバリデーションを追加すると以下のようになる(名前と本文のみ登録可能にする)

.. code-block:: json

  {
    "rules": {
      ".read": true,
      "comments": {
        "$comment": {
          ".write": "!data.exists()",
          ".validate": "newData.hasChildren(['name', 'body'])",
          "name": {
            ".validate": "newData.isString() && newData.val().length < 20"
          },
          "body": {
            ".validate": "newData.isString() && newData.val().length < 255"
          },
          "$other": {
            ".validate": false
          }
        }
      }
    }
  }

.validate
-------------

``.validate`` も ``.read`` / ``.write`` 同様式を記述し、その式の評価結果が true だったのみ書き込みできるようになる。

* ``.read`` / ``.write`` はより親に近い要素に記述されたものの評価結果が優先されるが、 ``.validate`` は書き込み位置にマッチする全ての ``.validate`` をパスする必要がある

.. note::

  (少し脱線するが重要なので補足) 具体例をあげると、以下のような記述をしても admin_users への書き込みは防げない。 ``.read`` / ``.write`` をネストして書くのは基本的に避けた方がよさそうに思える。

  .. code-block :: json

    {
      "rules": {
        ".write": true,
        "admin": {
          ".write": false,
          "admin_users": ["<管理者のID>"]
        }
      }
    }

newData
-----------

``newData`` は ``data`` と似ているが、書き込みが成功した場合のデータを参照する。

例えば、dbに以下のようなデータが入っているとする。

.. code-block:: json

  {
    "users": {
      "-XXX1": {
        ".validate": "newData ...",
        "name": "Alice"
      }
    }
  }

この db に

.. code-block:: javascript

  db.ref("users/-XXX1").update({ email: "alice@example.com" })

のような操作を行った場合、newData は以下のように既存のデータとマージされた値になる。

.. code-block:: json

  { "name": "Alice", "email": "alice@example.com" }

``#`` 上記のバリデーションではマージうんぬんは関係ないがあとで必要になる

.hasChildren()
------------------

`.hasChildren() <https://firebase.google.com/docs/reference/js/firebase.database.DataSnapshot#haschildren>`_ は、data (newData) が引数で与えられたキーを含んでいることを検証する。

.val()
-----------------

`.val() <https://firebase.google.com/docs/reference/js/firebase.database.DataSnapshot#val>`_ は data (newData) の値を取り出すのに使う。

戻り値は保存されてるデータの型( Object, Array, string, number, boolean or null ) がそのまま帰ってくるので、 str.length や str.matches を使って値の検証ができる。

$other
------------

``$comment`` とおなじ変数だが、この場合上に書いてある "name" / "body" 以外のすべてのキーにマッチすることになる。 "name" / "body" 以外のキーはバリデーションで常に書き込み失敗するので、想定外のデータが入ることを防げる。

ルール設定(3): いいねカウントの追加
========================================

今までのルールにいいねのカウントを保存できるように修正すると以下のようになる。

.. code-block:: json

  {
    "rules": {
      ".read": true,
      "comments": {
        "$comment": {
          ".write": "(!data.child('name').exists() && !data.child('body').exists()) || (data.child('name').val() === newData.child('name').val() && data.child('body').val() === newData.child('body').val())",
          # name, body の validate 部分は同じなので省略
          "fav": {
            ".validate": "newData.isNumber()"
          },
          "$other": { ".validate": false }
        }
      }
    }
  }

`.child() <https://firebase.google.com/docs/reference/js/firebase.database.DataSnapshot#child>`_ で data / newData の子要素の参照を取得し、値が変わっていなければ write を許可するようにした。

前述したように、 newData は既存の値とマージされるので以下のように update で差分更新してもバリデーションをパスできる。

.. code-block:: javascript

  db.ref(`/comments/${key}").update({ fav: 1 })

``#`` もうちょっとスマートにしたい

評価
==========

連続投稿などの対策も必要なのだが、牧歌的な環境ではまぁ問題にはならないでしょということでとりあえずヨシとする

* 匿名で連投に対応するには承認制とかにしないと無理ではと思うが(bot相手ならreCapcha で対応できるが)、問題起きてからでいいかなと

気になることメモ
===================

* Anonymous ユーザを作ってしまった方がスッキリする可能性はあるが、ローカルにユーザ識別情報を入れる時点でプライバシーポリシーとか真面目にやる必要がでるのでは？（気にしすぎな感もあるが）

* 仮に業務で使う場合に、なにかよろしくない投稿があったとして、発信者情報開示請求(法的請求)とかっていう話になった場合に「私はしらないしIP等保存してないので、Firebase (google) に聞いてね」で済むのか？

  * Firebase を利用する開発者は何らかのサーバ側の実装をしないと 投稿者のIPはとれないのでそこまでする必要があるかっていう話と、そんな面倒なことをすることを Firebase 側がユーザに期待してはいないと思うので、多分「聞いてね」でいいんだと思われるが、そもそも匿名投稿自体がユースケースとして主流ではない説もある

* 今回既存のものがあったので Realtime Database を使っているが、Firestore の方が主流な感があるのと、ルール周りは Firestore の方が設定しやすそうな雰囲気がある

検証コード
============

(ルールを書き換えながら検証しているすると検証コードが悪いのかルールの記述を間違えているのか分からなくなることが多発したので、テストコードを書いた

https://github.com/ykrods/note/blob/master/src/posts/2021/08/14/code

補足: 削除許可について
========================

チュートリアルには ``".write": "!data.exists() || !newData.exists()"`` という例があるが、これは上書きは禁止するが削除は許可するというルールになる。

Firebase Realtime Database では ``remove()`` と ``set(null)`` が等価であり、 newData が存在しない == 削除オペレーション ということになるのだが、初見では少しわかりにくい。

参考
=======

- `Firebase Realtime Database <https://firebase.google.com/docs/database>`_
