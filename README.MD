# Gravitee.IO Prometheus exporter

An exporter for Prometheus based on the logs backend (ElasticSearch) of Gravitee.io.

## Environment variables

- GPE_GIO_URL : Gravitee.IO management Url (default : <http://localhost:8005/management> )
- GPE_GIO_USR Gravitee basic auth Username (default : admin)
- GPE_GIO_PWD Gravitee basic auth Password (default : admin)
- GPE_ES_URL Elasticsearch Url (default : <http://localhost:9200)>)
- GPE_ES_USER ElasticSearch basic auth user (default : 'None')
- GPE_ES_PWD Elasticsearch basic auth password (default : 'None')
- GPE_ES_INDEX Index Pattern for Gravitee index. Must contains %Y, %m, %d. (default : gravitee-%Y.%m.%d)
- GPE_PORT Port to listen on. (default : 8888)
- LOG_LEVEL (ERROR, WARNING, INFO, DEBUG)
  
## Metrics returned

    # HELP api_count Number of APIS in Gravitee.io
    # TYPE api_count gauge
    api_count 2.0
    # HELP gio_http_call Api calls
    # TYPE gio_http_call gauge
    gio_http_call{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCode="200",uri="/v1/customers"} 166.0
    gio_http_call{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCode="201",uri="/v1/customers"} 10.0
    gio_http_call{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCode="404",uri="/v1/customers"} 3.0
    # TYPE gio_http_call_familly gauge
    gio_http_call_familly{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCodeFamily="1XX",uri="/v1/customers"} 0.0
    gio_http_call_familly{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCodeFamily="2XX",uri="/v1/customers"} 176.0
    gio_http_call_familly{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCodeFamily="3XX",uri="/v1/customers"} 0.0
    gio_http_call_familly{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCodeFamily="4XX",uri="/v1/customers"} 3.0
    gio_http_call_familly{api_id="...",api_name="V1Customer",description="About customer ressources...",owner="admin",responseCodeFamily="5XX",uri="/v1/customers"} 0.0
## Internals

This application scrape Elasticsearch to retrieve gravitee logs. It consolidate datas by calling Gravitee Management API.

### Cache

To avoid too much trafic load on elasticsearch & gravitee, a little cache layer is added

- Api informations is available for 300 seconds (api name, owner name, description etc)
- Logs Count is available for 10 seconds
- Api count is available for 300 seconds
