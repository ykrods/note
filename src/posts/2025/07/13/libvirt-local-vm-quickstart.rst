.. post:: 2025-07-13
   :tags: libvirt
   :category: Virtualization

.. meta::
  :description: libvirt で開発環境をつくる

=================================================
ローカル開発用の VM を構築するための速習 libvirt
=================================================

導入
=================

個人的にローカル開発用の仮想マシン(以下 VM)を構築するのに snap の multipass を利用していましたが、VM を停止できなくなったり、status が unknown になったりとどうも不安定 [1]_ なので、いっそのこと `libvirt <https://libvirt.org/>`_ を使ってみることにしました。そのため、必要知識を整理しました。

基礎
=================

- libvirt は openvz, kvm, qemu, virtualbox, xen などの仮想化エンジンを統一的に制御するためのAPI群
- 最近はハイパーバイザーとして Qemu/KVM が用いられる
- libvirt の cli として virsh, virt-install がある

接続タイプ
-------------

libvirt の接続タイプとして ``qemu:///system`` と ``qemu:///session`` がある

``qemu:///system``

- root ユーザあるいは ``libvirt`` ユーザグループに属しているユーザはシステム接続になる

``qemu:///session``

- ``libvirt`` ユーザグループに属していない非 root ユーザはセッション接続になる
- 他のユーザ(root を含む)によって作成された仮想マシンにはアクセスできない
- セッション接続ではネットワークの作成が不可、VM の自動起動設定が不可などの制限がある

接続タイプの確認は以下のコマンドで行える

.. code-block:: bash

  $ virsh uri
  qemu:///session
  $ sudo virsh uri
  qemu:///system

システム接続の方がやれることは多いが、開発目的ではセッション接続で十分だと思われるので、以後その前提で進める。 [2]_

環境構築
===============

- libvirt, virt-manager, passt をインストール

  .. code-block:: bash

    # arch系ディストリビューションの場合
    $ sudo pacman -S libvirt passt virt-manager

- デフォルトでインストールされている場合もある [3]_
- virt-manager は VM を管理するための GUI ツールなので必須ではないが、libvirt では VM 等の設定が xml で管理されるので GUI で確認・編集できた方が便利


セッション接続の場合、libvirt デーモンは不要だが、一応状況を確認しておく

.. code-block:: bash

  $ sudo systemctl status libvirtd
  $ sudo systemctl status virtqemud
  $ sudo systemctl status virtnetworkd
  $ sudo systemctl status virtstoraged

- libvirtd はレガシーで現在はモジュールに分割された複数のデーモンで構成される

  - virtqemud, virtnetworkd, virtstoraged など
  - 稼働中の VM がなければ libvirtd より分割されたデーモンを使う方がよいと思われる

VM の作成(1): イメージ
=========================

開発用の VM を作成するたびに毎回対話的に設定を行うのは面倒なのでクラウドイメージ [4]_ と cloud-init を使う

- Ubuntu では以下のサイトでクラウドイメージが配布されている

  - https://cloud-images.ubuntu.com/

- VM 内の変更はクラウドイメージに直接書き込まれる形になる
- cloud-init は二重に実行されないための仕組みがあり、cloud-init が実行済み状態のディスクイメージに対して設定の変更が反映されない場合がある

上記の都合により cloud-init の検証時は毎回新しいイメージを作成する必要があり、都度コピーをとったりダウンロードしなおすのは面倒なので、差分イメージを利用する

差分イメージ
----------------

qemu の機能でその名前のとおり対象のイメージからの差分情報のみを含んだイメージを作成できる

- ベースイメージへは絶対パスで参照するのでベースイメージの配置を変えてはいけない

  - 変える必要がある場合は ``$ qemu-img rebase`` でパスを書き換える

- ベースイメージは上書きするのも NG なので日付などで管理し、書き込みも禁止しておく

.. code-block:: bash

  # ディレクトリ構成はお好みでよいが運用の一例としてこんな感じかと
  $ mkdir -p ~/libvirt/{base,vms}
  $ cd ~/libvirt
  $ curl -o base/ubuntu-22.04-20250702.qcow2 https://cloud-images.ubuntu.com/jammy/20250702/jammy-server-cloudimg-amd64-disk-kvm.img
  $ chmod 444 base/ubuntu-22.04-20250702.qcow2

  # 差分イメージを作成する。ディスクサイズもここで指定する。
  $ qemu-img create -f qcow2 -b $HOME/libvirt/base/ubuntu-22.04-20250702.qcow2 -F qcow2 vms/myvm1.qcow2 16G

  # イメージの確認
  $ qemu-img info vms/myvm1.qcow2

.. tip::

  qcow2 は qemu で使用されるイメージフォーマット

VM の作成(2): cloud-init
==============================

cloud-init を使う際、以前は設定情報を記述した user-data.yaml と meta-data.yaml を含んだ ``seed.iso`` を作る必要があったが ``virt-install`` の ``--cloud-init`` オプションを使うと yaml ファイルを直接指定できる。

しかし環境によっては ``--cloud-init`` オプションが期待した通りに動作しないこともあるらしいので、一旦最低限の VM を作成し動作検証する。この状態ではネットワーク設定をしていないので VM からインターネットに接続したり外から ssh ができない。

user-data.yaml

.. code-block:: yaml

  #cloud-config
  ssh_pwauth: false
  users:
    - default
  chpasswd:
    list: |
      ubuntu:ubuntu
    expire: False

- Ubuntu のクラウドイメージでは、default ユーザは "ubuntu" という名前で作成される
- 明示的に users で指定しないと ubuntu ユーザは作成されない
- デフォルトで ``ubuntu`` ユーザのパスワードは設定されていないため、 ``chpasswd`` でパスワード( ``ubuntu`` ) を設定する [5]_
- ssh 接続(公開鍵)を設定した場合はパスワードは不要となるが、最初のうちは console で接続できるようにパスワードを設定した方が良いと思われる

.. tip::

  好みが分かれるところだと思われるが、 ``default`` でなく明示的に ubuntu ユーザを指定してもよい

  .. code-block:: yaml

    #cloud-config
    ssh_pwauth: false
    users:
    - name: ubuntu
      uid: 1001
      gecos: Ubuntu
      sudo: ALL=(ALL) NOPASSWD:ALL
      shell: /bin/bash
      lock_passwd: false
      plain_text_passwd: ubuntu

meta-data.yaml

.. code-block:: yaml

  instance-id: myvm1
  local-hostname: myvm1

* instance-id はなんでもよいため上記では myvm1 としているが、 ``$ uuidgen`` で uuid を生成するのが無難か


user-data.yaml と meta-data.yaml を作成後、以下のコマンドで VM を作成する。

.. code-block:: bash

  $ virt-install \
      --name myvm1 \
      --autoconsole text \
      --import \
      --memory 2048 --vcpus=2 \
      --osinfo generic \
      --disk bus=virtio,path="$HOME/libvirt/vms/myvm1.qcow2" \
      --cloud-init user-data=user-data.yaml,meta-data=meta-data.yaml


- ``--autoconsole`` で自動的に ``$ virsh console myvm1`` を行いシリアル接続する
- 最初のうちは console で入って cloud-init が期待した設定になっているかは確認したほうがよい。不要な場合は ``--noautoconsole`` に変える。
- 起動後に ``ubuntu/ubuntu`` でログインできるか確認する
- cloud-init の状態は ``$ cloud-init status`` コマンドや ``/var/log/cloud-init.log`` のログで確認する
- console は ``ctrl+]`` で抜ける

seed.iso
----------

``--cloud-init`` が期待した動作にならない場合、以下のコマンドで seed.iso を作成してみる

.. code-block:: bash

  $ genisoimage -output seed.iso -volid cidata -joliet -rock user-data.yaml meta-data.yaml

virt-install の ``--cloud-init`` オプションを以下に変更する

::

  --disk path=seed.iso,device=cdrom


VM の操作
================

よく使うコマンドを例に挙げる。

.. code-block:: bash

  $ virsh start myvm1  # 停止中の VM を起動
  $ virsh shutdown myvm1  # 起動中の VM を停止
  $ virsh destroy myvm1  # 起動中の VM を強制停止
  $ virsh undefine myvm1 # VM を登録解除
  $ virsh undefine myvm1 --remove-all-storage  # VM を登録解除してディスク( ~/libvirt/vms/myvm1.qcow2 など) を削除
  $ virsh console myvm1  # VM にシリアル接続
  $ virsh dumpxml myvm1  # VM の設定を出力(xml)
  $ virsh edit myvm1  # VM の設定を編集

``virt-manager`` では xml を直接編集せずに GUI で設定の変更が可能 ( すべての設定に対応しているわけではない )

ネットワーク
================

セッション接続でネットワークを利用する場合、 ``passt`` が利用できる。 ``passt`` ではホストから VM へのアクセスはポートフォワーディングを用いる。

先ほどの VM を削除し、 ``virt-install`` にネットワークオプションを追加する。また、 ``user-data.yaml`` を編集し、ssh 接続用のユーザを追加する。

.. tip::

  VM を削除しなくても設定の変更でネットワーク設定を追加することもできる

.. code-block:: yaml

  #cloud-config
  ssh_pwauth: false
  users:
    - default
    - name: yourname
      lock_passwd: true
      sudo: ALL=(ALL) NOPASSWD:ALL
      uid: 1000
      shell: /bin/bash
      ssh_authorized_keys:
      - ssh-rsa AAAAB3Nz...(略, .ssh/id_ed25519.pub 等の内容をコピペ)
  chpasswd:
    list: |
      ubuntu:ubuntu
    expire: False

.. code-block:: bash

  $ virsh shutdown myvm1
  $ virsh undefine myvm1 --remove-all-storage
  $ # イメージ再作成
  $ qemu-img create -f qcow2 -b $HOME/libvirt/base/ubuntu-22.04-20250702.qcow2 -F qcow2 vms/myvm1.qcow2 16G

  $ virt-install \
     --name myvm1 \
     --autoconsole text \
     --import \
     --memory 2048 --vcpus=2 \
     --osinfo generic \
     --disk bus=virtio,path="$HOME/libvirt/vms/myvm1.qcow2" \
     --network passt,model=virtio,portForward=20222:22 \
     --cloud-init user-data=user-data.yaml,meta-data=meta-data.yaml

これにより、VM からのインターネット接続と、ssh接続 (ローカルの ``20222`` を ``22`` にポートフォワーディング ) ができる。

- VM を複数起動する場合、ローカルポートはかぶらないようにする（若干面倒）

.. code-block:: bash

  $ ssh -i .ssh/id_ed25519 -p 20222 yourname@localhost

.. tip::

  portForward はコマンドラインからでは複数設定できない(?) ようなので、複数のポートを公開したい場合は xml を編集する必要がある

  .. code-block:: xml

    <!-- 追加で 8000番ポートを開ける例 -->
    <interface type="user">
      <mac address="52:54:00:62:e2:d6"/>
      <portForward proto="tcp">
        <range start="20222" to="22"/>
        <range start="8000" to="8000"/>
      </portForward>
      <model type="virtio"/>
      <backend type="passt"/>
      <alias name="net0"/>
      <address type="pci" domain="0x0000" bus="0x00" slot="0x03" function="0x0"/>
    </interface>

フォルダ共有
===================

ファイルシステムのドライバーとして ``virtio-9p`` (デフォルト) と ``virtiofs`` が選択できる

- パフォーマンスは ``virtiofs`` の方がよいらしいが、 ``virtiofs`` をセッション接続で用いる場合、ゲストOSの共有対象のディレクトリのユーザがホストOSの root にマッピングされるため [6]_ 、ゲストOS側のログインユーザでは Permisson Error が起きる可能性があり、使い勝手が若干よくない。
- 共有フォルダに書き込みを行う場合は 9p の方が楽なので、ここでは virtio-9p を使う。ただし、ホストOS とゲストOS で UID/GID を揃える必要がある。

共有フォルダを利用する場合、 ``virt-install`` に以下のような ``--filesystem`` オプションを追加する

::

  --filesystem $HOME/path/to/shared,shared,type=mount,accessmode=passthrough \

VM にログインして以下のコマンドでマウントする

.. code-block:: bash

  $ mkdir shared
  $ sudo mount -t 9p -o trans=virtio shared shared

virtiofs の場合
-------------------

``virtiofs`` を利用する場合は ``--memorybacking`` の設定が追加で必要になる。

.. code-block:: bash

  # virtiofs が利用できるか確認
  $ modinfo virtiofs

.. code-block:: bash

  # virt-install のオプションに以下を追加
  --memorybacking source.type=memfd,access.mode=shared \
  --filesystem $HOME/path/to/host/shared,shared,type=mount,driver.type=virtiofs \

``virtiofs`` の場合の ``mount`` コマンドは以下

.. code-block:: bash

  $ mkdir shared
  $ sudo mount -t virtiofs shared shared

.. tip::

  VSCode では remote-ssh, sftp, rsync などいろいろなファイル同期手段があるので、開発用途VM としてはそれらを使うのもよい

おまけ: システム接続でのコマンド
======================================

あまり検証してないメモ書きなので、参考程度に

環境設定

.. code-block:: bash

  $ sudo systemctl status libvirtd
  $ sudo systemctl enable --now virtqemud.socket
  $ sudo systemctl enable --now virtnetworkd.socket
  $ sudo systemctl enable --now virtstoraged.socket
  $ sudo systemctl start virtqemud
  $ sudo systemctl start virtnetworkd
  $ sudo systemctl start virtstoraged

ネットワーク設定

.. code-block:: bash

  # net-undefine したときに xml ごと消されることがあるのでバックアップしておく
  $ sudo cp /etc/libvirt/qemu/networks/default.xml /etc/libvirt/qemu/networks/default.xml.bak

  # ネットワークを作成
  $ sudo virsh net-define /etc/libvirt/qemu/networks/default.xml
  $ sudo virsh net-autostart default
  $ sudo virsh net-start default
  $ sudo virsh net-list --all

  # ネットワークの自動起動解除
  $ sudo virsh net-autostart --disable default
  # ネットワークの削除（xml も同時に消される模様）
  $ sudo virsh net-undefine default


VM でネットワーク利用

::

  --network bridge=virbr0,model=virtio \
  # or
  --network default,model=virtio \

IP の確認

.. code-block:: bash

  $ virsh domifaddr myvm1
  $ sudo virsh net-dhcp-leases default
  $ sudo virsh dumpxml myvm1 | grep interface -A 10

VM 側でのネットワークインターフェイスの確認・有効化

.. code-block:: bash

  $ ip -br addr show
  $ sudo ip link set virbr0 up


参考
============

- `libvirt: Sharing files with Virtiofs <https://libvirt.org/kbase/virtiofs.html>`_
- `1.5. 仮想化のユーザー空間接続タイプ | Linux 仮想マシンの設定と管理 | Red Hat Enterprise Linux | 10 | Red Hat Documentation <https://docs.redhat.com/ja/documentation/red_hat_enterprise_linux/10/html/configuring_and_managing_linux_virtual_machines/user-space-connection-types-for-virtualization>`_
- `Launch QCOW images using libvirt - Ubuntu Public Images documentation <https://documentation.ubuntu.com/public-images/public-images-how-to/launch-with-libvirt/>`_
- `ubuntu cloud image の見分け方 #Ubuntu - Qiita <https://qiita.com/kwi/items/f3cfaa8f7a4a5384a5e2>`_
- `Using virtiofs with libvirt/virt-install - A Random Walk Down Tech Street <https://dustymabe.com/2023/09/08/using-virtiofs-with-libvirt/virt-install/>`_

..
  pacman -Qk libvirt  # パッケージ管理されたファイルのチェック
  sudo pacman -S libvirt  # パッケージの再インストール


.. [1] 筆者は Manjaro Linux を使っているが、Ubuntu ホストで動作させた方が安定するらしい?
.. [2] ログインユーザを ``libvirt`` グループに参加させるのでもよいが、せっかくユーザ向けに動く環境が用意されているのだからそれを使おうという判断。共有の開発サーバを立ち上げるような場合ではシステム接続が適する。
.. [3] passt は podman の依存パッケージでもあるので知らずに使っている事も
.. [4] パブリッククラウド上で実行するためにカスタマイズされたイメージ
.. [5] ちなみにパスワードの設定有無は ``$ sudo cat /etc/shadow`` でわかる
.. [6] このマッピングには Linux のユーザ名前空間 (user namespace) が利用されている
