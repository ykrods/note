.. post:: 2019-07-01
  :tags: 要件定義, ドキュメンテーション
  :category: Software Development Process

==============================
開発の各工程における成果物
==============================

目次

.. contents::
  :local:

このドキュメントの目的
=======================

受託開発でいつ何を作るんだっけ、というのを整理する。

- WEBシステム開発を想定しています。
- 要素の洗い出しをする意図でまとめており、プロジェクトによっては不要な成果物もあると思われます。

成果物の必要性
===============

- いわゆる「顧客が本当に欲しかったもの」を作るためにはプロジェクトメンバー全員の認識共有が重要であり、認識を共有するために都度全員集めてミーティングを行うよりドキュメントにまとめた方が効率が良い。

  - 実装者の仕様の理解度はコードに反映されるので、健全な運用をしたければドキュメントを書いて共有する。

- 見積もりの精度を上げ、認識齟齬を減らすにはなんらかの形でアウトプットするのが良い
- 各工程での進捗の把握と評価に使う

  - 成果物の完成を以ってその工程が完了、とした方が進捗が分かりやすい

工程ごとの成果物
=================

.. list-table::
  :header-rows: 1
  :widths: 25, 25, 50

  - - 工程
    - 成果物
    - 成果物の内容
  - - 要求定義 / ヒアリング
    - RFP (Request For Proposal, 提案依頼書)
    - - システム導入の目的
      - 組織体制や業務の説明
      - 現状の課題
      - 依頼者のプロジェクト体制・役割
      - 委託範囲
      - 予算規模
      - 提案依頼事項
  - -
    - 提案書
    - - システムの提案
      - プロジェクトの進め方
      - ベンダーのプロジェクト体制・役割
  - - 要件定義
    - 要件定義書
    - * システム概要
      * 全体図
      * 機能一覧
      * 業務フロー図
      * 非機能要件
      * 納品対象
      * 現状分析資料
      * 用語集
  - - 見積もり
    -
    - * 見積書
      * スケジュール
      * 前提条件
  - - 外部設計
    - 機能仕様書
    - * 画面・帳票・バッチ各機能の入出力・処理内容
      * ユースケース記述
      * 画面遷移図
      * シークエンス図
      * 連携システムなどの外部資料
  - - 基本設計
    - 基本仕様書
    - * インフラ・ミドルウェア・フレームワーク選定
      * 画面レイアウト・共通機能
      * db設計（基本部分）
      * ER図
      * 用語集
      * 状態遷移図
      * システム構成図
      * ネットワーク構成図
      * アーキテクチャ
  - - 詳細設計
    - 技術仕様書
    - * 実装方針
      * モジュール・クラス設計
      * アルゴリズム・ライブラリの選定
      * ロバストネス図
  - - 実装・システム構築
    - システム
    -
  - - テスト設計
    - テスト設計書
    -
  - - テスト
    - テスト実施書
    -
  - - 検収・納品
    - 各成果物の確認
    -

要求定義 / ヒアリング
========================

顧客の要求をまとめて、システム案と進め方を提案する。

- RFP は依頼主が主体となって作成するものだが、コンサルとして作成支援する場合もある
- 個人的な経験としては、RFPおよび提案書は省略され、システム概要の様なパワーポイントの資料をいただく形が多い

  - システム概要的なものが来た場合は、RFPの記載項目と比較して足りない情報がないかを確認しておくと良いと思われる。足りない情報がある場合はそれらを文章化するところから始めた方が安全。
  - システム概要のものをそのまま作っても顧客要求が満たせないことも普通にあるので、背景にある課題がなんなのか(そのシステムで本当に課題が解決できるのか)には特に注意する

RFP (Request For Proposal, 提案依頼書)
------------------------------------------

- システム導入の目的
- 組織体制や業務の説明
- 現状の課題
- 依頼者のプロジェクト体制・役割
- 委託範囲

  - システムの一部なのか、全体なのか
  - どの工程を委託するのか
  - 環境構築も含むのか

- 予算規模
- 提案依頼事項

上記は業務システム想定だが、BtoCのシステムの場合でも項目にターゲットのユーザ層とユーザ価値を内容に加えれば良いと思われる

提案書
---------

- システムの提案

  - webシステムの場合「webでやります」で済んでしまう場合が多いと思われるが、例えば業務システムでもタブレットで業務する場合はネイティブアプリにするのか、ブラウザ上で動作させるのかなどが提案項目になる

- プロジェクトの進め方

  - 具体的には以下を決める（合意を取る）。

    - どのような工程（マイルストーン）を設けるか
    - どのような合意形成フローを取るか
    - ツール（課題管理・テキストチャット・ドキュメンテーション）
    - 定例打ち合わせ頻度
    - スケジュール管理方法(WBS など)
    - 開発環境・検証環境などの構成時期

  - どの情報が揃っているか、どのような合意が必要な事柄（課題）があるか、及び想定されるシステムの規模がどの程度かで必要な工程を判断する
  - 認識ずれが起きるリスクがそれなりにありそうな場合はプロトタイプや PoC を作る工程を挟むなど

- ベンダーのプロジェクト体制・役割

.. tip::

  提案時の役割

  - 要件定義が必要な場合、大抵業務担当者にヒアリングする人が必要なのでそれを誰がやるかは明確にする

要件定義
=========

開発スコープをFIXさせ、のちの設計と実装の工数が大きくブレないレベルの情報を揃える。

- システムの対象外についてもドキュメントか見積もりの前提条件に記載する

要件定義書
--------------

* システム概要
* 全体図

  - 1枚で全体が俯瞰できるもの
  - 内容は書く人によってまちまちな様だが、以下が入っていれば良いと思われる

    1. ユーザ（アクター）
    2. 連携する外部システム・サブシステム
    3. ストレージ(database, ストレージサーバ)

* 機能一覧

  - 詳細な画面設計などは含まれないが、その機能でできる事・できない事が判断できる程度の説明を付記する

* 業務フロー図

  - 詳細な画面操作などは含まずに対象システムに対してどの業務で何の入出力を行うかを記載する
  - システムのユーザおよび連携システムを想定しやすくなるので基本的に作った方が良いと思われる

* 非機能要件

  - 動作環境（対象ブラウザ）・性能・セキュリティ要件のほか、インフラや外部サービスに指定がある場合、それを記載する
  - バックアップ方針やプライバシー保護目的でのデータ削除方針なども確認する。この辺りはプライバシーポリシーとも関わってくる。

  - 詳細な項目は IPA の `システム構築の上流工程強化（非機能要求グレード） <https://www.ipa.go.jp/sec/softwareengineering/std/ent03-b.html>`_ が参考になる

* 納品対象

  - 何をどう納品するかを確定させる
  - 例えば運用マニュアルが納品対象に含まれる場合、マニュアルの作成工数が発生する。紙メディアを要求された場合は印刷代も必要。
  - 動作環境を作り直すということは普通にあり得るので、構築手順あるいはスクリプト類、最低でも環境のなんらかの資料は納品しておいた方が良いように思う

* 現状分析資料

  - 既存システムがある場合のそれに関する資料
  - 要求段階で作成するものな気がするが、実情としては要件定義と平行で作ることが多い

* 用語集

  - 用語の説明とドキュメントでの出現箇所、英訳を記載する
  - 表記揺れの発見や・後のコーディングでの英訳を統一するのに有用
  - 用語集は順次アップデートする（この段階では完成しない）

見積もり
==========

要件に対して工数を見積もり、納品までの計画を立て、スケジュール・金額を提示する。

- 要件定義と外部設計の間に置いたのは、要件定義までは準委任、設計以降は請負で受ける事が多いため
- 小規模なら設計前に見積もりFIXでもなんとかなるが、中〜大規模の場合は設計後際見積もりや、開発フェーズを分けて都度見積もり等した方が安全（反復型開発というやつ）

  - 少なくとも画面設計をせずに見積もりするのは、顧客の思い描いているものとイメージが乖離している可能性があり、それなりにリスクを伴う。この文章のように設計を実装フェーズに含められる（つまり設計にかかる工数が見積もり可能）のは、見積もり段階で画面のイメージがほぼできていて、「WEBでシステムを作ったら普通こうなる」というような共通の認識が顧客・ベンダー間が持てていて、かつ追加の要求もなさそうな場合。 [1]_
  - 開発フェーズを分けるのとは別の進め方として、プロトタイプを作成するというパターンもあるが、プロトタイプとして作ったものがそのまま本番に転用される流れになってしまう場合があるので少なくとも「捨てる」合意なしではオススメできない [2]_

見積書
----------

- 見積もり
- 前提条件

  - 概ね「要件にない追加機能は対象外になります」と書く。

- スケジュール

  - 開発期間・テスト期間・検収期間・納期を記載

外部設計
==========

システムの外部（ユーザあるいは連携するシステム）から見て、そのシステムがどの様に振る舞うかを説明する。

.. tip::

  上述したように外部設計は要件定義に含める場合もある。

機能仕様書
-------------

* 画面・帳票・バッチ各機能の入出力・処理内容
* ユースケース記述

  - 何かの業務を行うときに、どの画面でどのような操作を行うかをより具体的に記述する
  - 業務フロー図との照らし合わせ（できない業務がないか）やテスト設計時に利用できる

* 画面遷移図
* シークエンス図

  - 外部システムとのやりとりがある場合に有効
  - フロント - WebAPI - db でシークエンス図を書くこともあるが、単純なCRUDなどでは省略可能

* 連携システムなどの外部資料


基本設計
=========

システム全体に関わる仕様を決める。

.. tip::

  基本設計の中に外部設計が含まれるという見方もあるが、定義があるわけではないようなのでここでは分けて書く。 [3]_

基本仕様書
------------

* インフラ・ミドルウェア・フレームワーク選定

  * 例えばバッチ処理やジョブキュー・PUSH通知など必要に応じてフレームワークやインフラを選定する

* 画面レイアウト・共通機能

  * ヘッダーフッターなどの共通のレイアウト
  * ログイン・ログアウト・ユーザ権限などの共通機能

* db設計（基本部分）

  * 主要なデータ（複数の画面から参照されるようなデータ）はここで設計する

* ER図

  * 手書きはメンテナンスコストが高いのでテーブル作成後はテーブルからツールで生成した方がよい
  * この段階でdb設計したテーブルのモデルを定義してしまって、ツールでER図を生成するというやり方もよいと思われる

* 状態遷移図
* システム構成図
* ネットワーク構成図
* アーキテクチャ

  - コーディング規約や命名規則など、開発者が準拠するルール

詳細設計
=========

機能ごとの技術仕様をまとめる。

- 対外向けというより、実装者が計画的に実装を進めるために作る

  - 1タスクが最長でも5人日になるようにタスクを分割すると良いので、分割可能なように設計する

- コードレビューを行う場合、レビュワーは詳細設計のレビューも行うと良い

技術仕様書
-----------

* 実装方針
* モジュール・クラス設計
* アルゴリズム・ライブラリの選定
* ロバストネス図

  - ロバストネス分析する場合

テスト設計
=============

どのようなテストを行うか検討し、テスト仕様書を作成する

* バグがあった場合のワークフローも決める
* 機能仕様書がないとテスト設計できないので適当にモンキーテストしてなんとなく納品することになる

テスト仕様書
---------------

具体的なテスト手順を示したテストケースのまとまり

* 該当システムに対して理解のない実施者でもテストできるように記述する

まとめ
=======

開発の成果物について、軽い解説をつけて列挙しました。

それぞれのドキュメントをどう書くかという話もありますが、とりあえず計画を立てる時の抜け漏れの防止に使えたらいいなと思います。


(おまけ) 要件定義で気をつけると良い事
=========================================

- 期日になったというだけで要件定義を終わらせると、大抵の場合実質終わっていない

  - 第三者に成果物をレビューしてもらって客観的な評価してもらうのが良さそう

- 顧客にご協力頂かない限り良いシステムを作るのは不可能なので、定例のミーティングを設け、役割を決める等はやった方が良い
- タスクごとのデットラインと、過ぎた場合のリスクを前もって伝える

  - x: いついつまでに終わるように協力ください
  - o: いついつまでに終わらない場合、追加の予算が必要になります/スケジュールが変動します/アサインできない可能性があります

- 相手が忙しそうだとか単純に面倒だとかで突っつくのを躊躇っていると結果的により悪い事態になるので無心で突っついた方がいい

.. update:: 2019-10-06

  進め方について加筆 + ついでに全体を修正

.. update:: 2020-06-18

  読みやすいように再構成

.. update:: 2020-10-27

  環境抜けてたので追記

.. rubric:: Footnotes

.. [1] リプレイス案件で「既存の画面通りで〜」とかなった場合は注意が必要で、大体画面設計レベルでおかしいことがある（必要以上に複雑な場合を含む）から実装がおかしくなって開発が立ち行かなり、下手に変更を加えることができなくなり、リプレイスする必要性が生まれてくる。
.. [2] (余談) ここ数年で PoC (Proof of Concept) または MVP (Minimum Viable Product) という単語が流行っていて、スモールスタートしようという原義には大変同意できるが、 PoC/MVP と言っておきながら検証のための指標をとる計画が立っていなかったり初っ端から機能過剰であったりでなんというかアレな感がある
.. [3] 外部＝外からみた振る舞い、基本＝システムの基礎部分 という意味合いから考えると分けた方が自然という判断だが、本当に定義ないの？というのは別途確認したい。
