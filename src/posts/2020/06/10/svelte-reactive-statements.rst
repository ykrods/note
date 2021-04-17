.. post:: 2020-06-10
   :tags: JavaScript, Svelte
   :category: JavaScript

.. meta::
  :description: Svelte の Reactivite Statements について、実際の挙動を確認してみた。


==========================================
[Svelte] Reactive Statements の挙動の確認
==========================================

`Svelte <https://svelte.dev/>`_ の `Reactivite Statements <https://svelte.dev/tutorial/reactive-statements>`_ について、実際の挙動を確認してみた。

* (チュートリアル内で Reactive Statements という表記はしていないが、URL が ``/tutorial/reactive-statements`` となっているので、今回はそう呼ぶことにする
* Svelte自体の紹介とか、何がいいのかというのは別途記事を書く予定。

.. note::

  * Svelte のバージョンは 3.23.1 で確認

Reactive Statements の基本
===============================

``$: 文`` または ``$: ブロック`` の形で記述された文またはブロックが、内部で参照している変数に対して "リアクティブ" に実行される。

例えば

.. code-block:: javascript

  $: console.log(`a: ${a}`);

のように記述すると、変数a の値が変わるごとに値がログ出力される。

また以下のように条件分岐もできる(例はチュートリアルのまま)

.. code-block:: javascript

  $: if (count >= 10) {
      alert(`count is dangerously high!`);
      count = 9;
  }

検証
=====

1. 一つのコンポーネント内で複数の Reactive Statements を定義できるか
-----------------------------------------------------------------------

検証コード

.. literalinclude:: ex1.svelte
  :caption: ex1.svelte
  :language: html

結果

問題ない。

* それぞれ独立して a,b の変更に対して実行される

2. Reactive Statement から別の Reactive Statements の監視対象を更新した場合どうなるか
----------------------------------------------------------------------------------------

検証コード

.. literalinclude:: ex2.svelte
  :caption: ex2.svelte
  :language: html

実行結果のログ

::

  A: 0
  B: 0
  A: 1
  B: 1
  ...

結果

Reactive Statement から別の Reactive Statements の監視対象を更新しても、正しく検知される。

* `Reactive Decrelations <https://svelte.dev/tutorial/reactive-declarations>`_ とやっていることは同じと思われる ( ``$: doubled = count * 2`` < こういうやつ )

3. Reactive Statements の中で監視対象を更新するとどうなるか
-------------------------------------------------------------------

検証コード

.. literalinclude:: ex3.svelte
  :caption: ex3.svelte
  :language: html

実行結果のログ

::

  foo: 1
  foo: 11

結果

Reactive Statements の中で自身の監視対象を更新してもループにはならない

* 同じDOM更新のタイミング( `tick <https://svelte.dev/tutorial/tick>`_ ) で変更が解決されるため？

4. Reactive Statements の中で非同期で監視対象を更新するとどうなるか
-------------------------------------------------------------------------

* ちなみに現時点では Reactive Statement は非同期関数をサポートしていない (非同期の結果を待てない）

検証コード

.. literalinclude:: ex4.svelte
  :caption: ex4.svelte
  :language: html

結果

Reactive Statements の中で非同期で監視対象を更新するとループする

* 1秒ごとにカウントが増え続ける
* ``counter++`` は ``counter = counter + 1`` なので counter を参照しており、 counter が監視対象になる。非同期で( tick が進んでから) counter が更新されるので Reactive Statements がループする
* こういう使い方がある、というよりは Reactive Statements 内で非同期で変数参照すると予期せぬループが発生するので、注意が必要だと思う。

5. Reactive Statement 内で関数呼び出しした場合、関数の中で参照している変数は監視対象になるのか
------------------------------------------------------------------------------------------------

検証コード

.. literalinclude:: ex5.svelte
  :caption: ex5.svelte
  :language: html

結果

Reactive Statement 内で関数呼び出しした場合、関数の中で参照している変数は監視対象にならない

6. if文の条件式で参照されている変数は監視対象になるのか
---------------------------------------------------------

検証コード

.. literalinclude:: ex6.svelte
  :caption: ex6.svelte
  :language: html

結果

if文の条件式で参照されている変数は監視対象になる

* threshold の変更時にログ出力される

検証のまとめ
=============

監視対象ごとに Reative Statements を定義すれば基本的には素直に動いてくれるが、以下の点に注意が必要と言える

* 意図しない変数が監視対象に含まれること
* Reactive Statement 内に非同期処理を含める場合

検証を踏まえてのベスト(かどうかはわからない)プラクティス
================================================================

監視対象を明確にするため、コールバック関数を定義し監視対象を引数として渡す。

.. code-block:: javascript

  let foo = 0;
  let bar = 0;

  $: onFooChanged(foo);
  $: onBarChanged(bar);

  async function onFooChanged() {
    // some statements
  }

  function onBarChanged() {
    // some statements
  }

こうしておくと、意図しない監視対象の変更により予期せぬタイミングで実行されたり、ループするのを防げる。かつ単純に読みやすい。

対象が複数で、そのどれかが更新したタイミングで発火したい場合は一つの関数に対象の変数をまとめてわたせば良い

.. code-block:: javascript

  let foo = 0;
  let bar = 0;

  $: onFooOrBarChanged(foo, bar);

  function onFooOrBarChanged() {
    // some statements
  }

if文を書ける場合(監視対象が null にならない場合)はif文を書いた方が一番すっきりする

.. code-block:: javascript

  let params = {};

  $: if (params) {
    onParamsChanged();
  }

  function onParamsChanged() {
    // some statements
  }

調査メモ
===============

* Reactive Statements は内部的には DOM更新と同じ流れの中で処理されている模様。 [1]_

  * チュートリアルには「DOM更新が発生するごとに(before|after)Update が呼ばれる」とあるが [2]_ 、(before|after)Update は Reactive Statements の監視対象に変更があった場合も呼ばれている [3]_

.. mermaid::

  graph TB
    id1(状態の変更を検知) --> id2(対応する Reactive Statements の実行) --> beforeUpdate --> DOM更新 --> afterUpdate

* (before|after)Update で監視対象を更新した場合の挙動は未検証

.. rubric:: Footnotes

.. [1] 挙動的にそうらしいという話なので今後変更がある可能性はある
.. [2] https://svelte.dev/tutorial/update
.. [3] https://github.com/sveltejs/svelte/blob/master/src/runtime/internal/scheduler.ts この辺り
