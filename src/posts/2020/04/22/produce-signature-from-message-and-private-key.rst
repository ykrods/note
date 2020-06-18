.. post:: 2020-04-21
   :tags: RSA, Cryptography
   :category: Cryptography

.. meta::
  :description: 「RSAではメッセージを秘密鍵で暗号化して署名を生成する」は正しいのか

========================================================
メッセージと秘密鍵から署名を生成する
========================================================

「RSAではメッセージを秘密鍵で暗号化して署名を生成する」は正しいのか

状況説明
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

`RFC 4949 - Internet Security Glossary, Version 2 <https://tools.ietf.org/html/rfc4949>`_ から引用すると

::

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

他者に対する許可・不許可については直接的には書いていない様です。とはいえ、秘匿(conceal) という言葉にそのニュアンス（不許可）は含まれているとは思います。

例えばこの定義で行くと、「RSAではメッセージを秘密鍵で秘匿されたデータに変換して署名を生成する」という言い換えができるハズですが、署名が秘匿情報かというとそうではないという気がします。

はっきりしないので別の文章も見ましょう。

技術文書上の記載
==================

他の技術文章でどういう使われ方をされているかという事で、RSA関連文書を時系列順に並べました。

A Method for Obtaining DigitalSignatures and Public-Key Cryptosystems
------------------------------------------------------------------------

:著者: Ron Rivest, Adi Shamir, Leonard Adleman
:公開: 1977年
:資料: `A Method for Obtaining DigitalSignatures and Public-Key Cryptosystems <https://people.csail.mit.edu/rivest/Rsapaper.pdf>`_

RSA はこの論文の著者三名の頭文字をとって命名されたもので、この論文内ではまだ RSA という単語自体でてきていません。時代背景について触れておくと、公開鍵を使った暗号化・署名という画期的なコンセプトが誕生したのが前年1976年の Diffie, Hellman らの `New Directions in Cryptography <https://ee.stanford.edu/~hellman/publications/24.pdf>`_ で、そのコンセプトを現実的なシステムに落とし込むための鍵となる一方向関数を発見したのが、リヴェスト・シャミア・アドルマンの３人ということになります [1]_ 。

この論文内ではまだ private key という名称も使われていないのですが、encrypt/decrypt の応用で署名も実現できることが示されています。

つまり、「メッセージを秘密鍵で暗号化」と解釈はできるものの、その暗号化は目的でなく手段ということです。


RFC 2313 - PKCS #1: RSA Encryption Version 1.5
-------------------------------------------------

:公開: 1998年5月

PKCS #1 は RSA Security LLC (上述した３人により設立された会社）により作成された標準であり、Version1.5以降はRFCとして発行されています。

ちなみに Ver 1.0 - 1.3 は 1991年に作成されたらしいですが、社外秘的な文章だったようです。

Ver1.5 での注目すべき文章を `10.1.3 RSA encryption <https://tools.ietf.org/html/rfc2313#section-10.1.3>`_ から引用します。

::

  10.1.3 RSA encryption

  The data D shall be encrypted with the signer's RSA private key as
  described in Section 7 to give an octet string ED, the encrypted
  data. The block type shall be 01. (See Section 8.1.)

ここで、明確に「秘密鍵で暗号化」と書いてあることがわかります。

* （10.1 Signature process の中でのステップに 10.1.3 RSA Encryption が含まれています

結論を急がず、次のバージョンも確認しましょう。

RFC 2437 - PKCS #1: RSA Cryptography Specifications Version 2.0
-----------------------------------------------------------------

:公開: 1998年10月

v1.5 の5ヶ月後に公開された Version 2.0 では、説明が大きく変更されています。

`8.1.1 Signature generation operation <https://tools.ietf.org/html/rfc2437#section-8.1.1>`_ の Step 3 を引用します

::

   3. Apply the RSASP1 signature primitive (Section 5.2.1) to the
   private key K and the message representative m to produce an integer
   signature representative s: s = RSASP1 (K, m)

::

  # 拙訳
  整数署名表現s を生成するため、RSASP1 署名プリミティブを RSA 秘密鍵K と
  メッセージ表現m に対して適用する: s = RSASP1 (K, m)

プリミティブという新しい概念が導入されています。プリミティブは数学的な論理に基づく根本的な演算アルゴリズムを指します。

RSAのプリミティブを以下にリストアップします。

:RSAEP: RSA Encryption Primitive
:RSADP: RSA Decryption Primitive
:RSASP1: RSA Signature Primitive, version 1
:RSAVP1: RSA Verification Primitive, version 1

これらについての説明が `5.2 Signature and verification primitives <https://tools.ietf.org/html/rfc3447#section-5.2>`_ にあるのでそれも引用します。

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

Ver2.0 では encrypt と signature の手順についてアルゴリズムが同じでも区別して扱っていることがわかります。

まず、なぜ新しい概念が必要になったのかというと RSA 以外の公開鍵暗号・署名が生み出され、それらを体系化する必要がでてきたのだと思われます [2]_ 。またその際に暗号化と署名で同じアルゴリズムを使えるということがRSAの持つ特殊な性質ということが他と比較することで明らかになった、ということも区別して扱う一因になったのではないかと思われます。

ただし「秘密鍵で暗号化って概念的におかしいから表現変えない？」という議論が実際にあったのかは不明です。

- PKCS #1 はその後 Ver 2.1, 2.2 が発行されていますが、手順の記述に関しては変更がないため省略します

結論
=================

「メッセージを秘密鍵で暗号化して署名を生成」は不適切と言えそう

根拠: 現行のPKCS #1 では同じアルゴリズムでも encrypt と signature を区別しており、署名の生成手順で（昔使っていた） encrypt という単語を使っていない。

一応補足ですが、RSAは最初の公開鍵暗号であり、発表時点では間違いとは言えないと思います。発表時点で存在しない別の暗号方式がどういう性質を持っているか、あるいは自分たちの発明が今後どう標準化されていくかなど、知る由もないので。。

感想
=====

* 調べてみるとちゃんとした？経緯があるのでそこまで躍起になるものでもなかったわけですが、まぁ気になってしまったのでした
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

.. [1] 暗号解読 (下) （サイモンシン）によるとイギリスの情報機関GCHQ の方が先に公開鍵暗号を発明していたが、情報機関なので公表していなかったらしい。本文と関係ないけどこの本面白いのでおすすめです。
.. [2] 本当はこの暗号が出てきたのが〜年で、何がしで標準化されたのが〜年でという公開鍵暗号全体の流れも調べた方が背景がわかって良いのですが、今回は見送りで..
