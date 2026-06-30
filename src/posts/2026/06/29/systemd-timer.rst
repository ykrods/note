.. post:: 2026-06-29
   :tags: systemd, systemd.timer
   :category: os

.. meta::
  :description: systemd.timer のモノトニックタイマーについてまとめた

=======================================
systemd.timer のモノトニックタイマー
=======================================

導入
=========

systemd.timer 自体は以前にも使ったことがあったが、モノトニックタイマーについては使ったことがなかったのでその方法について整理・検証した。用語の整理の都合上 systemd unit についても簡単におさらいする。

systemd unit のおさらい
==========================

unit
------

- ユニットは systemd が管理する対象の基本単位。
- ユニットは ``active``, ``inactive (dead)`` とそれらの中間状態( ``activating``, ``deactivating`` )、および ``failed`` の状態を持つ
- ユニットには service, socket, timer などのタイプがあり、タイプごとに設定ファイルの拡張子が異なる

  ::

    # 例
    sshd.service
    syslog.socket

- cron のように時間を起点としてタスクを実行したい場合、timer が利用できる

systemd.timer
-----------------

ユニットタイプによっては他のユニットと連携して使う前提のものがあり、timer もその内の一つ。実行タイミングに関わる設定は timer に記述し、実行内容を同名の .service ユニットに記述する。 [1]_

サンプルとして、毎日 05:00 に ``date`` コマンドを実行する例を挙げる。

.. code-block:: ini
  :caption: /etc/systemd/system/sample.timer

  [Unit]
  Description="Run sample.service"

  [Timer]
  OnCalendar=*-*-* 05:00:00 Asia/Tokyo

  [Install]
  WantedBy=timers.target

.. code-block:: ini
  :caption: /etc/systemd/system/sample.service

  [Unit]
  Description=sample service

  [Service]
  Type=oneshot
  User=ubuntu
  Group=ubuntu

  ExecStart=/usr/bin/date --iso-8601=seconds


ユニットファイルを更新した際は以下のコマンドでユニットファイルを再読み込みする

.. code-block:: shell

  $ sudo systemctl daemon-reload

タイマーとサービスはそれぞれ別のユニットとして扱われるため、それぞれが状態を持つ。以下のコマンドでタイマーユニットを起動すると、指定したタイミングでタイマーがサービスユニットを起動するようになる。

.. code-block:: shell

  $ sudo systemctl start sample.timer
  $ # OS起動時にタイマーを自動起動させる + start .timer
  $ sudo systemctl enable --now sample.timer

以降、分かりやすさのための便宜上、タイマーがサービス(unit)を起動することをタスク起動と記述し、タイマーユニットの起動と区別する。

タイマー起動後は以下で実行スケジュールを確認できる

.. code-block:: shell

  $ sudo systemctl list-timers sample.timer

タイマーの指定方法
======================

タイマーの指定方法にはモノトニック(単調)タイマーとカレンダータイマーがある。それぞれ以下のタイミングでタスクを起動する。

:モノトニックタイマー: (概ね)「なんらかのイベント発生から指定した時間が経過」したタイミング
:カレンダータイマー: cron と同じように日付を基準としたタイミング

カレンダー式の方が直感的だがモノトニックでは手軽に並行実行を避けられる利点がある。

- なお実際の利用シーンは少ないかもしれないが、カレンダーとモノトニックを組み合わせたスケジュールも可能

モノトニックタイマー
------------------------

モノトニックタイマーは対象のイベントとそのイベント発生時点からの経過時間の組み合わせで設定を記述する。例えば ``OnBootSec=60s`` と記述した場合、OSが起動してから 60秒後にタスクが起動する。

``[Timer]`` セクションに、モノトニックタイマーとして以下のディレクティブが指定できる。

.. list-table::
  :header-rows: 1

  - - ディレクティブ
    - 起点
  - - ``OnActiveSec=``
    - タイマーが active になった時
  - - ``OnBootSec=``
    - OS起動時
  - - ``OnStartupSec=``
    - サービスマネージャーの開始時

      - (ユーザでない)システムのタイマーでは ``OnBootSec`` とほぼ同じ。

  - - ``OnUnitActiveSec=``
    - タイマーが起動したユニットが最後にアクティベートされたとき
  - - ``OnUnitInactiveSec=``
    - タイマーが起動したユニットが最後にデアクティベートされたとき

``OnUnitActiveSec`` または ``OnUnitInactiveSec`` を指定することで、繰り返しタスクを実行することができる。が、これらは定義通りユニットのアクティベートまたはでアクティベート（つまり前回のタスクの実行）を起点に動くので「最初の一回の起動」は別の方法で行う必要がある。通常は ``OnActiveSec``, ``OnBootSec``, ``OnStartupSec`` などと組み合わせて使う。 [2]_

.. warning::

  少し紛らわしいが ``OnActiveSec=`` は timer ユニット自身を、 ``OnUnitActiveSec=`` は timer が起動するユニットを対象にしている。

モノトニックタイマーの一般的な組み合わせ例としては以下のようなユニットファイルになる。

::

  [Unit]
  Description="Run sample.service"

  [Timer]
  OnActiveSec=1min     # timer が起動してから 1分後に sample.service を起動
  OnUnitActiveSec=5min # 5分間隔で sample.service を起動
  AccuracySec=1s

  [Install]
  WantedBy=timers.target

詳細は次のセクションで述べるが、 ``OnBootSec`` より ``OnActiveSec`` の方が挙動がシンプルで使いやすそうに感じる。 ``OnActiveSec`` でも ``$ systemctl enable xxx.timer`` しておけばタイマーは ``OnBootSec`` 同様OS起動時に自動起動する。

.. tip::

  細かい補足だが、 ``OnUnitActiveSec=`` は前述の通りアクティベートされたタイミングであり ``Active`` になったタイミングではない。そもそも ``Type=oneshot`` のサービスの状態は "activating" から "deactivating" or "dead" に直に変わり、 "active" にならない（と man に書いてある）。何が言いたいかというと、ディレクティブ名からして unit が active になったタイミングと想像しやすいがそうすると oneshot の説明と矛盾するということで混乱しやすいところだと思う。

OnBootSec の挙動
------------------

man page に以下のように記述されている

    If a timer configured with OnBootSec= or OnStartupSec= is already in the past when the
    timer unit is activated, it will immediately elapse and the configured unit is started.
    This is not the case for timers defined in the other directives.

OS起動後に設定を変更した後、OS再起動を行わなくともタスクが起動できるような対応がされているようだが、実際に ``OnBootSec=30s`` のみ記述したタイマーで試してみると以下のような挙動になっていた。

- タイマー起動状態で ``OnBootSec=30s`` を追記して daemon reload のみを行った場合、タスクが起動しない
- 上の状態でタイマーを restart すると判定が行われ、タスクが即時実行される
- 更にその後もう一度タイマーを restart した際はタスクが起動しない
- .timer を編集し、 ``daemon-reload`` およびタイマーの再起動を行うと、タスクが即時実行される

同一のタイマーで1回のOS起動に対して1回の ``OnBootSec`` が起動するという事だと思われるが、慣れていないと「よくわからないがタイマーが動かない」ということになりそうである。個人的には ``OnBootSec`` は繰り返しの初回用でなく「本当に OS 起動に対して何か処理を行いたい」という用途で使うのが良いように思われる。

疑問: OnUnitActiveSec より対象ユニットの処理に時間がかかったらどうなる？
---------------------------------------------------------------------------

``ExecStart=/usr/bin/sleep 90``, ``OnUnitActiveSec=60s`` などでどういった挙動になるか検証したところ、実際には約90秒ごとに実行された。

man page には次の説明がある。

    Note that in case the unit to activate is already active at the time the timer elapses it is not restarted, but simply left running.

ここから実行中のユニットが中断されたり、並行して実行されることがないというのがわかる。

また上記の説明からは読み取りにくいが、実際には「タイマーの対象ユニットが処理を終えて ``inactive`` になったタイミングでタイマーの再評価が行われ、 ``OnUnitActiveSec`` で指定した時間を既に経過している場合(既に条件を満たしている場合)は即時次の activation を実行する」という挙動なようである。 [3]_

ちなみに、sleep 時間を 30s にした変更した場合は ``OnUnitActiveSec=60s`` の通り60秒ごとに実行される。これらの事から処理が終わってからの間隔を一定にしたい場合は ``OnUnitInactiveSec`` の方が適していると思われる。


感想
==============

一定間隔で実行しつつ、同じサービスの並行実行を避けたいバッチ処理などに対してモノトニックタイマーは向いていると思われる。

今回、「大まかな理解で使っていたけどちゃんと理解するか」と思い調べてみたが、意外と紛らわしかったりアンドキュメントと思しき部分があり、「大まかな理解のままでもよかったのでは？」という思いが頭の中を少しよぎった。が、 ``OnActiveSec`` ディレクティブや ``OnCalendar`` のタイムゾーン指定など便利な記述を知れたのでよしとする。

おまけ(1): カレンダータイマー
----------------------------------------

カレンダーのフォーマットは ``$ systemd-analyze calendar "EXPRESSION"`` で確かめられる。

サンプルとしてありそうなフォーマットをいくつか載せておく。

::

  *-*-* 05:00:00             # 毎朝5時
  *-*-* *:00:00              # 毎時00分
  *-*-* *:00,30:00           # 毎時00分, 30分
  *-*-* 05:00:00 Asia/Tokyo  # タイムゾーン付き
  Mon..Fri *-*-* 08:00:00    # 平日の朝08時

おまけ(2): start と enable について補足
-----------------------------------------

enable は、ユニットの ``[Install]`` セクションに従って、OS起動時などにユニットを開始対象となるよう設定する操作であり、ユニットの現在の状態とは無関係である。

- つまり disabled のままでもユニットを起動して active にできるし、inactive 状態のまま enable することもできる
- enable と同時にユニットを起動したい場合は ``enable --now`` が使える

参考
=======

- `Ubuntu Manpage: systemd.service - Service unit configuration <https://manpages.ubuntu.com/manpages/noble/man5/systemd.service.5.html>`_
- `Ubuntu Manpage: systemd.timer - Timer unit configuration <https://manpages.ubuntu.com/manpages/noble/man5/systemd.timer.5.html>`_
- `systemd.timer 入門 | DevelopersIO <https://dev.classmethod.jp/articles/slug-btThPHViGsPt/>`_

.. rubric:: Footnotes

.. [1] ``[Timer]`` セクションに ``Unit=`` を追記することで起動するユニットを指定可能だが、基本的にはデフォルトのままにしておくことが推奨される模様。また ``Unit=`` ということは対象はサービスに限定されないものと考えられるが、具体的な用例などは不明。
.. [2] 一応、最初の一回だけ ``$ systemctl start xxx.service`` で手動起動する形でも良い
.. [3] 実運用で止まってしまうのも困るのでありがたい挙動ではあるが、シンプルに説明できない感じになってしまっている感がある。
