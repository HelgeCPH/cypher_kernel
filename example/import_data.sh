#!/usr/bin/env bash
echo "*************************************************"
echo "Starting a Neo4j container"
echo "*************************************************"
docker run \
    -d --name neo4j \
    --rm \
    --publish=7474:7474 \
    --publish=7687:7687 \
    --volume=$(pwd):/import \
    --volume=$(pwd)/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/class \
    --env=NEO4J_dbms_memory_pagecache_size=6G \
    --env=NEO4J_dbms_memory_heap_max__size=10G \
    --env=NEO4J_dbms_security_procedures_unrestricted=apoc.\\\* \
    neo4j

echo "*************************************************"
echo "Downloading dataset"
echo "*************************************************"
mkdir csv_paradise_papers
pushd csv_paradise_papers
wget https://offshoreleaks-data.icij.org/offshoreleaks/csv/csv_paradise_papers.2018-02-14.zip
unzip csv_paradise_papers.2018-02-14.zip
popd

echo "*************************************************"
echo "Downloading APOC"
echo "*************************************************"
mkdir plugins
pushd plugins
wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.3.0.1/apoc-3.3.0.1-all.jar
popd

echo "*************************************************"
echo "Fixing CSV header"
echo "*************************************************"
sed -i -E "1s/START_ID/\:START_ID/" csv_paradise_papers/paradise_papers.edges.csv
sed -i -E "1s/END_ID/\:END_ID/" csv_paradise_papers/paradise_papers.edges.csv
sed -i -E "1s/TYPE/\:TYPE/" csv_paradise_papers/paradise_papers.edges.csv

echo "*************************************************"
echo "Importing the data"
echo "*************************************************"
docker exec neo4j sh -c 'rm -r data/databases/graph.db; \
mkdir data/databases/graph.db; \
neo4j-admin import \
    --nodes /import/csv_paradise_papers/paradise_papers.nodes.address.csv \
    --nodes /import/csv_paradise_papers/paradise_papers.nodes.entity.csv \
    --nodes /import/csv_paradise_papers/paradise_papers.nodes.intermediary.csv \
    --nodes /import/csv_paradise_papers/paradise_papers.nodes.officer.csv \
    --nodes /import/csv_paradise_papers/paradise_papers.nodes.other.csv \
    --relationships /import/csv_paradise_papers/paradise_papers.edges.csv \
    --quote "\"" \
    --ignore-missing-nodes=true \
    --ignore-duplicate-nodes=true \
    --multiline-fields=true \
    --id-type=INTEGER'

echo "*************************************************"
echo "...And now, there seems to be nothing..."
echo "*************************************************"
docker exec -it neo4j sh -c "echo 'MATCH (n) RETURN count(n);' | cypher-shell -u neo4j -p class"

docker exec -it neo4j sh -c "echo 'CALL apoc.meta.graph();' | cypher-shell -u neo4j -p class" 

