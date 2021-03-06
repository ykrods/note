.. post::
   :tags: Docker
   :category: 小ネタ
   :author: ykrods

============================================================
(小ネタ) Dockerfile の上位ディレクトリのファイルをCOPYする
============================================================

背景
=====

開発用の環境などをdockerで構築する場合、`COPY` は上位のパス ( `../` のような)を指定できない [1]_  ので、アプリのリポジトリ直下などの上位に Dockerfile を置く必要があると思っていた。

例えば Python のアプリならこんな感じ

リポジトリ構造

::

  + Dockerfile
  + requirements.txt
  + webapp.py

.. code-block :: text
  :caption: Dockerfile

  COPY . /app
  WORKDIR /app
  RUN pip install -r requirements.txt
  CMD ["python", "webapp.py"]

上の例くらい単純ならあまり気にもならないが、COPY を複数記述する必要が出てきたり、 Dockerfile が複数必要になったり... となると見通しが悪くなってくる。

が、実はビルド時に context を指定すれば Dockerfile を下位ディレクトリに置ける（ドキュメントに書いてあるが）。

やり方
======

docker-compose.yml を以下のように書く。

ディレクトリ構造

::

  * docker
    * webapp
      * Dockerfile
  * requirements.txt
  * webapp.py

.. code-block:: yaml
  :caption: docker-compose.yml

  version: '3'
  services:
    webapp:
      build:
        context: .
        dockerfile: ./docker/webapp/Dockerfile

公式
======

https://docs.docker.com/compose/compose-file/ のcontextの項

.. rubric:: Footnotes

.. [1] https://docs.docker.com/engine/reference/builder/#copy
