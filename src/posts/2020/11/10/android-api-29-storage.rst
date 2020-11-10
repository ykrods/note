.. post:: 2020-11-10
  :tags: Android, Kotlin
  :category: Android

=======================================================================
[memo] Android の getExternalStorageDirectory が非推奨な件の対応例
=======================================================================

Android 10 Q (API level 29) 以降、getExternalStorageDirectory() が非推奨になったので、代替案を模索した

.. meta::
   :description: Android 10 Q (API level 29) 以降、getExternalStorageDirectory() が非推奨になったので、代替案を模索した

はじめに
==========

Android 10 Q (API level 29) 以降、 `getExternalStorageDirectory() <https://developer.android.com/reference/android/os/Environment#getExternalStorageDirectory()>`_ が非推奨になった。同バージョンでは scoped storage という新しい概念が導入され、ストレージのユースケースに合わせた対応が必要になる。

この記事では「アプリがアンインストールされても消えないデータファイルを残したい」という場合について、 MediaStore の実装例があまり見つからなかったのでとりあえず試作したものを載せる。

MediaStore の仕様上の留意事項
===============================

* ユーザがファイルを参照・削除できるので確実にファイルが残るわけではない
* ドキュメントに「アプリ固有のデータはアプリ固有のディレクトリに入れた方が良い」と書いてあるので行儀が悪いかもしれない。

  * が、アンインストール時に一緒に消えないファイルを作りたい場合は MediaStore か Storage Access Framework を利用するしかない（ように見える

権限について確認
=================

scoped storage
------------------

まず、 scoped storage は「最初にファイルを作ったアプリがそのファイルの READ/WRITE 権限を持つ」モデルである。イメージ的にはファイルのオーナーと同じようなものだが、従来のオーナーと区別して「App attribution 」という表記になっている。 [1]_

具体的には scoped storage は以下のような挙動をする

* ファイルの新規作成、およびアプリが所有するファイルの更新については特に権限を必要とせずに行うことができる。

  * 別のアプリが所有する同名のファイルが存在する場合は「foo(1).mp3」のような別名で保存されるのでエラーにはならない

* MediaStore で条件に一致するファイルをクエリする場合、権限のあるファイルのみが検索対象となる

ただし、アプリのパーミッションで ``READ_EXTERNAL_STORAGE``, ``WRITE_EXTERNAL_STORAGE`` 権限が与えられている場合は所有していないファイルも扱うことができる。

* ``XXX:`` Android 11 (API level 30) の場合は READ だけが書いてあるが、WRITE は不要になったのか？

一点注意したいのは、アプリを再インストールした場合は所有権は別扱いになるため、アプリを削除する前に作成したファイルを読み取るには ``READ_EXTERNAL_STORAGE`` 権限が必要になる。

複数バージョン対応
-------------------

いきなり Android 9 (API level 28) 以前を切るというわけにもいかないのでそのための権限が必要になる。

* Android 9 以下か、 `scoped storage をオプトアウト <https://developer.android.com/training/data-storage/use-cases#opt-out-scoped-storage>`_ した状態で動作する場合:

  * (scoped storage は関係なく、従来の権限モデルとして) ``READ_EXTERNAL_STORAGE`` or ``WRITE_EXTERNAL_STORAGE`` 権限が必要

* scoped storage が有効な場合

  * 扱いたいファイルの性質に合わせて、 ``READ_EXTERNAL_STORAGE``, ``WRITE_EXTERNAL_STORAGE`` が必要

今回の場合、getExternalStorageDirectory() で取得したディレクトリ以下のデータを取得してデータマイグレーションすることも視野に入れ、scoped storage をオプトアウトする。 (なので実は scoped storage の所有権とパーミッションについては現状知らなくてよかった)

実装
=======

.. literalinclude:: MainActivity.kt
   :caption: MainActivity.kt
   :language: kotlin

実装上のポイント
--------------------

* コレクションに追加するときは DISPLAY_NAME に拡張子を含まないのにクエリするときは拡張子必要なのが罠

問題点
--------

動作確認していて気づいたが、この実装だと Android 9 (API level 28) の端末で保存できてない

画像用のコレクションであれば

::

  MediaStore.Images.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY)

のようなコードで Uri を取得できるのだが、現時点でドキュメントの場合 ``MediaStore.Documents`` が存在しない [2]_

そのため、この実装では ``RELATIVE_PATH`` で ``DIRECTORY_DOCUMENTS`` を渡しているのだが、 ``RELATIVE_PATH`` が追加されたのが `API Level 29 から <https://developer.android.com/reference/android/provider/MediaStore.MediaColumns#RELATIVE_PATH>`_ なので、それ以前のOSでは動いていない？のか？？

とりあえず、今まで通りの（レガシーの）保存先に置くことはできるが、そうすると Scoped Storage をオプトインした時にそのファイルを読めなくなる。そのためデータのマイグレーションを行うには、アップグレード中はまたどこか別の場所にデータを保存しておくなどを考える必要があると思われる。そこまでやる必要性があるかは今まで外部ストレージに置いていたファイルがどれだけ重要かによってくるので、とりあえずこれ以上は踏み込まない。


その他メモ
===============

* ``MANAGE_EXTERNAL_STORAGE`` という強い系の権限もあるらしいが基本ファイルマネージャーとかそれ系用のものらしいので一般のアプリでは関係なさそう
* パーミッション取得するコードは Android Developer だと ``registerForActivityResult`` 使っているけどこれまだベータリリースなのでは？
* shouldShowRequestPermissionRationale がどういう条件で値が変わるのかよくわからん

Device File Explorer
------------------------

* Android Studio の View > Tool Windows > Device File Explorer で開く
* 以下のパスでファイルが生成されているか確認できる

  * 従来の実装 => ``/storage/emulated/0`` 以下
  * MediaStore => ``/sdcard/`` 以下の決められたディレクトリ以下(この実装では ``/sdcard/Documents/MyApp/data``

    * ただし、 MediaStore を用いる場合は Files アプリからファイルを確認できるので Device File Explorer を使う意味はあまりないかもしれない

* ``/storage/emulated`` 以下が ``ls: /storage/emulated: Permission denied``
  のようなエラーメッセージが表示される場合、ADV Manager で端末リセット(Wipe Data) を行うと解決する場合がある。
  また、 ``/sdcard`` や ``/storage/self/primary`` 等では表示できる場合がある

* 作成したファイル or ディレクトリが表示されない場合、親ディレクトリを右クリック > Synchronize で表示される場合がある

感想
=====

内部ストレージやら外部ストレージやら共有ストレージやら対象範囲別ストレージやらアプリ固有の内外ストレージやらMediaStoreやらコレクションやらStorage Access Framework やら、固有の概念が多くて戸惑った。

参考
=====

公式のドキュメントは日本語と英語で書いてあることが違っていたので英語を参照した(日本語の方が最終更新日が古い）

* `Data and file storage overview  |  Android Developers <https://developer.android.com/training/data-storage#scoped-storage>`_
* `Access media files from shared storage  |  Android Developers <https://developer.android.com/training/data-storage/shared/media#app-attribution>`_
* `Create/Copy File in Android Q using MediaStore - Stack Overflow <https://stackoverflow.com/questions/59511147/create-copy-file-in-android-q-using-mediastore>`_

.. rubric:: Footnotes

.. [1] 帰属するアプリ、というのが意味合い的には近いかと思う
.. [2] そもそも Android 9 (API level 28) では Documents のコレクションが存在していなかった？ ``DIRECTORY_DOCUMENTS`` の定義は `API level 19 からあった <https://developer.android.com/reference/android/os/Environment#DIRECTORY_DOCUMENTS>`_ のだが、単なるファイル置き場みたいな感じだったのだろうか
