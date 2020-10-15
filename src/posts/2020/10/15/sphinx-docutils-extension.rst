.. post:: 2020-10-15
   :tags: Sphinx
   :category: Python

.. meta::
  :description:

====================================================
Sphinx (Docutils) の拡張を触って得た知識とTIPS
====================================================

はじめに
=========

この記事は Sphinx 拡張あるいは Docutils 拡張の開発にこれから挑む人向けに、ざっくり把握しておきたい知識と現状の私の知見を TIPS としてまとめたものです。知見と言っても既存の拡張のバグを修正した程度なので慣れてる人には目新しいことは特にないと思いますが、自分が無知識で挑んでハマったり調査に時間がかかったので記録として残すことにしました。

公式のドキュメントを読んでいない場合はまずそちらを読まれることをオススメします。

* `Sphinx拡張機能の開発 — Sphinx 4.0.0+/e4e5ee333 ドキュメント <https://www.sphinx-doc.org/ja/master/extdev/index.html>`_
* `"Hello world" 拡張機能の開発 — Sphinx 4.0.0+/e4e5ee333 ドキュメント <https://www.sphinx-doc.org/ja/master/development/tutorials/helloworld.html>`_

知識
=========

reStructuredText, Docutils, Sphinx についてまず整理する。

* reStructuredText は軽量マークアップ言語の一つであり、拡張可能な構文を有している。
* Docutils は reStructuredText をパースして html など別形式に変換するテキスト処理システムであり、  reStructuredText の拡張にも対応している。
* Sphinx は Docutils を拡張し、ドキュメントを構成できるようにしたもの

  * Docutils は基本的に単体の rst ファイルを独立した文書として扱うが、Sphinx は別ファイルへの参照など、ファイル間の繋がりを扱うことができる
  * Sphinx の機能の多くが Docutils の拡張として定義されており、さらに Sphinx ユーザが拡張を行うための独自のイベントフックや、拡張を容易にするAPI群を提供している。

用語
-----

reStructuredText, Docutils, Sphinx それぞれのドメインで拡張の開発に必要な用語をまとめる。

reStructuredText 用語

:Directive: 文章構造（ブロック要素）を記述する仕組み。例えば図・テーブル・注釈など。ディレクティブは独自に定義できる。
:Role: テキストをマークアップする仕組み。例えば強調やハイパーリンクなど。ロールも独自に定義できる。

Docutils 用語

:Document Tree (doctree): 1つのrstファイルを解釈し木構造のデータに変換したもの
:Node: doctree に存在する文書の構成要素。単純にxmlのノードと捉えてしまって良い。
:Transform: doctree 内のノードの変換、追加、削除を行うクラス。（詳しくは後述）
:Writer: doctree を入力として、ファイルの出力を行うクラス。 html や tex 、 manpage など、出力フォーマットごとに定義される
:Translator (Visitor): doctree 内のノードを出力形式ごとのデータに変換するクラス。Writer がそれぞれの Translator を持っている。(詳しくは後述)

Sphinx 用語

:Application (app): Sphinx自体。ユーザが拡張を追加するインターフェイスを提供するクラス。
:Domain: ディレクティブ・ロールのグループ（詳しくは後述）
:Environment: ビルド環境。rst のパース時に得られたデータを保持するところ（詳しくは後述）。
:Builder: パースされたドキュメントを入力として、ファイルの出力やなんらかのデータ処理を行うクラス。docutils の Writer, Translator を利用したり拡張したりしている。


Transform
--------------

Transfrom は doctree 生成後に doctree 内のノードの変換、追加、削除を行う。

Transform の内容は多岐にわたる。デフォルトで適用される Transform が多数あり、役割がよくわからんものも割とあるが、例えば ``docutils.transforms.universal.StripComments`` は ``comment`` ノードを doctree から削除するのに使われる。

また、Sphinx レイヤでの例としては、 ``sphinx.transforms.post_transforms.ReferencesResolver`` がある。前述したように、Sphinx では異なる rstファイルへの参照（クロスリファレンス）が可能だが、参照先が具体的にどこになるか（あるいは実在しているか）は一度全ての rstファイルをパースして見ないことにはわからない。そこで、Sphinx では次の手順をとっている。

1. rstをパースする際に以下の処理を行う

   * ``:ref:`` が出現した場合 ``<pending_xref>`` という一時的なノードを生成する
   * ラベル(例: ``.. _my-ref-label:`` ) が出現した場合、参照先として ``std domain`` にラベル情報を追加する(ドメインについては後述)

2. 全てのrstをパースしたのち、 ``ReferenceResolver`` で ``<pending_xref>`` の解決（変換）を行う。解決には 1. で取集した ``std domain`` のラベル情報を用いる。

* (post_transformsについて) Transform は docutils の機能だが、Sphinx は ``add_post_transform`` というAPIを追加で提供している。transform が1つ1つのrstファイルをパースした後に実行されるのに対して、 post_transform は一度全ての rst をパースし終わった後に再度実行される、ということのようだ。


Translator (Visitor)
----------------------------------

出力形式に合わせてノード単位のデータ処理を行う。例えば、html 出力を行う ``HTMLTranslator`` は title ノードを h1 ~ h6 に変換している。

* docutils で拡張されたノードを扱うには Translator に ``visit_{node_name}`` と ``depart_{node_name}`` 関数をねじ込む

  * この方法は Sphinx の内部実装を参考にしたが、Docutils の拡張として公開する場合は NodeVisitor(Translator), Writer をそれぞれ継承した新しいクラスをつくった方が良いかもしれない（コードがわかりにくくなるので）

  .. code-block:: python

    from docutils import nodes
    from docutils.parsers.rst import (
        Directive,
        directives,
    )
    from docutils.writers.html5_polyglot import HTMLTranslator

    class mynode(nodes.General, nodes.Inline, nodes.Element):
        pass


    class MyDirecitive(Directive):
        required_arguments = 0
        optional_arguments = 0
        final_argument_whitespace = True
        has_content = True

        def run(self):
            node = mynode()
            node['content'] = self.content

            return [node]


    def visit_mynode(self, node):
        content = node['content']
        html = f'<div class="mydirective">{content}</div>'
        self.body.append(html)


    def depart_mynode(self, node):
        pass


    directives.register_directive("mydirective", MyDirective)

    setattr(HTMLTranslator, "visit_mynode", visit_mynode)
    setattr(HTMLTranslator, "depart_mynode", depart_mynode)

* sphinx の場合は簡略化されたAPIが提供されており、 ``app.add_node()`` の引数に ``(visit_.., depart_..)`` のタプルを渡せば良い

  .. code-block:: python

    def setup(app):
        app.add_directive('mydirective', MyDirective)
        app.add_node(mynode, html=(visit_mynode, depart_mynode))


* Translator は Visitor パターンで実装されており、変数名が visitor になっていることもある
* 独自のノードを追加する場合、上記例のような html だけの対応では tex など他の出力でエラーになってしまい、汎用性が失われてしまう。とはいえ全ての形式に対応するのも結構な手間と知識が要求されるため、可能なら既存のノードを応用する方が望ましい。


Environment と Domain
----------------------------------

Environment は rst パース時に得たメタデータなどを保持する。

Environment は(doctreeも同様だが)パース時に ``.doctrees`` ディレクトリ以下にファイルキャッシュされる。キャッシュは単純な Python の pickle データなので、以下のようなコードで内容を確認できる。

.. code-block:: python

  import pickle
  from pprint import pprint

  with open('.doctrees/environment.pickle', 'rb') as f:
      env = pickle.load(f)
      print("docname:", env.docname)
      for domain, data in env.domaindata.items():
          print("domain:", domain)
          pprint(data)

Domain は Sphinx で Python 以外の言語のドキュメントを書けるようにするための機能だが、とりあえずはラベルの情報は ``env.domains["std"].data["labels"]`` に入っているというのを押さえておけば良いと思う。

``#`` ビルド環境が複数のドメインを持っていて、それぞれが専用の Directive / Role を持っていて、ドメインごとに違うメタ情報を持つ。という感じっぽいがよくわかっていない。

Sphinx のイベントフック
----------------------------------------------

Sphinx はビルド中に発生したイベントに対して拡張でコールバック関数を登録できるようになっている。

* Sphinx のビルド流れと、ビルドのフェーズごとに発生するイベントについては以下を参照

  * `アプリケーションAPI — Sphinx 4.0.0+/e4e5ee333 ドキュメント <https://www.sphinx-doc.org/ja/master/extdev/appapi.html#sphinx-core-events>`_

TIPS
========

* キャッシュが有効な場合、独自に定義したディレクティブの ``Directive.run`` が呼び出されない

  * 上にも少し書いたが、Sphinx は rstファイルをパースした結果を ``.doctrees`` ディレクトリ以下にキャッシュする。キャッシュが有効な場合、rstのパース処理をスキップするので、 ``Directive.run`` が呼び出されなくなる
  * 対応としては ``sphinx-build`` コマンドに ``-E`` オプションを渡すか、単純に ``.doctrees`` ディレクトリを消す。
  * 余談だが environment は拡張の実行時のバージョンも保持しており、その情報は再ビルド時のキャッシュの有効判定に利用される。このため ``setup`` 関数で返す ``env_version`` など、拡張のバージョン情報は適切に更新した方がよいだろう。

* printデバッグする時は、 ``sphinx-build`` コマンドに ``-v`` オプションをつける

  * デフォルトの verbosity=0 ( ``-v`` 無し) の状態では、進捗表示をしている一部のログ出力でキャリッジリターンを使っているため、 ``print`` 出力が正しく表示されない・上書きされて見れないと言った問題が起きることがある

* ログ出力は、 ``sphinx.util.logging`` を使う

  * docstring に拡張でも使って良いように書いてある
  * Sphinx は root ロガーには何も手をつけず、 ``sphinx`` ロガーを定義している。わざわざ独自のロガーを設定するよりは乗っからせてもらうのが良いだろう
  * debug ログは `-vv` 以降で出力されるが、 debug ログはかなり色々出る

* Sphinx のイベントハンドラについて、コールバックは他の拡張や Sphinx 本体でも登録されている可能性があるので、その前提で実装を行う。可能なら「そのコールバックで扱うべきイベントかを判定する」ような実装をすると良さそう。

  * 例えば、 ``missing-reference`` イベントはクロスリファレンスが解決できなかった際に発生するが、 ``missing-reference`` をイベントを拾ってコールバックで解決を試みるような実装は ``sphinx.ext.intersphinx`` でされている。 intersphinx のコールバックで解決される可能性があるので、自前のコールバックで参照が解決できなかったとしても例外を投げたりエラーログを残す必要はない。自前のコールバックで解決すべき未解決の参照なのかどうかを判定できるのであれば別。

さいごに
=========

とりあえずTIPSを書いておこうと思って、ついでなので基本知識も整理しておこうと思ったら際限なく広がっていって困った。あとリファレンス周りを自分が触っていたのでそっちに内容が偏った印象があるが、まぁクロスリファレンスを持てるのが Sphinx の特徴なのでちょうど良いでしょう（きっと）。

TIPSの方が少ないので何かしら知見を得たら追記していきたい。

Sphinx のメンテナでいらっしゃる @tk0miya さんが `Inside Sphinx <https://booth.pm/ja/items/1576243>`_ という書籍を出版されているのでそちらも参考になると思います。凄まじい勢いでコントリビュートされている tk0miya さんを応援しよう！

参考
=====

* `reStructuredText Markup Specification <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_
* `reStructuredText マークアップ仕様 — Docutils documentation in Japanese 0.12 ドキュメント <https://docutils.sphinx-users.jp/docutils/docs/ref/rst/restructuredtext.html#inline-markup>`_
* `The Docutils Document Tree <https://docutils.sourceforge.io/docs/ref/doctree.html>`_
* `用語集 — Sphinx 4.0.0+/e4e5ee333 ドキュメント <https://www.sphinx-doc.org/ja/master/glossary.html>`_
* `ファイルを超えてリンクを貼る (domain#resolve_xref() のすゝめ) - Hack like a rolling stone <https://tk0miya.hatenablog.com/entry/2014/07/29/122535>`_
* `Sphinx ではどのようにラベルとキャプションを結びつけているのか - Hack like a rolling stone <https://tk0miya.hatenablog.com/entry/2014/08/11/003957>`_
