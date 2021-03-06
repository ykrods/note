.. post:: 2019-06-20
  :tags: pytest, pytest-cov
  :category: Python

==============================
pytest の Coverage の計算方法
==============================

カバレッジはこうやって出すんですよという資料を書いていたら自分がわかっていなかったので調べた話です。

クイズ
========

以下のサンプルでテストを実行し、 `pytest-cov <https://pypi.org/project/pytest-cov/>`_ でカバレッジを取得した場合、その値はいくつになるでしょう。なお ``branch`` オプションは無効の状態で取得するものとします。

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

83% です。

::

  ----------- coverage: platform linux, python 3.7.1-final-0 -----------
  Name            Stmts   Miss  Cover   Missing
  ---------------------------------------------
  apps/myapp.py       6      1    83%   9

これ恐らく ``pytest-cov`` (``Coverage.py``) 自体を調べたことある人以外間違えるのでは無いかと思います。

この数値はどこから来たのか
===========================

まず83%という数字自体については、表示されている Stmts=6, Miss=1 の値から算出しているとみて良いでしょう。

.. math::

  (Stmts - Miss) / Stmts = 5 / 6 = 0.833...

続いて Stmts, Miss の集計方法ですが、 pytest-cov は `Coverage.py <https://pypi.org/project/coverage/>`_ を pytest で使えるようにしたプラグインなので、 Coverage.py のドキュメントを読む必要があります。

`How Coverage.py works <https://coverage.readthedocs.io/en/v4.5.x/howitworks.html>`_ によると

- ファイルごとに実行された「行」を記録している
- ファイルに対して実行可能な行を取得している。例えば docstring は実行可能な行から除外している。
- 実行可能な行は pyc (つまりバイトコード）が保持している行番号のテーブルを参照している

ということのようです。つまり行網羅率(Line Coverage)を出してるんですねこれ。 [1]_

実際にどの行が実行可能として扱われるのかは、見た方が理解しやすいので Coverage.py の API で取得してみます。

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

実際のところ網羅率について目標設定するのはあまり意味がないように思います。

行網羅率では(命令網羅率でも同じことが言えますが)一時変数などを加えたり、処理のステップを分けるだけでも割合は変わりますし、「実行可能行」を脳内で計算するのはなかなか難しいので意味を見出しにくいです [3]_ 。例えば網羅率が 90% を超えていればそれなりにテストされているんだなという気持ちにはさせてくれますが、テストされていない残りの 10% にどれだけ重要なロジックが含まれるかは数値から読み取れません。誰かが頑張って割合を上げた分、誰かが怠けられるようになるだけなようにも思えます。

個人的には網羅率は気にせずテスト漏れ(Missing)の検出器として使うのが良いのではないかと思います。最初はカバレッジを意識せずにテストコードを書いて、Missing があったら直すという感じですね。

網羅率100%を達成しようとするとコストがかかりすぎるという意見もありますが、

- テストしやすいモジュール設計にする
- テストが難しいコードは集計対象から除外する ( ``# pragma: no cover``
- あるいは重要なパッケージの置き場所を決めておいて、そこだけカバレッジを出す

など行っていけば、そこまでコストがかかることも無いかと思います。

まぁテストを考慮していない実装に対して新たにカバレッジ測定ツールを導入して100%まで持っていくのは当然辛いので、コストというのはそこから来ているんじゃ無いかという気もしますが。

.. update:: 2020-12-16

  Martin Fowler 大先生の `テストカバレッジ <https://bliki-ja.github.io/TestCoverage/>`_ では 100% は信用ならないと書いてありますが、これは数値だけ見てテストを書いた結果意図が読み取れないテストになっている疑いがあるっていう話で、まぁやっぱり「（見落としていた）テストが不十分なコードを見つける」のに有用なわけですね。

  テストしなくてもよい（10%~20%の)コードはそう分かるようにマーク等で除外しておけば、毎回集計結果を見て「あれここテストしなくていいんだっけ？と確認せずに済むので良いのではというのが上記の意図するところで、その結果数値は100%になりますが、それを目標にしようというわけではないです。実際問題としてフレームワーク的な制約でうまく除外するのが難しいという可能性はありますが。

感想
==========

今回調べた経緯としては、「フローチャートで手計算した結果と分岐網羅率の実際の計測結果が一致していれば 網羅率の概念の説明から実演という流れが綺麗にできるのでは？」と思い実際にやってみた結果、よくわからない数値が出てきたというが発端でした。Coverage.py は branch オプションが有効な場合、行数に分岐数を加算するような実装になっているので、理論値（？）とは合わないようです。最初の目的からするとそこは残念でしたが、バイトコードを使うという発想は素晴らしいなと思いました。

.. rubric:: Footnotes

.. [1] 行網羅率はあまり馴染みがなかったので最初は命令網羅率(Statement Coverage)で計算してるものと勝手に思っていた。
.. [2] `dis <https://docs.python.org/ja/3/library/dis.html>`_ で見てみるとそんな雰囲気がある
.. [3] ``else`` 以外にも ``finally`` も除外される。把握していないが他にもきっとある。
