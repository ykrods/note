.. post:: 2020-01-29
   :tags: Vue.js, JavaScript, ドキュメンテーション
   :category: JavaScript


=============================================================
Vue.js の event bus (あるいは event hub) 、非推奨になっていた
=============================================================

気づいたらドキュメントからいなくなっていた。

event bus (あるいは event hub) とは
=====================================

親子関係にないコンポーネント間でやり取りするための手段として `Vue.js の公式ドキュメント <https://vuejs.org/v2/guide/>`_ に載っていた方法です。

具体的には、 ``$emit``, ``$on`` でイベントをやり取りする用の vue インスタンスを作成するというシンプルなもので、
ざっくりとしたコード例は以下のようになります。

.. code-block:: javascript

  const bus = new Vue();

  // on ComponentA
  bus.$emit('some-event-occurred', data);

  // on ComponentB
  bus.$on('some-event-occurred', handler);

消えた記載
=============

私は数年前に Vue.js で簡単なアプリを作成していたくらいで、最近また触りだしたところでした。 [1]_

event bus の存在はおぼろげながら記憶していたので `日本語のVue.jsドキュメント <https://jp.vuejs.org/v2/guide/>`_ を確認したのですが、検索欄に ``bus`` と入力しても出てきません。

Googleで外部サイトを検索すると event bus の紹介記事は出てくる＆その記事にあるドキュメントのリンクは `コンポーネントの基本 <https://jp.vuejs.org/v2/guide/components.html>`_ ページを指しているので、公式のドキュメントから記載が消えていると予想できます。

こうなるとなんで消えたが気になってくるので、調べました。

調査
=====

調査1: ドキュメントのGithubリポジトリで検索する
-------------------------------------------------------

日本語のドキュメントページは英語ページを元に有志の方が翻訳したものなので、英語のドキュメントの Github リポジトリで ``bus`` と検索してみます。

https://github.com/vuejs/vuejs.org/search?q=bus

検索結果の Code、Issue から、

https://vuejs.org/v2/style-guide/#Non-flux-state-management-use-with-caution のページで「グローバルな状態の管理はイベントバスより Vuex を使った方が良い」ということが書いてあることがわかります。

また、上記のページの ``global event bus`` というリンクの先にイベントバス自体の説明（およびここでも Vuex 使った方が良いという説明）があるのがわかります。

`#` なおこのページでは event hub という書き方をしている

この時点で非推奨だから「コンポーネントの基本」ページから消したのかな？という予想は立ちますが、そのような議論をした Issue は見つかりませんでした。せっかくなのでどのコミットで消えたのか掘り下げてみます。

調査2: リポジトリを clone してログを追う
------------------------------------------

コードが追加・変更されたタイミングは ``git blame`` を使えばわかるのですが、削除の場合は ``git log -S`` を使います

.. code-block:: text

  man git-log
    ...
    -S<string>
      Look for differences that change the number of occurrences of the specified string (i.e. addition/deletion) in a file.
      Intended for the scripter's use.

      It is useful when you're looking for an exact block of code (like a struct), and want to know the history of that block
      since it first came into being: use the feature iteratively to feed the interesting block in the preimage back into -S, and
      keep going until you get the very first version of the block.


.. code-block:: shell

  # ファイルorディレクトリが分かっている場合は指定できる
  git log -p -Sbus -- src/v2/guide/components.md

この結果 ``commit:5adbc5f902a3562a3e233c06f99f9be30254741a`` (2018.03) で削除されているのがわかります。

Github ではコミットログに対してコメントをつけることができるのですが、このコミットのコメントに理由が書いてありました。

https://github.com/vuejs/vuejs.org/commit/5adbc5f902a3562a3e233c06f99f9be30254741a#r29139254

雑に翻訳すると

::

  event bus はどのようなユースケースであっても推奨できない手法なので削除した。
  event bus は使っているうちに(複雑化して?)辛くなってきて、
  辛くなった後ではリファクタリングするのも困難になる。

ということのようです。

まとめ
=======

公式には(2018年以降) event bus の利用は非推奨で、グローバルな状態管理には Vuex を使いましょうということで良いと思います。

- 例えばログインユーザのセッションなどはグローバルな状態だと思われるので、基本的には SPA を Vue で作るなら Vuex を利用することになると思います。

私見
------

Vue.js 自体が「プログレッシブフレームワーク（他の一枚板(モノリシック: monolithic)なフレームワークとは異なり、Vue は少しずつ適用していけるように設計されている）」なので、最初はシンプルに始める ==> シンプルな event bus を使う。という理屈は成り立つと思います。個人的にもシンプルを好みますし。

まぁただ選択肢が多いと今後の Vue本体の 機能拡張・ドキュメンテーション・サポート も大変になるので、そういう理由での削除という面もあるのかなと思います。

::

  Q. event bus で XXX するにはどうしたらいい？
  A. Vuex 使ってください

というやり取りが多すぎたとか（フォーラム等確認していないので推測ですが）

ちなみに ``$emit``, ``$on`` が使えなくなった訳ではないので、 event bus も使えなくなった訳ではありません。オススメできないだけです。

.. rubric:: Footnotes

.. [1] `#` 時代は Vue から Nuxt.js に移っている？様ですが、SSRしないなら Vue で良いんですかね？？何れにせよ Vue やってから考えようと思ってますが
