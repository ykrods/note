.. post:: 2020-04-21
   :tags: RSA, Cryptography
   :category: Cryptography

.. meta::
  :description: 「RSAではメッセージを秘密鍵で暗号化して署名を生成する」は正しいのか

========================================================
メッセージと秘密鍵から署名を生成する
========================================================

「RSAではメッセージを秘密鍵で暗号化して署名を生成する」は正しいのか

背景
=========

デジタル署名についてインターネットを検索するとその仕組みを解説したページが複数ヒットしますが、同時にその説明は間違ってるよというブログ等での指摘も複数出てきます。

そうした指摘事項の一つに「RSAではメッセージ（またはそのハッシュ値）を秘密鍵で暗号化して署名を生成する」という説明は「暗号化」という用語を誤用している、というものがあります。

指摘の根拠としては、暗号化は「何らしかのデータを特定の相手のみが解読（＝復号）できるデータに変換すること」であり、不特定多数が解読できるデータである署名データを暗号化した、とは言えないだろうという事の様です。

そう言われると一理ある気がしますが、これが単純に用語の定義の問題であるならば、暗号の専門家でなくても正誤が判断できるはずです。というわけで調べることにしました。

なお、その他の暗号化・署名に関する正誤の議論は話がややこしくなるのでここでは扱いません。

暗号化という用語
========================

まず初めに技術的な用語の定義ということでJIS規格を調べました。

どうやら JIS X 0008 情報処理用語（セキュリティ） に「08.03.02 暗号化」という記載がある様なのですが、
JIS X 0008 は 2017/12/20 に廃止された様で、閲覧できませんでした。

.. note::

  国会図書館にはある？と思われるので今の状況が落ち着いたらいくかもしれない

出落ちの様な展開ですが、どのみちグローバルスタンダードは確認する必要があるので 暗号化 === encryption として、encryption の定義を確認します。

encryption という用語
======================

`RFC 4949 - Internet Security Glossary, Version 2 <https://tools.ietf.org/html/rfc4949>`_ から引用します。


    $ encryption

      1. (I) Cryptographic transformation of data (called "plain text")
      into a different form (called "cipher text") that conceals the
      data's original meaning and prevents the original form from being
      used. The corresponding reverse process is "decryption", a
      transformation that restores encrypted data to its original form.
      (See: cryptography.)


::

  # 拙訳
  データのオリジナルの意味を秘匿し、オリジナルの形式を利用されることを防ぐ、
  データ（プレーンテキスト）から異なる形式（暗号文）への暗号変換。
  対応する逆の処理 (暗号化されたデータを元の形式に戻す変換) は "復号化(decryption)" 。

特定の相手のみが解読できる、という点については直接的な表現はありませんが、「秘匿(conceal)し、オリジナルの形式を利用されることを防ぐ」というフレーズにはそのニュアンスは含まれていると思えます。

例えばこの定義で行くと、「RSAではメッセージを秘密鍵で秘匿し、オリジナルの形式が利用されることを防ぐためのデータに変換して署名を生成する」という言い換えができるはずですが、署名は秘匿された情報でもなければ、オリジナルのデータと一緒に送信する以上オリジナルの形式が利用されることを防ぐものでもないので、定義に合致していないと言えます。 [1]_

ここまでで「定義上は合ってないんじゃない？」と思えますが、明確に違うという記述も無いので別の文章も見ましょう（まぁ悪魔の証明的な感がありますが）。

技術文書上の記載
==================

他の技術文章でどういう使われ方をされているかという事で、関連文書を時系列順に並べました。

New Directions in Cryptography
----------------------------------

:著者: Diffie, Hellman
:公開: 1976年
:原文: `New Directions in Cryptography <https://ee.stanford.edu/~hellman/publications/24.pdf>`_

この論文はRSAが世に出る前のものですが、流れを追う意味で触れておきます。

この論文で初めて公開鍵暗号という新しいコンセプトが公表されました。それは既存の共通鍵暗号が持つ鍵配送問題を解決する大変に革新的なものでしたが、それを実現する鍵となる一方向関数はこの時点で見つかっていませんでした。 [2]_

この論文が署名とどう関わってくるかですが、この論文中では公開鍵暗号の応用でデジタル署名も実現できることが示されており、手順として以下のように説明されています。

    A public key cryptosystem can be used to produce a true one-way authentication system as follows. If user A wishes to send a message M to user B, he “deciphers” it in his secret deciphering key and sends :math:`D_A(M)`. When user B receives it, he can read it, and be assured of its authenticity by “enciphering” it with user A’s public enciphering key :math:`E_A`.

    ( IV. One-Way AUTHENTICATION より引用

ここで使われているのは “decipher”です。 cipher は電子化以前も含んだ「暗号」（有名な例としてはエニグマなど）を表すので、あえて表現するなら「メッセージを“解読”して署名を生成」となります。当然、平文を解読というのはよく話からない話ですが、引用符を使っていることからも分かる通り単語をそのままの意味では使っていないと見るのが妥当で、あくまで手段として decipher と同じ変換をすることで署名ができるということでしょう。


A Method for Obtaining Digital Signatures and Public-Key Cryptosystems
------------------------------------------------------------------------

:著者: Ron Rivest, Adi Shamir, Leonard Adleman
:公開: 1977年
:資料: `A Method for Obtaining Digital Signatures and Public-Key Cryptosystems <https://people.csail.mit.edu/rivest/Rsapaper.pdf>`_

New Directions in Cryptography が公開された翌年、前述した一方向関数を発見したのが、リヴェスト・シャミア・アドルマンの３人になります [3]_ 。

ちなみに RSA はこの論文の著者三名の頭文字をとって命名されたものですが、この論文内ではまだ RSA という単語自体でてきていません。

この論文では署名について以下のように記されています。


    How can user Bob send Alice a “signed” message M in a public-key cryptosystem?
    He first computes his “signature” S for the message M using :math:`D_B`:

    .. math::

       S = D_B(M) .

    (Deciphering an unenciphered message “makes sense” by property (d) of a publickey cryptosystem: each message is the ciphertext for some other message.)

    ( IV Signatures より引用

文章としては 「Bob の復号鍵でメッセージに対する署名を計算する」で、何をしているかというと Deciphering です。カッコ書きで書かれていることから「（奇妙に思うだろうけど）平文を解読(復号)することには意味があります」というようなニュアンスになるかと思います。

ちなみに、この論文内では encipher / decipher と encrypt / decrypt を区別なく利用しているように読めるので復号どちらを使っても問題ないと思われます。（decryption key という単語が出てくるので、復号で統一でもいいかもしれない）。

RFC 2313 - PKCS #1: RSA Encryption Version 1.5
-------------------------------------------------

:公開: 1998年5月

PKCS #1 は RSA Security LLC (上述した３人により設立された会社）により作成された標準です。Ver 1.0 - 1.3 は 1991年に非公開で発行され、Ver 1.4 は同年に NIST/OSI 実装者向けワークショップドキュメント SEC-SIG-91-18 として発行されています。RSA暗号の特許は1983年に取得され2000年まで有効だったので、その辺りの事情に合わせて Ver 1.5 になってからRFC化されたものと思われます。

Ver1.5 での注目すべき文章を `10.1 Signature process <https://tools.ietf.org/html/rfc2313#section-10.1>`_ から引用します。


    10.1 Signature process

    The signature process consists of four steps: message digesting, data
    encoding, RSA encryption, and octet-string-to-bit-string conversion.

    (中略)

    10.1.3 RSA encryption

    The data D shall be encrypted with the signer's RSA private key as
    described in Section 7 to give an octet string ED, the encrypted
    data. The block type shall be 01. (See Section 8.1.)


ここで、明確に「秘密鍵で暗号化」と書いてあることがわかります。

結論を急がず、次のバージョンも確認しましょう。

RFC 2437 - PKCS #1: RSA Cryptography Specifications Version 2.0
-----------------------------------------------------------------

:公開: 1998年10月

v1.5 の5ヶ月後に公開された Version 2.0 では、説明が大きく変更されています。

`8. Signature schemes with appendix <https://tools.ietf.org/html/rfc2437#section-8>`_ より引用


   A signature scheme with appendix consists of a signature generation
   operation and a signature verification operation, where the signature
   generation operation produces a signature from a message with a
   signer's private key, and the signature verification operation
   verifies the signature on the message with the signer's corresponding
   public key.


もはや encrypt / decrypt という表現はなくなり、「メッセージと署名者の秘密鍵から署名を生成する」という表現になっているのが分かります。

- PKCS #1 はその後 Ver 2.1, 2.2 が発行されていますが、手順の記述に関しては変更がないため省略します

流れの整理
---------------

簡単にまとめると署名の生成手順の説明は以下のような変遷を辿ったと言えます。

1. 初出の論文 => （公開鍵暗号の応用で）メッセージを復号すると署名になるよ
2. PKCS #1 v1.5 => メッセージを秘密鍵で暗号化すると署名になるよ
3. PKCS #1 v2 以降 => メッセージと秘密鍵から署名ができるよ

エンジニア的な考えで言えば「最新のドキュメントが正」なので答えは出てるのですが、一応なんでこうなったのか考察してみましょう。

PKCS #1 v1.5 での変更
------------------------

なんで encrypt と表記されたかというと、おそらくアルゴリズムが暗号化・復号と署名生成・署名検証で全く区別されていなかったからだと思います。

実際にデータ通信する際のフォーマットの規定として、Object Identifier というどのアルゴリズムを使っているかを識別する項目があるのですが、 v1.5 の定義では以下の５種類が定義されています。

* pkcs-1
* rsaEncryption
* md2WithRSAEncryption
* md4WithRSAEncryption
* md5WithRSAEncryption

あれ署名は？と思いますが、RSAでは暗号化・復号・署名生成・署名検証で同じ式（アルゴリズム）が使えるので、署名でも上記のアルゴリズムを使うことになります。

そうすると「rsaEncryption で署名を生成」という表現が成り立つので、そこから「暗号化して署名を生成」につながったのではないかと考えられます。

PKCS #1 v2.0 の変更
------------------------

まず、v2.0ではプリミティブという新しい概念が導入されています。プリミティブは数学的な論理に基づく根本的な演算アルゴリズムを指します。

v2.0では以下に示すように、暗号化・復号と署名生成・署名検証で区別されています。

:RSAEP: RSA Encryption Primitive
:RSADP: RSA Decryption Primitive
:RSASP1: RSA Signature Primitive, version 1
:RSAVP1: RSA Verification Primitive, version 1

さらに、これらについての説明が `5.2 Signature and verification primitives <https://tools.ietf.org/html/rfc3447#section-5.2>`_ にあります。

::

   The main mathematical operation in each primitive is
   exponentiation, as in the encryption and decryption primitives of
   Section 5.1.  RSASP1 and RSAVP1 are the same as RSADP and RSAEP
   except for the names of their input and output arguments; they are
   distinguished as they are intended for different purposes.

::

   # 拙訳(意訳あり)
   それぞれのプリミティブ(訳注: RSASP1/RSAVP1のこと)での主な数学的な操作（変換）は累乗法であり、
   これは セクション5.1 の暗号化・復号プリミティブと同様である。
   RSASP1 および RSAVP1 は RSADP および RSAEP と入力・出力の引数の名前を除いて同様だが、
   異なる目的を対象としているためこれらは区別される。

推論ですが、なぜ新しい概念が必要になったのかというと RSA 以外の公開鍵暗号・デジタル署名が生み出され、それらを体系化する必要がでてきたのだと思われます [4]_ 。またそれらには暗号化と署名が表裏一体でなく、暗号化のみあるいは署名のみで使えるアルゴリズムも登場してきた、ということも区別して扱う一因になったのではないかと思われます。

ただし「秘密鍵で暗号化って概念的におかしいから表現変えない？」という議論が実際にあったのかは不明です。

結論
=================

「メッセージを秘密鍵で暗号化して署名を生成」は不適切。

根拠:

1. エンジニア的な考えをするなら「最新の公式ドキュメントが正義」なので現行の PKCS#1 に従い「メッセージと秘密鍵から署名ができるよ」と言えば良い。
2. 現行のPKCS #1 では同じアルゴリズムでも Encryption / Decryption / Signature Generation / Signature Verification を区別しており、署名の生成手順で昔使っていた encrypt という単語を使っていない。変更があったということは、それだけの理由があったと見るべき。

感想
=====

* 実際に調べてみると定義だけで正誤が判別できない話だった
* デジタル署名の一般的な説明をするときは

  * メッセージと秘密鍵から署名を生成する
  * 署名とメッセージを公開鍵により検証することで、次のことを保証できる。

    * 秘密鍵の所有者が作成した署名であること
    * メッセージが改ざんされていないこと

  以上に細かいこと言わなくていいんじゃないかなと思います。

本文中のリンク以外の参考
=========================

- `Why is RSA encryption version 1.0 not specified in an RFC?  - Cryptography Stack Exchange <https://crypto.stackexchange.com/questions/30515/why-is-rsa-encryption-version-1-0-not-specified-in-an-rfc>`_

.. rubric:: Footnotes

.. [1] メッセージを暗号文にしたければ署名＋暗号化をする。JWK のように署名のみでデータをやりとりすることも普通にある
.. [2] 厳密には彼らはこの論文で Diffie-Hellman (-Merkle) 鍵交換方式 と今日呼ばれる方式で、鍵配送問題の解決策を示していますが、暗号通信を送る相手ごとに交換手続きが必要であったり、認証機能を持たないため単独では使いにくいという問題がありました
.. [3] 暗号解読 (下) （サイモンシン）によるとイギリスの情報機関GCHQ の方が先に公開鍵暗号を発明していたが、情報機関なので公表していなかったらしい。本文と関係ないけどこの本面白いのでおすすめです。
.. [4] 本当はこの暗号が出てきたのが〜年で、何がしで標準化されたのが〜年でという公開鍵暗号全体の流れも調べた方が背景がわかって良いのですが、今回は見送りで..

.. update:: 2020-11-20

  `ご指摘 <https://github.com/ykrods/note/issues/3#issuecomment-726929819>`_ いただいた部分を修正（といいつつ全体リファイン）

  * `commit:ef9bb4d <https://github.com/ykrods/note/commit/ef9bb4da6c271c170433e070c366c267e8216d72>`_
