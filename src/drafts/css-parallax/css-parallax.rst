==============
css parallax
==============

ポイント
==========

* perspective を指定した要素と transform で変形する要素の間に 要素を挟む場合、transform-style を明示する

  * transform-style は親要素の値を継承しない仕様なので、明示する必要がある。 CSS Transforms Module は Editor's Draft なので最終的にどうなるかはわからない。
  * 現象としては間の要素で position 指定を変更した場合のみ、Firefox でスクロール時の再描画（アニメーション）が行われない
  * 三次元空間を共有されずに、子要素の二次元平面への変換が先に行われている？感じではないかと思うが、よくわからない。

* ``overflow: hidden scroll;`` は iOS 12 Safari にも対応するのであれば、 overflow-x, overflow-y に分けて記述する

  * 軽く検索したが、別のバグがヒットしてしまい同じような報告がみつからなかった。iOS 14 Safari では上記のように二値指定でも動く。

参考
======

* `erformant Parallaxing  |  Web  |  Google Developers <https://developers.google.com/web/updates/2016/12/performant-parallaxing>`_
* `A CSS Parallax Scroll Effect For All Modern Browsers - Orangeable <https://orangeable.com/css/parallax-scroll>`_
* `How To Create a Parallax Scrolling Effect with Pure CSS in Chrome | DigitalOcean <https://www.digitalocean.com/community/tutorials/css-pure-css-parallax>`_
