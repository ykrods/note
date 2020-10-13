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

この記事では Sphinx あるいは Docutils の拡張の開発者向けに、最低限必要な知識と現状の知見をまとめた。知見と言っても既存の Sphinx 拡張を Docutils だけで利用できるように改変したり、拡張のバグを修正した程度なので Sphinx に慣れてる人には目新しいことは特にないと思われる。が、自分が無知識で挑んでハマったり調査に時間がかかったので記録として残すことにした。

前提知識
=========

Sphinx, Docutils, reStructured Text の関係と、それぞれのドメインで拡張の開発に必要な用語を表にまとめる。

* reStructuredText は軽量マークアップ言語の一つであり、拡張可能な構文を有している。
* Docutils は reStructuredText のパーサであり、拡張に対して独自の処理を加えることができる。
* Sphinx は Docutils を拡張し、ドキュメントを構成できるようにしたもの

  * Docutils は基本的に rst ファイルを独立した文書として扱うが、Sphinx は別ファイルへの参照など、ファイル間の繋がりも扱うことができる
  * Sphinx の機能の多くが Docutils の拡張として定義されており、Sphinx ユーザが Sphinx にさらに拡張を加えることができるようになっている。

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
:Visitor (Translator): ノードを指定された形式に変換するクラス。 visit と depart を実装する

Sphinx 用語

:Application (app): Sphinx自体。拡張を追加するインターフェイスとなるクラス。
:Environment: ビルド環境。 doctree とともにキャッシュされる。
:config: ビルド設定
:builder: ビルドする人

知見
========

* キャッシュが有効な場合、 ``Directive.run`` が呼び出されない

  * `チュートリアル` に書いてあるが、Sphinx は rstファイルをパースした結果を ``.doctree`` ディレクトリ以下にキャッシュする。キャッシュが有効な場合、rstのパース処理をスキップする（おそらくrstファイルの更新日時を見ている）ので、 ``Directive.run`` が呼び出されなくなる
  * 対応としては ``sphinx-build`` コマンドに ``-E`` オプションを渡すか、単純に ``.doctree`` ディレクトリを消す。
  * 余談だが environment は拡張の実行時のバージョンも保持しており、その情報は再ビルド時のキャッシュの有効判定に利用される。このことから ``setup`` 関数で返す拡張のバージョン情報は適切に更新した方がよいと言える。

* printデバッグする時は、 ``sphinx-build`` コマンドに ``-v`` オプションをつける

  * デフォルトの verbosity=0 ( ``-v`` 無し) の状態だと進捗表示をしている一部のログ出力でキャリッジリターンを使っていて、 ``print`` 出力が正しく表示されない・上書きされて見れないことがある

* ログ出力は、 ``sphinx.util.logging`` を使う

  * docstring に拡張でも使って良いように書いてある
  * Sphinx は root ロガーには何も手をつけず、 ``sphinx`` ロガーを定義している。わざわざ独自のロガーを設定するよりは乗っからせてもらうのが良いだろう
  * debug ログは `-vv` 以降で出力されるが、 debug ログはかなり色々出る

参考
=====

* https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html
* https://docutils.sphinx-users.jp/docutils/docs/ref/rst/restructuredtext.html#inline-markup
* https://docutils.sourceforge.io/docs/ref/doctree.html
* https://www.sphinx-doc.org/ja/master/development/tutorials/helloworld.html
+ https://www.sphinx-doc.org/ja/master/extdev/index.html
