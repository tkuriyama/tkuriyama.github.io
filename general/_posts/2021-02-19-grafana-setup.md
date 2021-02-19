---
layout: post
title:  "Grafana on macOS with Sqlite, Python, Postgres"
date:   2021-02-19 13:20:30 -0500
tags:   grafana python sqlite postgres loki
---

## Setup

Following the [macOS instructions](https://grafana.com/docs/grafana/latest/installation/mac/) worked out of the box with Homebrew.

`brew install grafana`

... and to start/stop/restart grafana in the background:

`brew services start grafana`

There is also a simple [getting started overview](https://grafana.com/docs/grafana/latest/getting-started/getting-started/).

## Sqlite

Fake news... the Sqlite datasource [doesn't currently work on macOS](https://github.com/fr-ser/grafana-sqlite-datasource/issues/7)!

---
layout: post
title:  "Grafana on macOS with Loki nad Promtail"
date:   2021-02-20 13:00:00 -0500
tags:   grafana loki promtail
---

I've been using Python's `logging` library in various projects, and wanted to find a way to inspect the contents regularly (e.g. looking for counts of Warning or Error codes).

Grafana seems to be a popular option for that sort of thing, with Loki providing log aggregation and Promtail serving as the agent that collects logs.

Installing and running Grafana locally on macOS turned out to be simple ([docs](https://grafana.com/docs/grafana/latest/installation/mac/)), but setting up Loki and Promtail took a bit more digging through the docs. 

## Setup Grafana

With Homebrew:

`brew install grafana`

To start / stop / restart as a background service:

`brew services start grafana`

The default local URL for Grafana is `localhost:3000`


## Setup Loki

The canonical tool for aggregating logs into Grafana seems to be Loki (along with some process to send logs to  Loki). Loki has an API that can be used by a log handler in Python's `logging` ([example](https://github.com/GreyZmeem/python-logging-loki), but for existing files, Promtail is the tool written by the Loki folks.

The [Grafana Loki](https://grafana.com/docs/loki/latest/installation/) has a bunch of options, but Homebrew seems to work just fine.

`brew install loki`

... and same as Grafana, Loki can be managed as a background process:

`brew services start loki`

... or started directly with the `--config.file` flag:

`loki --config.file=loki-local-config.yaml`

[The docs](https://grafana.com/docs/loki/latest/installation/local/) provide a version of the default local config that didn't work for me, apparnetly due to the link pointing to `master` branch instead of the latest rlease; [this version worked](https://github.com/grafana/loki/issues/3055).

Once Loki is started, it can be configured as a datasource in the Grafana GUI. It took me a while to realize that the value of `http://localhost:3100` in the URL config was just a default hint, and needed to be typed in manually.


## Setup Promtail

Promtail is the agent that collects logs and sends them to Logi for aggregation.

`brew install promtail`

Similar to Loki, Promtail needs to be started with a config file:

`promtail --config.file=config_promtail.yaml`

The [Promtail docs](https://grafana.com/docs/loki/latest/clients/promtail/configuration/) are... missing a simple tutorial? But there is a [sample config file](https://grafana.com/docs/loki/latest/clients/promtail/configuration/#example-static-config) that can be used as a starting point.

At this point, it should be possible to get some raw log data into a Grafana dashboard, using Loki as a datasource. But it's not very useful without speciying some log processing and aggregation logic.


## Log Processing



## Postgres
