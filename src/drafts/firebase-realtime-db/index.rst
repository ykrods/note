==================================================================
認証不要のコメントフォームを Firebase Realtime Database でつくる
==================================================================

ポイント

* ちょっとした認証不要のコメント欄のようなものを Firebase Realtime Database を使ってつくる
* ルール設定を適切に行う必要がある
* 法的な部分がよくわかってないが、場末な感じのサイト上ではこれでもいいのでは

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

具体的なルール設定(1)
=======================

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

以下解説

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

``$comment`` はこの任意の key へのマッチャーとして使う変数を示す。（変数名は ``$c`` でもなんでもよい

.write ( .read )
---------------------

``.write`` は書き込み許可のルールを記述する特別なキー。上記のように値に式を入れることができ、その評価結果が true なら書き込みを許可する、といったことができる。

* 同じように ``.read`` は読み取り許可のルールを記述する。

data
----------

data は .write / .read (と後述する .validate ) の式で利用できる変数であり、書き込む位置の既に保存されたデータを参照できる。

.exists()
-------------

`exists() <https://firebase.google.com/docs/reference/js/firebase.database.DataSnapshot#exists>`_ は data が何らかの値を持っていれば true を返す


``#`` 認証する場合は ``auth`` を使ってユーザ自身が登録したデータなのかを判定する方がよい

バリデーションの追加
=======================

(1) で上書きは防げるが、データの中身は何でも受け付ける状態になっている

(1) にバリデーションを追加すると以下のようになる

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

* ``.read`` / ``.write`` はより親に近い要素に記述されたものの評価結果が優先されるが、 ``.validate`` はマッチする全ての ``.validate`` をパスする必要がある

.. note::

  (少し脱線するが重要なので補足) 例えば以下のような記述をしても書き込みは防げないので注意が必要。

  .. code-block :: json

    {
      "rules": {
        ".write": true,
        "admin_user": {
          ".write": false,
          # 管理者のID
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
        ".validate": "newData ..."
        "name": "Alice"
      }
    }
  }

この db に

::

  $db.ref("users/-XXX1").update({ email: "alice@example.com" })

のような操作を行った場合、newData は以下のような既存のデータとマージされた値になる。

::

  { "name": "Alice", "email": "alice@example.com" }

``#`` 上記のバリデーションではマージうんぬんは関係ないがあとで必要になる



メモ
======

* 匿名用に Anonymous ユーザというのもあるが、ローカルにユーザ識別情報を入れた時点でプライバシーポリシーとか真面目にやる必要がでるのでは？
* 仮に業務で使う場合に、なにかよろしくない投稿があったとして、発信者情報開示請求(法的請求)とかっていう話になった場合に「私はしらないしIP等保存してないので、firebase (google) に聞いてね」で済むのか？

  * firebaseを利用する開発者は何らかのサーバ側の実装をしないと IP とれないのでそこまでする必要があるかっていう話と、運用上の理由でわざわざセンシティブなデータをfirebaseに入れることを firebase 側が期待してはいないと思うので、多分「聞いてね」でいいんだと思われるが

* 連投対策

  * bot は reCapcha で対応する
  * ユーザの手動の連投に対しては IP とるくらいしか有効な手段がないのでは？
  * Anonymous ユーザだとローカルストレージか Cookie かを消せば新しいユーザになれるはず
  * 認証つけてもSNSのアカウントを複数もってる人とかもいるので監べきとはいえない
  * 牧歌的な環境ではまぁ悪い人こないでしょみたいな感じでいいような

~~ ここまでかいた ~~
