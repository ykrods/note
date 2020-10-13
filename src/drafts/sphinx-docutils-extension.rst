.. post::
   :tags: Sphinx
   :category: Python

.. meta::
  :description:

====================================================
Sphinx (Docutils) の拡張を触って得た知見
====================================================

はじめに
=========

Sphinx あるいは Docutils の拡張の開発者向けに、最低限必要な知識と現状の知見をまとめたもの

内容

* Sphinx と Docutils / reStructued Text の関係を整理し、開発に必要な概念（用語）がどのドメインに属しているかを整理する
* 拡張をデバッグしながら動かす際の注意点とロガーの書き方について触れる

知見と言っても既存の Sphinx 拡張を Docutils だけで利用できるように改変したり、拡張のバグを修正した程度だが、自分が無知識で挑んでハマったので記録として残すことにした

前提知識
=========

* Sphinx は Docutils を拡張してドキュメントを構成できるようにしたもの

  * Docutils は基本的に１つの rst ファイルを対象に変換を行うが、Sphinx はファイルの集合を対象にする

* reStructuedText 自体が拡張可能な仕様なので、Docutils が拡張可能であり、 Sphinx は Docutils を拡張しつつ、Sphinx もまた拡張可能なツールになっている

  * つまるところ、ソースコードを読む時は Sphinx と Docutils と関連する Sphinx拡張のコードを行ったり来たりする必要があり、それなりに複雑

用語
-----

reStructuredText 用語

:Directive: 文章構造（ブロック要素）を記述する仕組み。例えば図・テーブル・注釈など。ディレクティブは独自に定義できる。
:Role: 解釈済みテキスト（インライン要素）を記述する仕組み。例えば強調やハイパーリンクなど。ロールも独自に定義できる

Docutils 用語

:Document Tree (doctree): 1つのrstファイルを構造化文章として解釈したもの
:Node: doctree に存在する文書の構成要素
:Transform: doctree 内の「未解決」な要素を解決する仕組み（詳しくは後述）
:Writer:

Sphinx用語

:app:
:Environment:
:config:
:builder:

知見
========

* キャッシュが有効な場合、 ``Directive.run`` が呼び出されない

  * `チュートリアル` に書いてあるが、Sphinx は rstファイルをパースした結果を ``.doctree`` ディレクトリにキャッシュする。キャッシュが有効な場合、rstのパース処理をスキップする（おそらくrstファイルの更新日時を見ている）ので、 ``Directive.run`` が呼び出されなくなる
  * 対応としては ``sphinx-build`` コマンドに ``-E`` オプションを渡すか、単純に ``.doctree`` ディレクトリを消すのが良いようだ。
  * 余談だが environment は拡張の実行時のバージョンも保持しており、そのバージョンは再ビルド時のキャッシュの有効判定に利用されるため、拡張のバージョンは適切に更新した方がよい

* printデバッグする時は、 ``sphinx-build`` コマンドに ``-v`` オプションをつける

  * デフォルトの verbosity=0 ( ``-v`` 無し) の状態だと進捗表示をしている一部のログ出力でキャリッジリターンを使っていて、 ``print`` 出力が正しく表示されない・上書きされて見れないことがある

* ログ出力は、 ``sphinx.util.logging`` を使う

  * docstring に拡張でも使って良いように書いてある
  * 実用上でも、Sphinx は root ロガーには何もせず、 ``sphinx`` ロガーになんか色とかつけてる. わざわざ独自のロガーを設定するのも手間なので、乗っからせてもらうのが良いだろう
  * debug ログは `-vv` 以降で出力されるが、 debug ログはかなり色々出る

参考
=====

https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html
https://docutils.sphinx-users.jp/docutils/docs/ref/rst/restructuredtext.html#inline-markup
