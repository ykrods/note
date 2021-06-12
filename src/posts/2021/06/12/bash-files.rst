.. post:: 2021-06-12
   :tags: bash
   :category: bash

.. meta::
  :description: .bashrc の設定なんか読み込まれないなぁというよくあるアレに陥ったので調べてまとめた。

=======================================================
.bashrc, .bash_profile と bash シェル (Ubuntu 18.04)
=======================================================

はじめに
==========

.bashrc の設定なんか読み込まれないなぁというよくあるアレに陥ったので調べてまとめた。

.. warning::

  Ubuntu 18.04 で確認した内容をまとめています。ディトリビューションによって差異があるらしいのでご注意ください。

man bash
=============

::

  # man bash より引用

  When an interactive shell that is not a login shell is started, bash reads and executes commands
  from  /etc/bash.bashrc  and ~/.bashrc, if these files exist.

  # (訳) ログインシェルでないインタラクティブシェルが始まった時、 /etc/bash.bashrc や ~/.bashrc が存在すれば、
  #     それらを読み込んで実行する

  When  bash  is  invoked  as  an  interactive login shell, or as a non-interactive shell with the
  --login option, it first reads and executes commands from the file /etc/profile,  if  that  file
  exists.   After  reading that file, it looks for ~/.bash_profile, ~/.bash_login, and ~/.profile,
  in that order, and reads and executes commands from the first one that exists and  is  readable.

  # (訳) インタラクティブログインシェル、あるいは --login オプション付きノンインタラクティブシェル
  #      として bash が呼び出された場合、 ~/.bash_profile , ~/.bash_login, ~/.profile の順で
  #      最初の存在するファイルを読み込んで実行する


とりあえず上記を表にまとめるとこうなる。

.. list-table::
  :header-rows: 1

  - - 種別
    - 読み込むファイル

  - - インタラクティブログインシェル
    - * /etc/profile
      * ~/.bash_profile, ~/.bash_login, ~/.profile から一つ

  - - インタラクティブ(ログインじゃない)シェル
    - * /etc/bash.bashrc
      * ~/.bashrc

  - - ノンインタラクティブシェル+ login オプション
    - * /etc/profile
      *  ~/.bash_profile, ~/.bash_login, ~/.profile から一つ

  - - ノンインタラクティブシェル
    - 何も読み込まない?

うむ、わからん。ということで各用語の整理。

インタラクティブログインシェル (あるいはログインシェル)
================================================================

ログインしたときに起動するシェル。通常ログインしたら対話シェルが始まるので、単にログインシェルともいう。

起動方法

* ログインする
* ``$ su - [user]`` ( - は -l, --login の省略)
* ``$ bash -l``
* ``$ sudo -i [-u user]``

インタラクティブシェル
=======================

対話シェル。ログインシェルと対比して使われる場合はインタラクティブ（ログインじゃない）シェルの意味で使われる。厳密な定義は ``man bash`` を参照。

起動方法

* ``$ su [user]`` ( - 無し)
* ``$ bash``
* ``$ sudo -s [-u user]``

ノンインタラクティブシェル
=============================

非対話シェル。

起動方法

* ``$ bash -c command_string``
* ``$ sudo -s [-u user] command``

ノンインタラクティブシェル + ログインオプション
=================================================

非対話だがログイン時の設定( \*profile )を読み込みたい場合に使う。

起動方法

* ``$ bash -lc command_string``
* ``$ sudo -i [-u user] command``

初期設定
==============================

Ubuntu18.04 の設定ファイルがどの様になっているかを確認する。

.bashrc
-------------------------

* 以下の記述によりノンインタラクティブな場合は何もしない様になっている

  .. code-block:: shell

     # If not running interactively, don't do anything
     case $- in
         *i*) ;;
           *) return;;
     esac

  * ( ``$ bash -c 'echo $-'`` を実行すると ``hBc`` が帰ってくる。i を含んでいないので return される

* その他の設定項目

  * ``ll``, ``la`` などのエイリアス
  * 色関連
  * bash の入力補完

* => 内容的に、.bashrc は対話シェルで適用されることが想定されていると判断できる。

.profile
-------------------------

* ~/.bashrc の読み込み

  * man にある様にログインシェルは .bashrc を読み込まないので、.profile の中で ``. "$HOME/.bashrc"`` している

* パス設定

.bash_profile
-------------------------

* デフォルトで存在しない

.. tip::

   これ系の記事では .bash_profile について説明しているものが大半だが、少なくとも Ubuntu 18.04 では .bash_profile を設置することによりデフォルトの .profile が読み込まれなくなる(.bash_profile の方が優先度が高い)ことに注意が必要

動作検証
==========

su, sudo, bash コマンドでの .bashrc, .profile の読み込みの挙動を確認する。

準備
-----

.. code-block:: shell

   $ sudo useradd -m -s /bin/bash hogeo
   $ sudo su - hogeo
   $ echo 'export PATH="$HOME/.bin1:$PATH"' >> .bashrc
   $ echo 'echo ".bashrc loaded"' >> .bashrc
   $ echo 'export PATH="$HOME/.bin2:$PATH"' >> .profile
   $ echo 'echo ".profile loaded"' >> .profile

* .bashrc, .profile それぞれの読み込み時に echo する
* 検証のため、それぞれのファイルで PATH に $HOME/{.bin1, .bin2} を追加する(値に意味はない)
* デフォルトの設定に変更は加えない( .profile から .bashrc を読み込む)

su -
---------------

.. code-block:: shell

   $ sudo su - hogeo
   .bashrc loaded
   .profile loaded
   $ env | grep PATH
   PATH=/home/hogeo/.bin2:/home/hogeo/.bin1:/usr/local/sbin: ..(略)

両方読み込まれる

su
------------

.. code-block:: shell

   $ sudo su hogeo
   .bashrc loaded
   $ env | grep PATH
   PATH=/home/hogeo/.bin1:/usr/local/sbin: ..(略)

.bashrc のみ読み込まれる

bash
--------

.. code-block:: shell

   $ sudo su - hogeo
   .bashrc loaded
   .profile loaded
   $ bash
   .bashrc loaded
   $ env | grep PATH
   PATH=/home/hogeo/.bin1:/home/hogeo/.bin2:/home/hogeo/.bin1:/usr/local/sbin: ..(略)

``su -`` と ``bash`` で .bashrc が二回読み込まれ、 .bin1 のパスが二重になっている（実害はないが気持ちが悪い）

bash -l
------------

.. code-block:: shell

   $ sudo su - hogeo
   .bashrc loaded
   .profile loaded
   $ bash -l
   .bashrc loaded
   .profile loaded
   $ env | grep PATH
   PATH=/home/hogeo/.bin2:/home/hogeo/.bin1:/home/hogeo/.bin2:/home/hogeo/.bin1:/usr/local/sbin: ..(略)

``su -`` と ``bash -l`` でそれぞれ .profile, .bashrc を読み込んでいる。

この辺はまぁそもそも ``su -`` しているのだから ``bash -l`` する必要ないよね、ということでいいのだろうか？

( 上記の様なパス追加なら重複するだけだが、ログイン時に二重に実行されると困る様な処理を挟む場合は何かしら対応する必要がある。とはいえ、ログインシェルからインタラクティブシェルを起動するユースケースはあまりないようにも思える。

bash -c command_string
-------------------------

.. code-block:: shell

   $ sudo su - hogeo
   .bashrc loaded
   .profile loaded
   $ bash -c "env | grep PATH"
   PATH=/home/hogeo/.bin2:/home/hogeo/.bin1:/usr/local/sbin: ..(略)

非対話シェルなので何も読み込まない

bash -lc command_string
-------------------------

.. code-block:: shell

   $ sudo su - hogeo
   .bashrc loaded
   .profile loaded
   $ bash -lc "env | grep PATH"
   .profile loaded
   PATH=/home/hogeo/.bin2:/home/hogeo/.bin2:/home/hogeo/.bin1:/usr/local/sbin: ..(略)

``-l`` オプションにより .profile が読み込まれるが、非対話シェルなので .bashrc が読み込まない（中断される）

sudo -s [-u user] command
----------------------------

.. code-block:: shell

  $ sudo -s -u hogeo env | grep PATH
  PATH=/usr/local/sbin

非対話シェルなので何も読み込まれない

* (オプションなしの ``sudo [-u user] command`` の場合はそもそもシェルを起動しない(ハズ))

sudo -i [-u user] command
---------------------------

.. code-block:: shell

  $ sudo -i -u hogeo env | grep PATH
  # .profile loaded
  PATH=/home/hogeo/.bin2:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/snap/bin

``-i`` オプションにより .profile が読み込まれるが、非対話シェルなので .bashrc が読み込まない（中断される）

sudo [-u user] bash -c command_string
-----------------------------------------

.. code-block:: shell

  $ sudo -u hogeo bash -c 'env | grep PATH'
  SUDO_COMMAND=/bin/bash -c env | grep PATH
  PATH=/usr/local/sbin: ..(略)

非対話シェルなので何も読み込まれない

sudo [-u user] bash -lc command_string
------------------------------------------

.. code-block:: shell

  sudo -u hogeo bash -lc 'env | grep PATH'
  SUDO_COMMAND=/bin/bash -lc env | grep PATH
  PATH=/usr/local/sbin: ..(略)

``sudo -i -u`` と違い、 .profile が読み込まれない

* これは sudo のデフォルトの挙動では ``$HOME`` がログインユーザのもののままなため

  * ( sudo の実行ユーザの ``$HOME/.profile`` が読み込まれる
  * ( ``sudo -u hogeo bash -lc 'echo $HOME'`` すると変わっていないのが確認できる

sudo に ``-H (--set-home)`` オプションを加えると ``$HOME`` が切り替わった上でコマンドが実行される

.. code-block:: shell

  $ sudo -H -u hogeo bash -lc 'env | grep PATH'
  .profile loaded
  SUDO_COMMAND=/bin/bash -lc env | grep PATH
  PATH=/home/hogeo/.bin2:/usr/local/sbin: ..(略)

.. tip::

  余談になるが、ansible の become ディレクティブではデフォルトで sudo が使われ、デフォルトの ``become_flags`` に ``-H`` が入っているので何もしなくても ``become_user`` で指定したユーザのホームに切り替わっている

  * https://docs.ansible.com/ansible/2.9_ja/plugins/become/sudo.html

まとめ
==================

デフォルトの設定に合わせる場合、以下の様にまとめられる。

.. list-table::
  :header-rows: 1

  - - 種別
    - 起動方法
    - 読み込まれるファイル

  - - ログインシェル
    - * ログイン

      .. code-block:: shell

        $ su - [user]
        $ sudo -i [-u user]
        $ bash -l

    - .profile, .bashrc

  - - インタラクティブシェル
    - .. code-block:: shell

        $ su [user]
        $ sudo -s [-u user]
        $ bash

    - .bashrc
  - - 非対話シェル
    - .. code-block:: shell

        $ bash -c command_string
        $ sudo -s [-u user] command

    - なし

  - - 非対話シェル+ログインオプション
    - .. code-block:: shell

        $ bash -lc command_string
        $ sudo -i [-u user] command
        $ sudo -H [-u user] \
            bash -lc command_string

    - .profile

.bashrc と .profile の使い分けとしては(これもデフォルト設定に合わせるなら)以下

.. list-table::

  - - 対話のための設定
    - .bashrc
  - - それ以外
    - .profile

注意点

* .profile (または .bash_profile) に書いても複数回呼ばれるときは呼ばれる

他の方針
============

これが正解というものはないと思うので、結局のところちゃんと理解した上でやりたいことに合ったポリシーで管理しようという話になるのではないかと思う。ということで少し他の方針についても触れる。

* 全部 .bashrc に書く

  * 常に対話シェルを起動してからコマンドを叩く様な運用方針の場合
  * デフォルトの挙動を変えて非対話シェル + ログインオプションでも .bashrc を読み込ませる様に変更する場合
  * 個人的には、あえてデフォルトの挙動を変えてまでやるメリットは思い当たらないが、「常に対話シェルを起動する運用」は有り得なくもない？

* .bash_profile を使う

  * 不意に .bash_profile が置かれたことにより .profile が読み込まれなくなる可能性があるので、最初から .bash_profile を使った方が安心というのはあるかもしれない。
  * 個人的な感覚では、正しく .profile の内容 ( 主に .bashrc の読み込み ) を反映させた上で .bash_profile を配置し、不要な .profile は消す、というところまでやればこれでも良いと思う。
  * デフォルトで .bash_profile が存在する OS では当然 .bash_profile を使えば良いと思う

参考
======

* man bash
* man sudo
* man su
* `ログインシェルとインタラクティブシェルの違い <http://tooljp.com/windows/chigai/html/Linux/loginShell-interactiveShell-chigai.html>`_
