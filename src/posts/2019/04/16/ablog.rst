.. post:: 2019-04-17
   :tags: ABlog
   :category: blog
   :author: ykrods

============================================================
ABlog でブログを書く
============================================================

Sphinx でブログを書きたい、というより Sphinx でドキュメントを書く素振りのためにブログでも作ろうということで、 `ABlog <https://ablog.readthedocs.io/>`_ を利用してみました。

( `Tinkerer <http://tinkerer.me/>`_ も検討したが、こちらは今(2019/04/17)時点で Sphinx の新しいバージョンに対応してない模様 [1]_

ABlog
=======

ブログの静的ページを生成する Sphinx 拡張です。具体的には タグ・カテゴリ・最近の投稿リストなどを生成してくれます。atom フィードも作成されますが sitemap は対応してないみたいです。

使い方
=============

https://ablog.readthedocs.io/ の通りでOKです。

記事を書くときは、下記のように reStructuredText の先頭に post ディレクティブを書くだけでOKです。

.. code-block :: rest

  .. post:: 2019-04-17
     :tags: ABlog
     :category: blog
     :author: ykrods

  ============================================================
  ABlog でブログを書く
  ============================================================

  書く

デフォルトの設定だと日付を `Apr 15, 2014` のような表記にする必要がありますが、以下の設定でフォーマットを変更できます。

.. code-block :: python
  :caption: conf.py

  post_date_format = '%Y-%m-%d'

記事のファイルの置き場所もなんでも良いですが、ファイルパスがそのまま slug になるので 私は slugをそれっぽく見せるために

::

  posts/${%Y}/${%m}/${%d}/${title_en}.rst

みたいな規則にしています。

`ablog build` で `_website` 以下に html がビルドされます。

所感
======

ABlog は

* ディレクトリ構造の規則がない
* post ディレクティブを書くだけで記事を作れる

ため覚えることが少なく、シンプルで使いやすい印象です。

ベースが Sphinx なので表示内容やレイアウトをゴリゴリカスタマイズしたい場合は向いてないかもしれません。

元ソースも公開するので参考になれば `ykrods/blog <https://github.com/ykrods/blog>`_

.. rubric:: Footnotes

.. [1] https://github.com/vladris/tinkerer/issues/112 多分これ
