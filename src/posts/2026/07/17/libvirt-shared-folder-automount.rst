.. post:: 2026-07-17
   :tags: libvirt
   :category: Virtualization

.. meta::
  :description: libvirt の共有フォルダを自動マウントする

======================================
[libvirt] 共有フォルダの自動マウント
======================================

導入
==========

前回の記事 [1]_ で systemd unit についてまとめていた際に ``mount`` というユニットタイプが目に入りました。ちょうど開発用のVMで手動でマウントするのが面倒に思っていたところだったので、設定してみることにしました。

なお libvirt で開発用のVM を作成する方法については :ref:`libvirt-local-vm-quickstart` を参照ください。

環境
=================

- ホストは Manjaro Linux OS
- ゲストは Ubuntu 22.04
- VM は libvirt (QEMU/KVM) で管理
- 共有フォルダは以下の ``virt-install`` 実行時のオプションで設定している

  ::

    --filesystem path/to/myproj,myproj,type=mount,accessmode=passthrough

  - この設定では QEMU/KVM の ``VirtFS（virtio-9p）`` が使用され、マウントタグ名は ``myproj`` となる
  - また ``accessmode=passthrough`` によりVM からはホスト側の UID/GID がそのまま見えるため、ホスト側の作業ユーザも uid, gid をともに ``1000`` に揃え、共有フォルダ内で読み書きを可能にする

systemd.mount
================

systemd でマウントを管理するためのユニットタイプ。

このタイプでは ``[Mount]`` セクションにマウントするリソースとマウント先を指定する形でユニットファイルを作成する。

また、mount ユニットには命名規則があり、ユニットファイル名はマウント先のパスから決まる。

::

  # 例) マウント先
  /home/ykrods/myproj
  # ユニットファイル名
  /etc/systemd/system/home-ykrods-myproj.mount

設定例としては次のようなファイルになる。

.. code-block:: ini
  :caption: /etc/systemd/system/home-ykrods-myproj.mount

  [Unit]
  Description=Libvirt 9p shared folder mount

  [Mount]
  # マウントするリソースの識別子(9p の場合マウントタグ名)
  What=myproj
  # マウント先
  Where=/home/ykrods/myproj
  Type=9p
  Options=trans=virtio

  # [Install]
  # WantedBy=multi-user.target


各項目には、手動でマウントする場合のコマンドライン引数に相当する値を指定する。

うまくマウントできない場合は、まず mount コマンドを直接実行し、指定内容に問題がないか確認すると切り分けやすい。

::

  $ sudo mount -t 9p -o trans=virtio myproj /home/ykrods/myproj

正しく設定されていれば、 ``sudo systemctl daemon-reload`` 実行後
以下のコマンドでマウントとアンマウントを制御できる。

.. code-block:: shell

  $ sudo systemctl start home-ykrods-myproj.mount
  $ sudo systemctl stop home-ykrods-myproj.mount

mountユニットでは、基本的に active がマウント済み、inactive がアンマウント済みの状態に対応する。

OS起動時に自動的にマウントするという目的においては ``[Install]`` セクションを
記述してユニットを ``enable`` する形でも対応できるが、今回は ``automount``
ユニットを作成し、必要になった時点で自動的にマウントするようにする。


automount
==============

``automount`` ユニットがアクティブになると、起動時でなくマウント先が参照された
タイミングで自動的にマウントされる。

- (注) ``automount`` を利用する場合、同名の ``mount`` の設定が必要となる。

また、 ``TimeoutIdleSec`` を指定すると、一定時間マウント先が利用されていない場合に自動的にアンマウントできる。

.. code-block:: ini
  :caption: /etc/systemd/system/home-ykrods-myproj.automount

  [Unit]
  Description=Automount Libvirt 9p Shared Folder
  ConditionPathExists=/home/ykrods/myproj

  [Automount]
  Where=/home/ykrods/myproj
  TimeoutIdleSec=3min

  [Install]
  WantedBy=multi-user.target

設定を読み込み、 automount ユニットを有効化する。

.. code-block:: bash

  $ sudo systemctl daemon-reload
  $ sudo systemctl enable --now home-ykrods-myproj.automount

開発用のVMではVMを起動したまま放置したり、ゲストより先にホストOSをシャットダウンしてしまうことがあるので、
必要なときだけマウントする構成にしておいた方が余計な事故が減ると思われる。

補足: ユニットファイルの命名規則
=================================

``systemd-escape`` というコマンドを使うとマウント先のパスに対応するユニット名を出力してくれる。

::

  $ systemd-escape --path --suffix=mount "/home/ykrods/myproj"
  home-ykrods-myproj.mount
  $ systemd-escape --path --suffix=mount "/home/ykrods/myproj-1"
  home-ykrods-myproj\x2d1.mount
  $ systemd-escape --path --suffix=mount "/home/ykrods/myproj_1"
  home-ykrods-myproj_1.mount

この様にディレクトリ名に含まれるハイフンは ``\x2d`` でエスケープされるようである。

ハイフンを含むディレクトリ名自体に問題があるわけではないが、手動でファイルを作成する場合は
注意が必要かと思われる。


余談: 自動アンマウントされない?
==================================

検証時に ``TimeoutIdleSec`` で指定した時間が経過してもアンマウントされなかった。

ログを確認したところ、以下のメッセージが出ていた

.. code-block:: bash

  # $ sudo journalctl -u home-ykrods-myproj.automount

  Got automount request for /home/ykrods/myproj, triggered by 351 (reader#0)

reader#0 とは何か調査したところ、検証環境で動作していた ``collectd`` のプロセスだった。

``collectd`` が定期的にディスク容量を確認するためマウント先へアクセスしており、
アイドル状態にならなかったことが、自動アンマウントされない原因だった。

どちらかというとレアケースだと思われるが、同じような問題があったときに監視系の
サービスを疑うのは一考の余地があるかもしれない。

参考
======

- `systemd.mount(5) <https://www.freedesktop.org/software/systemd/man/latest/systemd.mount.html>`_
- `Documentation/9psetup - QEMU <https://wiki.qemu.org/Documentation/9psetup>`_

.. rubric:: Footnotes

.. [1] :ref:`systemd-timer`
