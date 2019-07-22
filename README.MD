# Gravitee.IO Prometheus exporter

An exporter for Prometheus based on the logs backend (ElasticSearch) of Gravitee.io.

## Environment variables

- GIO_URL : Gravitee.IO management Url (default : http://localhost:8005/management )
- GIO_USR Gravitee basic auth Username (default : admin)
- GIO_PWD Gravitee basic auth Password (default : admin)
- ES_URL Elasticsearch Url (default : <http://localhost:9200)>
- ES_USER ElasticSearch basic auth user (default : 'None')
- ES_PWD Elasticsearch basic auth password (default : 'None')
- INDEX Index Pattern for Gravitee index. Must contains %Y, %m, %d. (default : gravitee-%Y.%m.%d)

## Internals

This application scrape Elasticsearch every time we call it. It consolidate data (such as Api name, Context-path, owner name etc.)

### Cache

To avoid too much trafic load on elasticsearch & gravitee, a little cache layer is added : 

- Api informations is available for 300 seconds (api name, owner name, description etc)
- Logs Count is available for 10 seconds
