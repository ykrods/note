.. post:: 2019-09-25
  :tags: Chrome tcp
  :category: TCP

===========================================================================
Chrome から Python3 の HTTPServer へリクエストすると応答が返ってこない件
===========================================================================

ちょっとした検証のための単純なサーバアプリを書いていたら、表題の件に出くわしました。この記事は当問題の調査記録です。

現象
======

Python3 の http.server.HTTPServer でサーバを起動し、Chrome でアクセスするとレスポンスが返ってこないまま待ち状態になる

- DeveTools > Network パネル > Timing タブ で確認すると、リクエストが Stalled のまま止まっています

  - Stalled はより優先度の高いリクエストがあるなどの理由により、リクエストの送信が止められている状態を指します [1]_

- Firefox では普通に応答できてるのでネットワークの疎通に問題は無いように見えます

再現手順
---------

1. 以下のスクリプトを Python3 が動く環境に配置

   .. literalinclude:: myserver.py
     :caption: myserver.py
     :language: python

2. サーバを起動

   ::

     $ python myserver.py

3. Chrome で http://localhost:18000 にアクセス

バージョン情報
----------------

:Python: 3.7.1
:Chrome: 77.0.3865.90

なんで止まるのか
====================

結論からいくと、HTTPServer は多重接続を考慮していないシンプルな実装になっているが、Chrome は多重接続で通信しようとするので不具合が起きる、という事のようです。

tcpdump を使ってパケットを確認してみたところ、Chrome は以下の挙動をしていました。

1. メインの(サブリソースでない) リクエストを送る際、まずTCPコネクションを2つ貼る
2. 1番目のコネクションは確立した後すぐには利用せず、2番目のコネクションを使ってメインのリクエストを行う
3. メインのリクエストの応答が完了したのち、1番目に貼ったコネクションで favicon の取得を行う

Chrome が1番目のコネクションを先に使ってくれればおそらく HTTPServer でも問題ないのですが、実際は1番目のコネクションは放置状態になります。HTTPServer は先に貼られたコネクションからデータが送られてくるのをひたすら待ち続けるため、結果的にデッドロックのような状況になります。

調査ログ
----------

実際に ``$ tcpdump -X -s0 port 18000`` した結果を要約すると以下になります。生データは `こちら <https://github.com/ykrods/note/tree/master/src/posts/2019/09/25>`_ にあります。

1. HTTPServer に対して Chrome からアクセス

   ::

     # 1番目のコネクションの3ウェイハンドシェイク
     1. Chrome (port 54866) -> Server               :SYN (seq=4289580012)
     2. Server              -> Chrome (port 54866)  :SYN (seq=470751280, ack=4289580013)
     3. Chrome (port 54866) -> Server               :ACK (ack=1)

     # 2番目のコネクションの3ウェイハンドシェイク
     4. Chrome (port 54868) -> Server               :SYN (seq=4227204900)
     5. Server              -> Chrome (port 54868)  :SYN (seq=91222027, ack=4227204901)
     6. Chrome (port 54868) -> Server               :ACK (ack=1)

     # `GET /` のリクエストヘッダ送信
     7. Chrome (port 54868) -> Server               :PUSH (seq=1:547, ack=1)
     # 以降通信停止

2. HTTPServer に対して Firefox からアクセス

   ::

     # 3ウェイハンドシェイク
     1.  Firefox (port 54870) -> Server                :SYN
     2.  Server               -> Firefox (port 54870)  :SYN
     3.  Firefox (port 54870) -> Server                :ACK

     #  `GET /` のリクエストヘッダ送信
     4.  Firefox (port 54870) -> Server                :PUSH (seq=1:365, ack=1)
     5.  Server               -> Firefox (port 54870)  :ACK (ack=365)

     #  `GET /` のレスポンスヘッダ送信
     6.  Server               -> Firefox (port 54870)  :PUSH (seq=1:136, ack=365)
     7.  Firefox (port 54870) -> Server                :ACK (ack=137)

     #  `GET /` のレスポンスボディ送信
     8.  Server               -> Firefox (port 54870)  :PUSH (seq=136:146, ack=365)
     9.  Firefox (port 54870) -> Server                :ACK (ack=146)

     # 終了シークエンス
     10. Server               -> Firefox (port 54870)  :FIN (seq=146, ack=365)
     11. Firefox (port 54870) -> Server                :FIN (seq=365, ack=147)
     12. Server               -> Firefox (port 54870)  :ACK (ack=366)

3. 1.の実行後の状態から、Chrome 側からリクエストを中断

   ::

     # 1.の7ステップ目の続き
     8. Chrome (port 54868) -> Server               :FIN (seq=547, ack=1)
     9. Server              -> Chrome (port 54868)  :ACK (ack=548)

   - 1番目のコネクションは閉じられずに残っているのでこの状態でFirefoxでリクエストしても応答不能になります

4. 1.の実行後の状態から、Chrome 側からコネクションの切断要求

   私は今回初めて知りましたが、 Chrome で ``chrome://net-internals/#sockets`` を開いて Close idle sockets ボタンを押すとコネクションを閉じる事ができます [2]_

   ::

     # 1.の7ステップ目までと同様の流れだが、クライアントの port は 54942 と 54944 に変わっている

     # 1番目のコネクションの終了
     8.  Chrome (port 54942) -> Server               :FIN (seq=1, ack=1)
     9.  Server              -> Chrome (port 54942)  :FIN (seq=1, ack=2)
     10. Chrome (port 54942) -> Server               :ACK (ack=2)

     #. `GET /` へのレスポンスヘッダ
     11. Server              -> Chrome (port 54944)  :PUSH (seq=1:136, ack=530)
     12. Chrome (port 54944) -> Server               :ACK (ack=136)

     #. `GET /` へのレスポンスボディ
     13. Server              -> Chrome (port 54944)  :PUSH (seq=136:146, ack=530)
     14. Chrome (port 54944) -> Server               :ACK (ack=146)

     #. 2番目のコネクションの終了シークエンス
     15. Server              -> Chrome (port 54944)  :FIN (seq=146, ack=530)
     16. Chrome (port 54944) -> Server               :FIN (seq=530, ack=147)
     17. Server              -> Chrome (port 54944)  :ACK (ack=531)

     #. 再度 3ウェイハンドシェイクが始まり、 `GET./favicon.ico` の応答が行われる
     #. (通常の通信内容なので省略)

5. ``SERVER_CLASS=ThreadingHTTPServer`` に変更して、 Chrome からアクセス

   ::

     # 1番目の3ウェイハンドシェイク
     1.  Chrome (port 54908) -> Server              :SYN (seq=1534071394)
     2.  Server              -> Chrome (port 54908) :SYN (seq=1260582444, ack=1534071395)
     3.  Chrome (port 54908) -> Server              :ACK (ack=1)

     # 2番目のコネクションの3ウェイハンドシェイク
     4.  Chrome (port 54910) -> Server              :SYN (seq=314505008)
     5.  Server              -> Chrome (port 54908) :SYN (seq=4236869432, ack=314505009)
     6.  Chrome (port 54910) -> Server              :ACK (ack=1)

     #  `GET /` のリクエストヘッダ送信
     7.  Chrome (port 54910) -> Server              :PUSH (seq=1:547, ack=1)
     8.  Server              -> Chrome (port 54910) :ACK (ack=547)

     # `GET /` のレスポンスヘッダ送信
     9.  Server              -> Chrome (port 54910) :PUSH (seq=1:145, ack=547)
     10. Chrome (port 54910) -> Server              :ACK (ack=145)

     # `GET /` のレスポンスボディ送信
     14. Server              -> Chrome (port 54910) :PUSH (seq=145:155, ack=547)
     15. Chrome (port 54908) -> Server              :ACK (ack=155)

     # 2番目のコネクションの終了シークエンス
     16. Server              -> Chrome (port 54910) :FIN (seq=155, ack=547)
     17. Chrome (port 54910) -> Server              :FIN (seq=547, ack=156)
     18. Server              -> Chrome (port 54910) :ACK (ack=548)

     # `GET /favicon.ico` のリクエストヘッダ送信
     19. Chrome (port 54908) -> Server              :PUSH (seq=1:469, ack=1)
     20. Server              -> Chrome (port 54908) :ACK (ack=469)

     # `GET /favicon.ico` のレスポンスヘッダ送信
     21. Server              -> Chrome (port 54908) :PUSH (seq=1:160, ack=469)
     22. Chrome (port 54908) -> Server              :ACK (ack=160)

     # `GET /favicon.ico` のレスポンスボディ送信
     23. Server              -> Chrome (port 54908) :PUSH (seq=160:358, ack=469)
     24. Chrome (port 54908) -> Server              :ACK (ack=358)

     # 1番目のコネクションの終了シークエンス
     25. Server              -> Chrome (port 54908) :FIN (seq=358, ack=469)
     26. Chrome (port 54908) -> Server              :FIN (seq=469, ack=359)
     27. Server              -> Chrome (port 54908) :ACK (ack=470)


内容をまとめると上述した通りになります。1個目のコネクションが favicon の取得に使われる、というのは条件によるのかもしれませんがこの辺を解説しているドキュメントが見つかりませんでした。

問題への対応
==================

対応方法はいくつかあります

1. RequestHandler.timeout を設定する

   - これにより1番目のコネクションがタイムアウトになり、メインのリクエストが終わった後に Chrome が再度 favicon を取得するためのコネクションを貼りにくるので、うまくいきます

   .. code-block:: diff

      class RequestHandler(BaseHTTPRequestHandler):
      +    timeout = 0.1

2. ThreadingHTTPServer を使う

   - すでに調査でもでてきてますが、ThreadingHTTPServer であれば複数のリクエストを同時に受けられるので問題なく動きます

3. (おまけ) リバースプロキシを使う

   - nginx や httpモードの HAProxy を使ってリクエストヘッダーが送られてきてからアプリケーションに流すようにすれば多分いけるんじゃないかと思いますが、検証用でそこまでするのも何か違う気がするので未検証です。

まぁ本番で使うこともないでしょうし1,2どちらでも問題ないかと

(補足) なんで HTTPServer を使ったのか
----------------------------------------

- ``python -m http.server`` では ThreadingHTTPServer を使っている([3]_) ので Python で(サードパーティのフレームワークを使わずに)ちょっとしたHTTPサーバを作る場合はThreadingHTTPServer が順当な選択になるかと思います。
- ただ、 ThreadningHTTPServer だと print で標準出力した結果が他のリクエストの出力と混ざってよみづらくなる事があるので、検証目的ではシーケンシャルに一個一個リクエストを処理するアプリを書きたかったのでした。

余談
=====================

- TCPの知識が乏しかったので最初アプリ側で頑張ってprintデバッグとかしててだいぶ時間を無駄にしたが tcpdump 使えば一瞬だった。 tcpdump便利。
- https://bugs.python.org/issue31639 で Chrome で問題出てたので ThreadingHTTPServer を使うようにした模様。

.. rubric:: Footnotes

.. [1] `Network Analysis Reference  |  Tools for Web Developers <https://developers.google.com/web/tools/chrome-devtools/network/reference?hl=j#timing-explanation>`_
.. [2] `Force Chrome to close/re-open all TCP/TLS connections when profiling with the Network Panel - Stack Overflow <https://stackoverflow.com/questions/37170812/force-chrome-to-close-re-open-all-tcp-tls-connections-when-profiling-with-the-ne>`_
.. [3] この辺 https://github.com/python/cpython/blob/3.7/Lib/http/server.py#L1219
