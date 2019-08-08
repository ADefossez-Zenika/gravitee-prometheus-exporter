import os
from prometheus_client import start_http_server, Summary, Gauge, Metric
from prometheus_client.core import GaugeMetricFamily, CounterMetricFamily, REGISTRY
import time
import random
import logging
import requests
import json
from datetime import date
from cachetools import cached, TTLCache

requests.packages.urllib3.disable_warnings()

# CACHING
cacheApiInfos = TTLCache(maxsize=100, ttl=300)
cacheResponsesCount = TTLCache(maxsize=100, ttl=10)
cacheApiCount = TTLCache(maxsize=100, ttl=300)


class CustomCollector(object):
    def __init__(self):
        pass

    @cached(cacheApiCount)  # this function is cached, for 300 secs
    def apiCounter(self):
        try:
            curl = requests.get(
                GIO_URL+"/apis/", auth=(GIO_USER, GIO_PWD), verify=False)
            if curl.status_code is not 200:
                logging.error("Something went wrong when fetching {}, got status code {}" .format(
                    GIO_URL+"/apis/", curl.status_code))
                exit(1)
        except:
            logging.error("An error Occured during Api Count")
            raise
        else:
            return len(curl.json())

    @cached(cacheApiInfos)  # this function is cached, for 300 secs
    def apiInfos(self, uuid):
        try:
            curl = requests.get(GIO_URL+"/apis/"+uuid,
                                auth=(GIO_USER, GIO_PWD), verify=False)
            if curl.status_code is not 200:
                logging.error("Something went wrong when fetching {}, got status code {}" .format(
                    GIO_URL+"/apis/"++uuid, curl.status_code))
                exit(1)
            jsonResponse = curl.json()
        except json.decoder.JSONDecodeError as err:
            logging.error("Error de-serialising JSON : {}".format(err.msg))
            raise
        else:
            return jsonResponse

    @cached(cacheResponsesCount)  # this function is cached, for 10 secs
    def responsesCount(self):
        postField = json.dumps({
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
        headers = {"Content-Type": "application/json"}
        ES_INDEX = self.calculateIndex(
            os.getenv("GPE_ES_INDEX", "gravitee")+"-%Y.%m.%d")

        r = requests.get(ES_URL+"/"+ES_INDEX+"/_search", data=postField,
                         headers=headers, auth=(ES_USER, ES_PWD), verify=False)
        if r.status_code is not 200:
            logging.warning("Something went wrong when fetching {}, got status code {}" .format(
                ES_URL+"/"+ES_INDEX+"/_search", r.status_code))
            # If Elasticsearch is not available, or the index is not available (it happens on low traffic infrastructures) you should not exit, just alert and continue.
            return False
        result = r.json()
        if result["hits"]["total"] is not None and result["hits"]["total"] > 0:
            return result

    def collect(self):

        # Add Total number of Apis
        count = self.apiCounter()
        yield GaugeMetricFamily('api_count', 'Number of APIS in Gravitee.io', value=count)

        c = GaugeMetricFamily('gio_http_call', 'Api calls', labels=(
            'api_id', 'api_name', 'description', 'owner', 'uri', 'reponseCode'))
        responsesCodes = self.responsesCount()
        if (responsesCodes):
            for i in responsesCodes["aggregations"]["request"]["api"]["buckets"]:
                for j in i["status"]["buckets"]:
                    apiInfo = self.apiInfos(i["key"])
                    c.add_metric((i["key"], apiInfo['name'], apiInfo['description'], apiInfo['owner']
                                ["displayName"], apiInfo['context_path'], str(j["key"])), j["doc_count"])
            yield c

    def calculateIndex(self, pattern):
        today = date.today()
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
        global GIO_URL, GIO_USER, GIO_PWD, PORT, ES_URL, ES_PWD, ES_USER
        GIO_URL = os.getenv(
            "GPE_GIO_URL", "http://localhost:8005/management").rstrip("/")
        GIO_USER = os.getenv("GPE_GIO_USER", "admin")
        GIO_PWD = os.getenv("GPE_GIO_PWD", "admin")
        LOG_LEVEL = str(os.getenv("GPE_LOG_LEVEL", "info")
                        ).upper()  # get log level

        # test if provided log level exists in logging module
        if LOG_LEVEL not in ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG", "NOTSET"]:
            raise ValueError('Invalid log level: %s' % LOG_LEVEL)
        logging.basicConfig(
            level=LOG_LEVEL, format='%(asctime)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

        PORT = int(os.getenv("GPE_PORT", 8888))
        ES_URL = os.getenv("GPE_ES_URL", "http://localhost:9200")
        ES_USER = os.getenv("GPE_ES_USER", None)
        ES_PWD = os.getenv("GPE_ES_PWD", None)

        start_http_server(PORT)
        REGISTRY.register(CustomCollector())
        logging.info("Polling Gravitee.IO {} and ElasticSearch {} Serving at port: {}".format(
            GIO_URL, ES_URL, PORT))

        while "it wont stop":
            time.sleep(1)

    except KeyboardInterrupt:
        logging.warning(" Interrupted")
        exit(0)
    except ConnectionRefusedError:
        logging.error("Connection Refused")
        exit(1)
    except requests.exceptions.ConnectionError as e:
        logging.error("Connection error! \n Error : {}".format(e))


if __name__ == "__main__":

    main()
