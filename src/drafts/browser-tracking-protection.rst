.. post::
   :tags: Cookie, Tracking
   :category: Privacy

.. meta::
  :description: 最近のトラッキング防止事情について


=================================================
最近のブラウザのトラッキング防止の動き
=================================================

.. note::

  WIP: 一から振り返ると分量がすごいことになることに気づいたのでドラフトにする

導入
=========

* トラッキング防止の流れが色々きているらしいので、整理する


年表
======

* DNT(Do Not Track) について

  - https://www.w3.org/2011/tracking-protection/

* (memo) 最初表にしたが、時系列でまとめ直した方が良さそう

.. list-table::
  :header-rows: 1

  - - ブラウザ
    - リリースバージョン
    - 機能
    - 概要
  - - Firefox
    - 69.0 (2019/09/03)
    - `Enhanced Tracking Protection <https://support.mozilla.org/ja/kb/enhanced-tracking-protection-firefox-desktop>`_
    - `disconnect <https://disconnect.me/trackerprotection>`_ で提供されるトラッカーのリストを元に、諸々ブロック

  - - Safari
    - 11.0 (2017/09/19)
    - `ITP (Intelligent Tracking Prevention) <https://webkit.org/blog/7675/intelligent-tracking-prevention/>`_
    -

Safari
----------

- `Intelligent Tracking Prevention 1.0 <https://webkit.org/blog/7675/intelligent-tracking-prevention/>`_
- `Intelligent Tracking Prevention 1.1 <https://webkit.org/blog/8142/intelligent-tracking-prevention-1-1/>`_
- `Intelligent Tracking Prevention 2.0 <https://webkit.org/blog/8311/intelligent-tracking-prevention-2-0/>`_
- `Intelligent Tracking Prevention 2.1 <https://webkit.org/blog/8613/intelligent-tracking-prevention-2-1/>`_
- `Intelligent Tracking Prevention 2.2 <https://webkit.org/blog/8828/intelligent-tracking-prevention-2-2/>`_
- `Intelligent Tracking Prevention 2.3 <https://webkit.org/blog/9521/intelligent-tracking-prevention-2-3/>`_

Google Chrome
---------------

- DNT は設定可能だが、Cookie提供者が無視できるので、あまり効果がないらしい
- そもそもサードパーティCookieをサポートしないようにする予定らしい

  - 具体的にどういう？ SameSite=Strict を強制 or デフォルト値にする？

- https://blog.chromium.org/2020/01/building-more-private-web-path-towards.html
