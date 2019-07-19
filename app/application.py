import os
from prometheus_client import start_http_server, Summary, Gauge
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import time, random
import requests
import json
from datetime import date


COLLECTION_TIME = Summary('gio_collector_collect_seconds', 'Time spent to collect metrics from Gravitee.io') 
    
class CustomCollector(object):
    
    def api_counter(self):
            return 12
    def apis(self):
        curl=requests.get(GIO+"/apis",auth=('admin', 'admin'))
        #print(curl.json())
        return curl.json()

    def responsesCount(self):
        postField=   json.dumps({
        "size": 0,
        "query": {
            "match_all": {
            
            }
        },
        "aggs": {
            "request": {
            "filter": {
                "term": {
                "_type": "request"
                }
            },
            "aggs": {
                "api": {
                "terms": {
                    "field": "api",
                    "size": 500
                },
                "aggs": {
                    "status": {
                    "terms": {
                        "field": "status",
                        "size": 500
                    }
                    }
                }
                }
            }
            }
        }
        })
        headers={"Content-Type": "application/json"}
        r = requests.get(ES+"/"+INDEX+"/_search", data=postField, headers=headers)
        result = r.json()   
        
        if result["hits"]["total"] is not None and result["hits"]["total"] > 0 :
            return result

    @COLLECTION_TIME.time()
    def collect(self):
        #Add Total number of Apis
        count=self.api_counter()
        yield GaugeMetricFamily('api_count', 'Number of APIS in Gravitee.io', value=count)

        c = Gauge('gio_http_call', 'Api calls', ('api_id','api_name','owner','uri','reponseCode'))
        responsesCodes= self.responsesCount()
        #d = Gauge('data_objects', 'Number of objects')

        for i in responsesCodes["aggregations"]["request"]["api"]["buckets"]:
                print (i["key"])
                print (i["status"]["buckets"][0]["key"])
                print (i["status"]["buckets"][0]["doc_count"])
                c.labels(i["key"], "toto", "Jean Titi", "/tarace", i["status"]["buckets"][0]["key"]).set(i["status"]["buckets"][0]["doc_count"])
        yield c

def calculateIndex(pattern):
    today=date.today()
    mapping = [ 
        ("%Y", today.strftime("%Y")), 
        ("%m", today.strftime("%m")),
        ("%d", today.strftime("%d")) 
        ]
    for k, v in mapping:
        pattern = pattern.replace(k, v)
    return pattern

def main():
    try:
        global GIO, PORT, ES, INDEX 
        INDEX=calculateIndex(os.getenv("GIO_INDEX_PATTERN", "gravitee-%Y.%m.%d"))
        GIO=os.getenv("GIO_URL", "http://localhost:8005/management").rstrip("/")
        PORT=os.getenv("PORT", 8888)
        ES=os.getenv("ES_URL", "http://localhost:9200")
#        REGISTRY.register(CustomCollector())
        cc = CustomCollector()
        cc.collect()
        start_http_server(PORT)
        print("Polling Gravitee.IO {} and ElasticSearch {} Serving at port: {}".format(GIO, ES, PORT))
        while "it wont stop":
            time.sleep(1)
    except KeyboardInterrupt:
        print(" Interrupted")
        exit(0)


if __name__ == "__main__":
    main()