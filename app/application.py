import os
from prometheus_client import start_http_server, Summary, Gauge, Metric
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import time, random
import requests
import json
from datetime import date
from cachetools import cached, TTLCache  
cacheApiInfos = TTLCache(maxsize=100, ttl=300)  
cacheResponsesCount = TTLCache(maxsize=100, ttl=10)  

class CustomCollector(object):
    def __init__(self):
        pass
    
    def api_counter(self):
            return 12

    @cached(cacheApiInfos)  # this function is cached, for 300 secs
    def apiInfos(self, uuid):
        curl=requests.get(GIO_URL+"/apis/"+uuid,auth=(GIO_USER, GIO_PWD))
        return curl.json()

    @cached(cacheResponsesCount)  # this function is cached, for 300 secs
    def responsesCount(self):
        postField= json.dumps({
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
        r = requests.get(ES_URL+"/"+INDEX+"/_search", data=postField, headers=headers, auth=(ES_USER, ES_PWD))
        result = r.json()   
        if result["hits"]["total"] is not None and result["hits"]["total"] > 0 :
            return result

    def collect(self):
        #Add Total number of Apis
        count=self.api_counter()
        yield GaugeMetricFamily('api_count', 'Number of APIS in Gravitee.io', value=count)

        c = GaugeMetricFamily('gio_http_call', 'Api calls', labels=('api_id','api_name','description','owner','uri','reponseCode'))
        responsesCodes= self.responsesCount()

        for i in responsesCodes["aggregations"]["request"]["api"]["buckets"]:
            for j in i["status"]["buckets"] :
                apiInfo=self.apiInfos(i["key"])
                #print (apiInfo['name'])
                c.add_metric((i["key"], apiInfo['name'], apiInfo['description'], apiInfo['owner']["displayName"], apiInfo['context_path'], str(j["key"])),j["doc_count"])
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
        global GIO_URL,GIO_USER,GIO_PWD, PORT, ES_URL, ES_PWD, ES_USER, INDEX 
        INDEX=calculateIndex(os.getenv("GIO_INDEX_PATTERN", "gravitee-%Y.%m.%d"))
        GIO_URL=os.getenv("GIO_URL", "http://localhost:8005/management").rstrip("/")
        GIO_USER=os.getenv("GIO_USER", "admin")
        GIO_PWD=os.getenv("GIO_PWD", "admin")

        PORT=os.getenv("PORT", 8888)
        ES_URL=os.getenv("ES_URL", "http://localhost:9200")
        ES_USER=os.getenv("ES_USER", None)
        ES_PWD=os.getenv("ES_PWD", None)

        start_http_server(PORT)
        print("Polling Gravitee.IO {} and ElasticSearch {} Serving at port: {}".format(GIO_URL, ES_URL, PORT))
        REGISTRY.register(CustomCollector())

        while "it wont stop":
            time.sleep(1)
            
    except KeyboardInterrupt:
        print(" Interrupted")
        exit(0)

if __name__ == "__main__":
    main()