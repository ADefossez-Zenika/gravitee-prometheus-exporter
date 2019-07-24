# Gravitee.IO Prometheus exporter

An exporter for Prometheus based on the logs backend (ElasticSearch) of Gravitee.io.

## Environment variables

- GIO_URL : Gravitee.IO management Url (default : <http://localhost:8005/management> )
- GIO_USR Gravitee basic auth Username (default : admin)
- GIO_PWD Gravitee basic auth Password (default : admin)
- ES_URL Elasticsearch Url (default : <http://localhost:9200)>
- ES_USER ElasticSearch basic auth user (default : 'None')
- ES_PWD Elasticsearch basic auth password (default : 'None')
- INDEX Index Pattern for Gravitee index. Must contains %Y, %m, %d. (default : gravitee-%Y.%m.%d)
- PORT Port to listen on. (default : 8888)

## Metrics returned

    # HELP api_count Number of APIS in Gravitee.io
    # TYPE api_count gauge
    api_count 2.0
    # HELP gio_http_call Api calls
    # TYPE gio_http_call gauge
    gio_http_call{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",reponseCode="200",uri="/v1/customers"} 166.0
    gio_http_call{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",reponseCode="404",uri="/v1/customers"} 3.0

## Internals

This application scrape Elasticsearch to retrieve gravitee logs. It consolidate datas by calling Gravitee Management API.

### Cache

To avoid too much trafic load on elasticsearch & gravitee, a little cache layer is added

- Api informations is available for 300 seconds (api name, owner name, description etc)
- Logs Count is available for 10 seconds
- Api count is available for 300 seconds
