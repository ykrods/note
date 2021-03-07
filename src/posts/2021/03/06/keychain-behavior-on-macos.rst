.. post:: 2021-03-06
   :tags: keychain, macOS
   :category: DesktopApp

.. meta::
  :description: Security.framework でキーチェーンを操作する方法を調べていたが、仕様とか概念レベルのことからして公式のドキュメントを読んでもよくわからなかったので、コードを書いて挙動を確認することにした。


==================================
macOS でのキーチェーンの挙動
==================================

Security.framework でキーチェーンを操作する方法を調べていたが、仕様とか概念レベルのことからして公式のドキュメントを読んでもよくわからなかったので、コードを書いて挙動を確認することにした。

文章としてはとりあえず動かしたりキーチェーンアクセスをいじったり色々読んだ結果を先にまとめて、後ろに検証で使ったコードをおく形をとる。

.. note::

  iOS では単一のキーチェーンしか対応していないため [1]_ 、この文章の内容はあまり関係ない

まとめ
========

キーチェーン
---------------

* macOS ではキーチェーンを複数持つことができる。例えばキーチェーンアクセスを開くと左上のリストに「ログイン」と「システム」があるが、これらも別々のキーチェーン。
* キーチェーンには「パスワード」「証明書（＋秘密鍵）」「秘密メモ」などの要素を格納できる

キーチェーンのロック
----------------------

* キーチェーンはロック・アンロックの状態を持つ。キーチェーンに設定されたパスワードを入力してアンロックを行う。

  * キーチェーンアクセスで南京錠のマークが開いたり閉じたりするが、これはロック状態を表している

* キーチェーンのロック状態はコネクション（セッション？）単位でなく、システム単位で持つ

  * つまり、あるキーチェーンをあるアプリでアンロックしたのち、別のアプリでキーチェーンを開いた場合、既にアンロック状態になっているということ

キーチェーンの設定
---------------------

キーチェーン単位で以下の項目が設定できる [2]_

* 一定時間操作がなかった場合に自動的にロック（デフォルトでは５分間）
* PCがスリープ状態になった場合に自動的にロック
* パスワードの再設定

キーチェーンの実装
-------------------

* キーチェーンは内部的には SQLite ベースの db として実装されている [3]_ 。ファイルは ``~/Library/Keychains/`` 以下に配置される。
* キーチェーンは単なるファイルだが、キーチェーンのAPI (Security.framework) は直接ファイルを開くような実装にはなっておらず、securityd というデーモンに対してやりとりする形になっている [4]_

  * ロック状態は多分（おそらく） securityd が持っている

キーチェーンの要素
---------------------

* キーチェーンには「パスワード」「証明書（＋秘密鍵）」「秘密メモ」などの要素(データベース的に言えば行）を格納できる
* キーチェーン要素はパスワードや秘密鍵といった秘匿対象のデータの他、項目名や種類などのメタデータ（データベース的に言えば列）を持つ
* キーチェーン要素は検索できる。キーチェーンを指定しないで検索した場合、securityd に登録されている全てのキーチェーンが検索対象になる
* 要素単位でアクセス制御の設定ができる。設定内容としては以下がある

  * 全てのアプリケーションに要素の使用を許可
  * 特定のアプリケーションに要素の使用を許可
  * 許可する前にパスワード入力を要求

* アプリケーションからキーチェーンに要素を追加した場合、自動的にそのアプリケーションがアクセス許可される

アンロック・アクセス許可の要不要
-----------------------------------

後述のコードで実際の挙動を確認しつつ、どの条件でパスワード入力が求められるかを表にまとめた。

.. csv-table::
  :header-rows: 1
  :widths: 20,30,25,25

  対象            , 操作                     , アンロック, 要素のアクセス許可
  キーチェーン    , 開く                     ,           ,
                  , ロック                   ,           ,
                  , アンロック               ,           ,
                  , 新規作成                 , ``(*1)``  ,
                  , 削除                     ,           ,
                  , 設定変更                 , o         ,
  キーチェーン要素, 検索(メタデータのみ)     ,           ,
                  , 検索(秘匿データ含む)     , o         , o
                  , 追加                     , o         ,
                  , 更新(アクセス制御の変更) , o         , o
                  , 削除                     , ``(*2)``  ,

* ``(*1)`` キーチェーンの新規作成ではパスワード入力が必要で、作成直後はアンロック状態になる
* ``(*2)`` キーチェーンアクセスから要素を削除しようとするとアンロックが必要になるが、コードからだとロック状態でも削除できる（よくわからない）
* アクセス許可が必要な操作では、アプリがアクセス許可されていてもアンロックは必要になる

.. note::

  削除がアンロック（パスワード入力）無しでできてしまうが、まぁ実態がファイルなのでどのみちファイルを消されたらどうしようもないというのがあると思われる。 [5]_

検証コード
===========

``# XXX:`` 個人的な事情で Objective-C で書いたが、Swift の方が楽だった感がある

キーチェーンの作成
---------------------

.. literalinclude:: code/keychain-create.m
  :language: objective-c
  :caption: keychain-create.m

キーチェーンの削除
--------------------

.. literalinclude:: code/keychain-delete.m
  :language: objective-c
  :caption: keychain-delete.m

キーチェーンのロック
-------------------------

.. literalinclude:: code/keychain-lock.m
  :language: objective-c
  :caption: keychain-lock.m

キーチェーンのアンロック
--------------------------

.. literalinclude:: code/keychain-unlock.m
  :language: objective-c
  :caption: keychain-unlock.m

キーチェーンの状態取得
-------------------------

.. literalinclude:: code/keychain-getstatus.m
  :language: objective-c
  :caption: keychain-getstatus.m

要素の追加
-----------

.. literalinclude:: code/keychain-item-add.m
  :language: objective-c
  :caption: keychain-item-add.m

要素の削除
-----------

.. literalinclude:: code/keychain-item-delete.m
  :language: objective-c
  :caption: keychain-item-delete.m

要素の検索(メタデータのみ)
----------------------------

.. literalinclude:: code/keychain-item-list.m
  :language: objective-c
  :caption: keychain-item-list.m

要素の検索(秘匿データ含む)
----------------------------

* 結果に秘匿データを含める場合、アクセス許可が必要になる
* 設計的に、秘匿データをアプリケーションのメモリ上に展開しなくても
  認証等ができるようになっている？（ような雰囲気を感じる）

.. literalinclude:: code/keychain-item-retrieve.m
  :language: objective-c
  :caption: keychain-item-retrieve.m

(おまけ) Makefile
-------------------

.. literalinclude:: code/Makefile
  :language: Makefile
  :caption: Makefile


個人的見解
===========

* まぁ、使うときはアンロックして使い終わったらロックという方針になるかなぁ

  * 要素ごとのアクセス制御があるのでロックしたからなんなんだという感があるが、以下の理由による

    * ロックしてれば大丈夫な類の脆弱性とかあったらしい
    * 自動でロックされる・あるいは他アプリやユーザからロック可能な以上、セキュリティがどうのとは関係なくキーチェーンの状態を確認してアンロックする実装が必要になる

* 預かり知らぬところで削除される可能性があるので、適宜存在確認は必要そう

  * キーチェーンのデータが消えたら積む系の実装は避けた方が良さそう（実際そういうのが必要になった場合にどうすればいいのかは知らんが）

参考
=======

* `Cocoaの日々: [iOS] Keychain Services とは <http://cocoadays.blogspot.com/2011/02/ios-keychain-services.html>`_
* `iOSのSecurity Frameworkのステータスコード逆引き - will and way <https://matsuokah.hateblo.jp/entry/2019/05/24/015823>`_
* `soffes / SAMKeychain <https://github.com/soffes/SAMKeychain/blob/master/Sources/SAMKeychainQuery.m>`_ (アーカイブ済み)

.. rubric:: Footnotes

.. [1] `Keychains | Apple Developer Documentation <https://developer.apple.com/documentation/security/keychain_services/keychains?language=objc>`_
.. [2] キーチェーンアクセスのメニュー > ファイル > キーチェーンの追加 で作成したキーチェーンをキーチェーンアクセスに追加でき、設定を確認できる ( 正確には securityd の search list に追加していると思われるが )
.. [3] `Keychain data protection - Apple Support <https://support.apple.com/en-jo/guide/security/secb0694df1a/web>`_
.. [4] ``man securityd`` にそれっぽいことが書いてある。
.. [5] `Secure Enclave <https://developer.apple.com/documentation/security/certificate_key_and_trust_services/keys/storing_keys_in_the_secure_enclave?language=objc>`_ に鍵を保存した場合は挙動変わる？（未検証）
