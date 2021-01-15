.. post::
   :tags: Electron, Python
   :category: Python

.. meta::
  :description: Python で GUI アプリを作りたかったのでいろいろ調べました。


==============================================================================
[WIP] Python で Electron-like な事をする2021 (Eel, pywebview, CEF Python 他)
==============================================================================

Python で GUI アプリを作りたかったのでいろいろ調べました。

はじめに
=========

まず前提ですが、単純に Web の技術で GUI を作りたいというだけであれば Electron を使うのがいいと思います(詳しくは後述)。Python でやるモチベーションとしては以下が想定されます。

* Python のライブラリを使う必要があり、可能なら Python (+html/js/css) だけで完結させたい
* 既存の Python のサーバアプリケーションをアプリ化したい（サーバ運用はしたくない）

この記事は上記のような場合に、どういう方法があるか調べたものです。ゴールは実行可能形式のアプリを配布することなので、まず Python スクリプトを実行可能形式にする方法について触れ、その次に今回調べた以下のライブラリ・フレームワークについてそれぞれ触れていきます。

* Eel
* pywebview
* CEF Python
* ネイティブGUI + WebView
* Electron + Python
* Pyodido

バイナリ化
==============

Windows / macOS のGUIアプリケーションを作成するには、それぞれ専用の形式にする必要があります。 [1]_

* Windows の場合: 拡張子 .exe のファイル
* macOS の場合: アプリケーションバンドル(サフィックス .app の、決められた構造を持つディレクトリ)

Python スクリプトを実行可能形式にするツールは PyInstaller, py2exe, py2app があります。

* PyInstaller は Windows, GNU/Linux, macOS , FreeBSD, Solaris, AIX に対応していますが、それぞれのプラットフォーム上でビルドをする（つまり .exe を作成するには Windows 上でビルドする）必要があります。
* py2exe は Windows (.exe) のみに対応しており、 Windows 上でビルドする必要があります。
* py2app は macOS のみ対応しており、 macOS 上でビルドする必要があります。

つまり、ツールがなんであれ、クロスプラットフォームで動作するアプリを作るにはそれぞれのOS上でビルドする必要があるということになります。その場合、いちいち複数環境でビルドなんてやってられないので、ビルドサーバを利用するのが良さそうです。利用できそうなサービスを以下に挙げておきます。

* GitHub Actions: Windows、Linux, macOS に対応(これ Azure でホストされてるっぽいので実質 Azure Pipeline では)
* Azure Pipelines: Windows, Linux, macOS に対応
* AppVeyor: Windows, Linux に対応
* TravisCI: Windows, Linux, macOS に対応

料金体系とかはプライベートリポジトリかどうかによっても変わってくるので調べてみてください（他力本願）。

クロスプラットフォームならまぁ PyInstaller を使うのが良いのではないかと思いますが、大体 GUIライブラリのドキュメントに PyInstaller / py2exe / py2app どれが使えるかが書いてあるので、それをみて決めるのが良いかなと思います。

Eel
========

`Eel <https://github.com/ChrisKnott/Eel>`_ は HTML/JS でシンプルな GUI アプリケーションを作成するためのライブラリです。特徴としては以下が挙げられます。

* Python <-> js 双方向の関数呼び出しを可能にするAPIの提供
* ブラウザはデフォルトで appモードの Google Chrome だが変更可能。やろうと思えば Electron アプリをバイナリに組み込んでブラウザとして使うといったこともできる(後述)。
* Jinja2 テンプレートが使える。

注意点としては README にあるように、チーム内での限られたユーザ利用するアプリの作成に適している、言い換えると一般に公開するようなアプリには向いていない、という点です。具体的に何故かというのは明言されていないですが、おそらくアプリの起動・終了で UX 的によろしくない振る舞いをするからだと思われます。

どういうことかというと、Windows でのタスクバーにピン留め、または macOS での Dock に追加 を行った際に、アプリをクリックして起動しても別アプリの Chrome が立ち上がり、アプリ本体が起動中表示になりません。またアプリ本体を右クリックして閉じる、という操作ができず、アプリのプロセスを終了するには、Chrome のウィンドウを閉じる必要があります(多分ですが、これだとおそらくストアに申請を出しても通らないと思われます)。

この挙動は Eel の仕組みによるものです。Eel はアプリ起動時に `Bottle <https://bottlepy.org/docs/dev/>`_ の HTTP(WebSocket) サーバを立ち上げると共に、そのサーバの URL を指定してブラウザを起動し、表示はそちらに任せる、サーバとブラウザのコミュニケーションは HTTP と WebSocket で行う、という仕組みで動きます。Eel で作成されたアプリ本体は単なるサーバであり GUI アプリケーションとしての機能を持っていないため、上記のような挙動になります。

Eel の仕組みはおそらくメンテナンスが楽になるようになるべくシンプルに割り切った感じだと思われるので、Python で作ったデータを手軽にブラウザでビジュアライズしたいとかそういう用途で利用できます。

(補足ですが、Windows の場合 appモードの Chrome は表示しているサイトの favicon でアプリのアイコンを切り替えてくれるので、faviconを指定しておけば見かけ上の違和感はマシになります。

pywebview
=============

`pywebview <https://pywebview.flowrl.com/>`_ は ネイティブの GUI ウィンドウで HTML を表示するための WebView のクロスプラットフォームラッパーです。以下の特徴を持ちます。

* Windows, macOS, Linux に対応
* Python <~> JavaScript の双方向関数呼び出しが可能
* wsgi サーバをアプリ内のスレッドで立ち上げ、HTTPなどでやりとりできる

WebView を使ってアプリ自身でHTMLレンダリングできるようにした＋ネイティブ周りの実装をやってくれた感じですね。

Python <~> JavaScript の双方向関数呼び出し [2]_ は内部的には WebView のjs を eval できるAPIを利用しているようで、これによりHTTPのAPIを実装しなくてもやりとりができます。

.. warning:: WIP

  * WebKit と Chrome でそんな差があるんか？
  * デバッグが辛いらしい

CEF Python
============

`CEF Python <https://github.com/cztomczak/cefpython>`_ は `CEF (Chromium Embedded Framework) <https://bitbucket.org/chromiumembedded/cef/src/master/>`_ の Python バインディング

* CEF は Chrome(Chromium) を WebView としてアプリに組み込むためのもの
* Electron と同じようなことを Python でやりたい場合、一番近い選択肢になると思われる

  * (余談だが Electron は初期の段階では CEF を使っていたが今は Chromium をライブラリとして直接組み込んでいるらしい [3]_

* 今のところ Python3.4 ~ Python 3.7 に対応
* XXX: ブラウザエンジンの差異とか気にしなくて済むが、そもそも昔のIEでもなしに、今日日そんなに違いがあるもんか？

  * と思ったが、しばらくサーバサイドとかネイティブとかB向けの Chrome で動いてればOKっすみたいな仕事をやっていたので何とも言えんことに気づいた。

ネイティブGUI + WebView / CEF Python
======================================

* kivy, wxPython, qt など
* そんなに楽そうな感がない

Electron + Python
===================

* https://github.com/fyears/electron-python-example
* Python 使いたいだけならこういう選択肢も(1)

Pyodide
==========

* WebAssembly で Python を動かすやつ
* NumPy とか使える
* Python 使いたいだけならこういう選択肢も(2)

おわりに
=========

.. [1] Linuxユーザは普通でサーバ起動すればいいやろ
.. [2] https://pywebview.flowrl.com/guide/interdomain.html#invoke-javascript-from-python
.. [3] https://www.electronjs.org/blog/electron-internals-building-chromium-as-a-library
