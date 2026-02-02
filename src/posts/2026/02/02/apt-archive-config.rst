.. post:: 2026-02-02
   :tags: ubuntu, apt, security, ansible
   :category: security

.. meta::
  :description: apt アーカイブの記述方法について、armor の解説や keyring の配置場所についてまとめた

========================================
apt アーカイブの記述方法
========================================

導入
=========

`任意のバージョンの Redis を Ubuntu 22.04 にインストールする方法 <https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-linux/#install-on-ubuntudebian>`_ として、公式ドキュメントに以下のコマンドが記載されている。

.. code-block:: shell

  # 抜粋
  $ curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
  $ echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

簡単に説明すると、apt には apt アーカイブ(apt パッケージの配布元)から取得したパッケージの真正性を検証する仕組みがデフォルトで備わっており、その検証の際にアーカイブ鍵が必要となる。そのため上記のコマンドでは以下のことを行っている。

* 1行目: https://package.redis.io/ から鍵をダウンロードしてローカルに保存
* 2行目: https://package.redis.io/deb のアーカイブでは 1行目で保存した鍵を利用するように対応づけ

redis を例に挙げたが、docker や google cloud cli などでも同じような手順で apt パッケージを利用できるようになっている。

この手順によりインストールは問題なく行えるのだが、ネット上の関連記事を見てみると「dearmor はしなくて問題ない」「/usr/share/keyrings に置かない方がいい」など色々な話題があり、結局どうするのがいいのか不明だったので、諸々を調べた。結論を先に述べておくとどういう構成にしろクリティカルな問題が起きるような話ではなかったので、気になった人が読んでいただければ良い内容かと思う。


ASCII armor とは
==================

まず ``--dearmor`` について理解するには ASCII armor について知る必要がある。

`13. ASCII armor — OpenPGP for application developer <https://openpgp.dev/book/armor.html>`_ より引用すると

    The native format of OpenPGP data is binary.

    However, in many use cases it is customary to use OpenPGP data in a non-binary encoding called “ASCII armor.” For example, ASCII armored OpenPGP data is often used in email, for encrypted messages or for signatures.

    # 拙訳
    OpenPGP データのネイティブな形式はバイナリである。

    しかし、多くのユースケースで OpenPGP データを ASCII armor と呼ばれる非バイナリエンコーディングで使用することが通例となっている。例えば ASCII armored な OpenPGP データは暗号化されたメッセージや署名のためにメールの中でよく使用される。

つまり apt パッケージの配布元から提供されているgpg鍵が ASCII armor エンコードされており、 ``--dearmor`` はそれをバイナリに戻す処理を行っている、ということになる。gpg が公開鍵暗号技術なので「署名の検証などしてるんじゃないの？」と思ってしまうが、ASCII armor に関しては単なるエンコード・デコード以上のことはしていない。

そうなると次に「なぜ単なるエンコードを armor (装甲) と呼ぶのか？」と言う疑問が湧いてくる。これに関しては一次的かつ端的な解説が見つからなかったが、 `RFC9580 <https://www.rfc-editor.org/rfc/rfc9580.html>`_ に次の文章がある。

    2.4. Conversion to Base64

    OpenPGP's underlying representation for encrypted messages, signatures, keys, and certificates is a stream of arbitrary octets. Some systems only permit the use of blocks consisting of 7-bit, printable text. For transporting OpenPGP's raw binary octets through channels that are not safe to transport raw binary data, a printable encoding of these binary octets is defined. The raw 8-bit binary octet stream can be converted to a stream of printable ASCII characters using base64 encoding in a format called "ASCII Armor" (see Section 6).

    # 拙訳
    OpenPGP の暗号化されたメッセージ、署名、鍵、証明書の基礎となる表現は任意のオクテットのストリームである。いくつかのシステムでは 7-bit, 表示可能なテキストで構成されるブロックのみ使用することを許している。生のバイナリデータを転送する上で安全でないチャンネルを通じて OpenPGP の生のバイナリオクテットを転送するため、それらのバイナリオクテットの表示可能なエンコーディングが定義された。生の 8-bit バイナリオクテットのストリームは "ASCII Armor" と呼ばれるフォーマットで base64 エンコーディングを使った表示可能な ASCII 文字列のストリームに変換できる (Section 6 を参照)。

この文章から ASCII armor は 7-bit (ASCII) データしか扱えない転送経路で鍵などの OpenPGP のバイナリデータを送るために利用されるという事がわかる。先ほどのメールで使用されるという記述も踏まえると、具体的な転送経路というのは、 SMTP のことを指していると考えられる。

SMTP の初期は 7-bit の ASCII 文字列のみを扱う設計で、オクテットの先頭1ビットは常に 0 という前提で処理されるため [1]_ 、バイナリデータをそのまま送るとデータの欠損が起こりうる。そのため、「欠損からデータを保護する」というニュアンスで ASCII armor という呼び方になったようだ。 [2]_

ここまでで ``--armor`` の意義は理解できたが、そうなると新たな疑問が生まれてくる。「apt の鍵の配布においては HTTPS（= HTTP over TLS）はバイナリデータを送信できるのだから、ASCII armor エンコーディングは不要では？」という疑問である。

正直これに関しては推測するしかないが

1. 「転送時は ASCII armored 形式にする」という慣習の面
2. 「単純にテキストの方が メールやチャット、htmlの本文などにも埋め込みやすい」という利便性の面
3. 「新しいバージョンの apt では Signed-By に ASCII armored のテキストファイルも対応しているため、今後はこちらの方が主流になる(?)」という将来性の面

がそれぞれあり、元々の保護という観点からは別の面で現状の形になっているように思える。3 については後述するが、おそらく 3 が過渡期であるため、典型的なインストールガイドではどれも無難な（伝統的な）慣習を守って dearmor してローカルに保存しているのはないかと思われる。


/usr/share/keyrings と /etc/apt/keyrings
=============================================

`man 5 sources.list <https://manpages.ubuntu.com/manpages/jammy/en/man5/sources.list.5.html>`_ に

    The recommended locations for keyrings are /usr/share/keyrings for
    keyrings managed by packages, and /etc/apt/keyrings for keyrings managed by the system operator.

と記述されており

* ``/usr/share/keyrings`` はパッケージ管理された鍵ファイルをおく
* ``/etc/apt/keyrings`` はシステム管理者が追加する鍵ファイルを置く

という使い分けが推奨されている。実際 ``/usr/share/keyrings`` を覗いてみると ``ubuntu-archive-keyring.gpg`` があり、これは ``ubuntu-packages`` により管理されている。

::

  $ dpkg -S /usr/share/keyrings/ubuntu-archive-keyring.gpg
  ubuntu-keyring: /usr/share/keyrings/ubuntu-archive-keyring.gpg

`man 8 apt-key <https://manpages.ubuntu.com/manpages/jammy/en/man8/apt-key.8.html>`_ でも同じような記載があり

    Recommended: (...略...)
    Since APT 2.4, /etc/apt/keyrings is provided as the recommended
    location for keys not managed by packages. When using a deb822-style sources.list, and with apt version >= 2.4, the Signed-By option can also be used to include
    the full ASCII armored keyring directly in the sources.list without an additional file.

apt 2.4 以降ではパッケージ管理されていない鍵は ``/etc/apt/keyrings`` 以下に保存することが推奨とされている。

* redis などの apt アーカイブの手順で ``/usr/share/keyrings`` が記述されているのは、おそらく古い apt 環境との互換性や、従来のドキュメントとの整合性を考慮した結果ではないかと思われる

また前節で一度触れたが `man 8 apt-key <https://manpages.ubuntu.com/manpages/jammy/en/man8/apt-key.8.html>`_ では apt 1.4 以上では拡張子 .asc の ASCII armored 形式を使用できるという記述がある

    Alternatively, if all systems which should be using the created keyring have at least apt version >= 1.4 installed, you can use the ASCII armored format with the
    "asc" extension instead which can be created with gpg --armor --export.

まとめ
====================

* ``--dearmor`` は ASCII armor されたテキストを、OpenPGP のバイナリ形式に戻すだけ で、セキュリティ上の意味はない
* ``/etc/apt/keyrings`` は新しい置き場所で ``.asc`` で鍵を配置しても既存の何かに影響が出るということもないと予想される

ということで、

::

  $ curl -fsSL -o /etc/apt/keyrings/redis-archive-keyring.asc https://packages.redis.io/gpg
  $ echo "deb [signed-by=/etc/apt/keyrings/redis-archive-keyring.asc] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list

としてしまっても概ね問題はないと言える。前述したように環境によって動かないという可能性もなくはないので、指示通りの手順でも問題はない。

(おまけ1) DEB822 形式
========================

aptアーカイブの記述方法として、コマンド2行目で出てきたワンライナーの記述に変わり、 ``DEB822`` 形式が推奨されている。

例えば redis の場合は以下のように記述できる

.. code-block::
  :caption: /etc/apt/sources.list.d/redis.sources

  Types: deb
  URIs: https://packages.redis.io/deb
  Suites: jammy
  Components: main
  Signed-By: /etc/apt/keyrings/redis-archive-keyring.asc

* DEB822 形式の場合、拡張子は .list でなく .sources となることに注意

また、手前の引用の中で既に出ていたが ``man 8 apt-key`` で apt 2.4 以上で DEB822 形式でソースを記述する場合、Signed-by に ASCII armored keyring を直接記述できると書いてある。 ``man 5 sources.list`` の Signed-By の項目には具体例も示されている。

::

  Types: deb
  URIs: https://deb.debian.org
  Suites: stable
  Components: main contrib non-free
  Signed-By:
   -----BEGIN PGP PUBLIC KEY BLOCK-----
   .
   mDMEYCQjIxYJKwYBBAHaRw8BAQdAD/P5Nvvnvk66SxBBHDbhRml9ORg1WV5CvzKY
   CuMfoIS0BmFiY2RlZoiQBBMWCgA4FiEErCIG1VhKWMWo2yfAREZd5NfO31cFAmAk
   IyMCGyMFCwkIBwMFFQoJCAsFFgIDAQACHgECF4AACgkQREZd5NfO31fbOwD6ArzS
   dM0Dkd5h2Ujy1b6KcAaVW9FOa5UNfJ9FFBtjLQEBAJ7UyWD3dZzhvlaAwunsk7DG
   3bHcln8DMpIJVXht78sL
   =IE0r
   -----END PGP PUBLIC KEY BLOCK-----

* Signed-By の中の `.` は空行を表すために必要とのこと

例だけ見ると１ファイルにできて便利なのではと思ったりもするが、実際に redis-archive.asc などを見てみると 52行あるので個人的にはファイルは分けたほうが見通しが良さそうに思う。

(おまけ2) fingerprint と構成管理の雑感
========================================

ここまで触れてこなかった観点で、アーカイブ鍵によりパッケージの真正性が検証できるとして、では鍵の真正性はどうやって検証するのかという問題がある。
鍵の fingerprint がガイドやリリースノートなどに記載されている場合はダウンロードした鍵ファイルの fingerprint を取得して一致するか確認することはできるが、redis など大体のアーカイブでは fingerprint の記載は特にない。これが「HTTPS(tls) だからヨシ！」というスタンスなのかはわからないが、完璧に安全な fingerprint の提供方法というのも考えると結構難しかったり運用負荷になったりするので、その辺は割り切りなのだと思われる。 [3]_

この面を踏まえると Debian/Ubuntu の archive key であれば最初から OS 配布物として埋め込まれており、パッケージ管理されているので鍵の更新も apt update で可能となっており、より安全性は高いように思う。

また、鍵自体の安全性を人間が確認する必要があるのであれば、ansible などで構成管理する場合は鍵を確認した後 asc ファイルを設定ファイルとして
リポジトリに追加してしまった方が都度実行時にダウンロードするより安全だと思うがどうなんだろうか。

アーカイブ管理者が持つ秘密鍵が何らかの理由で漏洩した場合、ユーザ側の鍵は破棄した方が良いということになりそうだし、アーカイブ
管理者の運用方法として鍵を定期的に変えるというものもパターンとしてはあり得ると思うが、そのあたりは各々のアーカイブ管理者に判断が委ねられていて、
特にリファレンスがないのでどうした方がいいというのは一概に言えない気がしている。

とりあえず、先ほどダウンロードした redis-archive-keyring の fingerprint を記載しておくが、これが確実に正しいかはわからない。

.. code-block:: shell

  $ gpg --show-keys --with-fingerprint /etc/apt/keyrings/redis-archive-keyring.asc
  gpg: keybox '/home/ubuntu/.gnupg/pubring.kbx' created
  pub   rsa4096 2021-07-21 [SC]
        5431 8FA4 052D 1E61 A6B6  F7BB 5F43 49D6 BF53 AA0C
  uid                      Redis (Package Signing) <redis-packages@redis.io>
  sub   rsa4096 2021-07-21 [E]

  # こっちのコマンドだと keybox を作らないようなのでこっちの方が良いのだが、.gpg しか対応していない?
  $ gpg --no-default-keyring --keyring redis.gpg --list-keys --with-fingerprint --quiet
  ./redis.gpg
  -----------
  pub   rsa4096 2021-07-21 [SC]
        5431 8FA4 052D 1E61 A6B6  F7BB 5F43 49D6 BF53 AA0C
  uid           [ unknown] Redis (Package Signing) <redis-packages@redis.io>
  sub   rsa4096 2021-07-21 [E]


参考
========

* `gpg - What is the armored option for in GnuPG? - Unix & Linux Stack Exchange <https://unix.stackexchange.com/questions/623375/what-is-the-armored-option-for-in-gnupg>`_
* `Ansibleでgpg公開鍵とaptのサードパーティリポジトリを追加する ～Terraformをインストールしたい～ - Sogo.dev <https://sogo.dev/posts/2023/03/ansible-apt-repo-signed-by-gpg-key>`_
* `Debian APTの鍵を安全に追加する方法 <https://zenn.dev/takc923/articles/391ea8a4e03f43>`_
* `第675回　apt-keyはなぜ廃止予定となったのか | gihyo.jp <https://gihyo.jp/admin/serial/01/ubuntu-recipe/0675>`_

.. rubric:: Footnotes

.. [1] あまりはっきりとした解説が見つからなかったが、ソフトウェアによって 先頭ビットを無視して ASCII 文字列として読み込まれた結果データとして欠損するということなのだろうか？
.. [2] 後に ESMTP (Extended SMTP) 拡張機能により8-bitデータをそのまま送れる様になった
.. [3] パッケージ配布元と同じドメインで fingerprint を公開しても、そのドメイン自体が安全でなかったら fingerprint も偽装される可能性があるなど
