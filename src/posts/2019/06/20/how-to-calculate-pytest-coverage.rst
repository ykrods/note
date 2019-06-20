.. post:: 2019-06-20
  :tags: pytest, pytest-cov
  :category: test

==============================
pytest の Coverage の計算方法
==============================

カバレッジはこうやって出すんですよという資料を書いていたら自分がわかっていなかったので調べた話です。

問題
======

以下のサンプルでテストを実行し、 `pytest-cov <https://pypi.org/project/pytest-cov/>`_ でカバレッジを取得した場合、その値はいくつになるでしょう。なお `branch` オプションは無しです。

.. code-block :: text
  :caption: directory layout

  + (current)
    + apps
      + myapp.py
    + tests
      + test_myapp.py

.. literalinclude:: pytest-example/apps/myapp.py
  :caption: myapp.py
  :language: python

.. literalinclude:: pytest-example/tests/test_myapp.py
  :caption: test_myapp.py
  :language: python

テストの実行環境とコマンド

::

  $ python -V
  Python 3.7.1
  $ pip list
  coverage           4.5.3
  pytest             4.6.3
  pytest-cov         2.7.1
  $ pytest --cov-report=term --cov=apps tests

正解
-----

83% です

::

  ----------- coverage: platform linux, python 3.7.1-final-0 -----------
  Name            Stmts   Miss  Cover   Missing
  ---------------------------------------------
  apps/myapp.py       6      1    83%   9

この数値はどこから来たのか
===========================

まず83%という数字自体については、表示されている Stmts=6, Miss=1 からカバーされている割合を出してるとみて良いでしょう。

.. math::

  (Stmts - Miss) / Stmts = 5 / 6 = 0.833...

続いて Stats, Miss の算出方法ですが、 `pytest-cov` は `Coverage.py <https://pypi.org/project/coverage/>`_ を `pytest` で使えるようにしたプラグインなので、 `Coverage.py` のドキュメントを読む必要があります。

`How Coverage.py works <https://coverage.readthedocs.io/en/v4.5.x/howitworks.html>`_ によると

- ファイルごとに実行された「行」を記録している
- ファイルに対して実行可能な行を取得している。例えば docstring は実行可能な行から除外している。
- 実行可能な行は pyc (つまりバイトコード）が保持している行番号のテーブルを参照している

ということのようです。 [1]_

実際にどの行が実行可能として扱われるのか見た方が理解しやすいので Coverage.py の API で取得してみます。

.. literalinclude:: pytest-example/show_analysis.py
  :caption: show_analysis.py
  :language: python

このスクリプトの実行結果

.. code-block::

  Executable: [3, 4, 5, 6, 7, 9]
  Missing: [9]
  Name            Stmts   Miss  Cover   Missing
  ---------------------------------------------
  apps/myapp.py       6      1    83%   9

Executable が実行可能な行のリスト、Missing が実行されなかった行のリストを表します。

実行可能行にハイライトをつけて myapp.py を再喝します。

.. literalinclude:: pytest-example/apps/myapp.py
  :caption: myapp.py
  :language: python
  :linenos:
  :emphasize-lines: 3-7,9

- L1,2: docstringが除外されている
- L3: 関数宣言は実行可能として扱われている（importした段階で「関数宣言」が実行された扱いになる）
- L8: else は、実行可能ではない扱いになっている

がわかります。

else についてはバイトコードの話になるのであまり掘り下げないでおきますが、ペアになる ``if`` or ``elif`` のジャンプ先は ``else:`` の次の行になるのでバイトコードとして保持する必要がないということだと思います [2]_ 。また、行網羅の計算として正しいかというと、 ``else`` はそれ自体に処理があるわけではないので集計対象にならないようです(ネットで見た感じなので要出典)。

まぁ最初の問題に関しては、実行可能な行が6行あり、そのうち5行を通過したので 86% になりますと。

.. Converge.py の実装メモ
   buit-in の compile 関数で code object を取得, co_lnotab / co_firstlineno から行数計算している
   coverage.parser.PyteParser._bytes_lines() のあたり

この数値をどう使うか
======================

網羅率は割合について目標設定するのは難しいというか、あまり意味がないように思います。「テストケースの漏れ検出器」として、 Missing があったら全て直すというつもりで使うのが良いのではないでしょうか。

網羅率100%を達成しようとすると余計なコストがかかりすぎるという意見もありますが

- テストしやすいモジュール設計にする
- テストが難しいコードは集計対象から除外する ( ``# pragma: no cover``
- あるいは重要なパッケージの置き場所を決めておいて、そこだけカバレッジを出す

など行っていけば、そこまでコストがかかることも無いかと思います。

まぁ100%なら完全に安全かというとそんなことはないので、やっぱりあくまでテストし忘れ防止でしかないですが。

さいごに
==========

branch オプションを有効にすれば分岐網羅の論理的な数値が出てくると思っていたが、行網羅に分岐のパターンが追加されるような実装になっていたので、ちょっと残念 [3]_ 。

.. rubric:: Footnotes

.. [1] 行網羅(line coverage)はあまり馴染みがなかったので最初は命令網羅で計算してるものと勝手に思っていた。
.. [2] `dis <https://docs.python.org/ja/3/library/dis.html>`_ で見てみるとそんな雰囲気がある
.. [3] フローチャートでの手計算した値と一致していれば網羅率の概念の説明からコードでの実演が綺麗に説明できる、という点で残念だったが、Coverage.py 自体は素晴らしい。
