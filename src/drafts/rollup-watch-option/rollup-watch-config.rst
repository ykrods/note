.. meta::
  :description: rollup の watch の設定を誤解していたというメモ

=========================================
[調査メモ] rollup の watch 設定について
=========================================

rollup の watch の設定を誤解していたというメモ

.. warning::

  rollup@2.52.2 で確認

結論から言うと
================

* watch はビルド時に参照されたファイルが自動的に監視対象( watchFile ) になる。特に設定をする必要はない。
* ``watch.include`` は監視対象の中で、自動ビルドを行うファイルをさらに制限するためのオプション
* ``watch.exclude`` は監視対象の中で、自動ビルドの対象外となるファイルを示すためのオプション

include で ``src/**`` など指定したら src 以下のファイルがすべて監視対象になるものと勘違いしていた

調査
===============================

watchFile(s) を確認したかったので、コードを書いた。

oo

.. literalinclude:: watch-dump-event.js
  :caption: watch-dump-event.js
  :language: javascript

サンプルの内容は以下

.. literalinclude:: rollup.config.js
  :caption: rollup.config.js
  :language: javascript

.. literalinclude:: src/main.js
  :caption: src/main.js
  :language: javascript

.. literalinclude:: src/submod1.js
  :caption: src/submod1.js
  :language: javascript

.. literalinclude:: src/submod2.js
  :caption: src/submod2.js
  :language: javascript

``node watch-dump-event.js`` を実行すると以下のような出力を得る

::

  { code: 'START' }
  {
    code: 'BUNDLE_START',
    input: 'src/main.js',
    output: [ '/work/rollup-watch/dist/bundle.js' ]
  }
  {
    code: 'BUNDLE_END',
    duration: 47,
    input: 'src/main.js',
    output: [ '/work/rollup-watch/dist/bundle.js' ],
    result: {
      cache: { modules: [Array], plugins: [Object: null prototype] },
      close: [AsyncFunction: close],
      closed: false,
      generate: [AsyncFunction: generate],
      watchFiles: [
        '/work/rollup-watch/src/main.js',
        '/work/rollup-watch/src/submod1.js',
        '/work/rollup-watch/src/submod2.js'
      ],
      write: [AsyncFunction: write]
    }
  }
  { code: 'END' }

include と exclude を変えても watchFile(s) には影響しない

watchFile(s) を追加したい場合
===============================

(最初の勘違いのように) 任意のファイル・ディレクトリを監視対象に追加したい場合はプラグインを書く。 [1]_ プラグインの `this.addWatchFile <https://rollupjs.org/guide/en/#thisaddwatchfileid-string--void>`_ が利用できる。

``#`` 参照してるファイルが自動的に追加されるのであまり必要ないかもしれないが

参考) `rollupjs - rollup watch include directory - Stack Overflow <https://stackoverflow.com/questions/63373804/rollup-watch-include-directory>`_

.. [1] 既にそのためのプラグインが公開されているかもしれないが、未調査
