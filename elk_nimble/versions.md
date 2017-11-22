# Version track:

## 01 (Working): 	

pure ELK Stack without Kafka messaging adapter

## 02 (Not Working):	

testing integration

## 03 (Not Working):	

integration is OK, but build problems due to dns (see README.md)

## 04 (Not Working):	

integration is OK, but build problems due to dns (see README.md)

## 05 (Working):	

ELK Stack with integrated Kafka messaging adapter, running

## 06 (Working):

set dependencies of ELK+Kafka Stack and use environment variables in docker-compose.yml

## 07 (Working):

Updated ELK to Version 6.0
		
## 08 (Working):

Adapter start when elasticsearch is reachable. Various compose tunings. Data directory is in home now
		
## 09 (Working):

Adapter start when elasticsearch is reachable. Various compose tunings. Data directory is in home now
		
## 10 (Working):

logstash.conf:  codec => "json_lines"
		
		




## TODOs:

* scale on cluster, elasticsearch-config and deviantony for details

* yaml security_opt. Password

* sysctl and ulimits can be set explicitely in yaml

* Wait until in kafka until logstash is running time.sleep(20)

* mount cluster storage for elasticsearch data
