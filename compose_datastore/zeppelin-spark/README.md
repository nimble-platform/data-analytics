# Zeppelin with Spark and Data Science Tools inside the Data Analytics Stack

A `debian:jessie` based Spark and [Zeppelin](http://zeppelin.apache.org) Docker container.

This image is large and opinionated. It contains:

- [Spark 2.1.1](http://spark.apache.org/docs/2.1.1) and [Hadoop 2.7.3](http://hadoop.apache.org/docs/r2.7.3)
- [PySpark](http://spark.apache.org/docs/2.1.1/api/python) support with [Anaconda3-5](https://www.anaconda.com/distribution/)



## usage

Start the ELK stack using `docker-compose`:

```bash
cd ../zeppelin
docker-compose up --build -d
```

The flag `-d` stands for running it in background (detached mode):


Watch the logs with:

```bash
cd ../zeppelin
docker-compose logs -f
```


Zeppelin will be running at [http://localhost:8080](http://localhost:8080).



## complex usage

You can use [docker-compose](http://docs.docker.com/compose) to easily run Zeppelin in more complex configurations. See this project's `./examples` directory for examples of using Zeppelin with `docker-compose` to :

- read and write from local data files
- read and write documents in ElasticSearch

## onbuild

The Docker `onbuild` container is still a part of this project, but **there are no plans to keep it updated**. See the `onbuild` directory to view its `Dockerfile`.

To use it, create a new `Dockerfile` based on `dylanmei/zeppelin:onbuild` and supply a new, executable `install.sh` file in the same directory. It will override the base one via Docker's [ONBUILD](https://docs.docker.com/reference/builder/#onbuild) instruction.

The steps, expressed here as a script, can be as simple as:

```
#!/bin/bash
cat > ./Dockerfile <<DOCKERFILE
FROM dylanmei/zeppelin:onbuild

ENV ZEPPELIN_MEM="-Xmx1024m"
DOCKERFILE

cat > ./install.sh <<INSTALL
git pull
mvn clean package -DskipTests \
  -Pspark-1.5 \
  -Dspark.version=1.5.2 \
  -Phadoop-2.2 \
  -Dhadoop.version=2.0.0-cdh4.2.0 \
  -Pyarn
INSTALL

```



