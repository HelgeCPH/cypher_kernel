#!/usr/bin/env bash
rm -rf plugins
mkdir plugins
rm -rf import
mkdir import
echo "*************************************************"
echo "Starting a Neo4j container"
echo "*************************************************"
docker run \
    -d --name neo4j \
    --rm \
    --publish=7474:7474 \
    --publish=7687:7687 \
    --volume=$(pwd)/import:/import \
    --volume=$(pwd)/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/class \
    --env=NEO4J_dbms_memory_pagecache_size=6G \
    --env=NEO4J_dbms_memory_heap_max__size=10G \
    --env=NEO4J_dbms_security_procedures_unrestricted=apoc.\\\* \
    neo4j

echo "*************************************************"
echo "Downloading dataset"
echo "*************************************************"
cd import
mkdir csv_paradise_papers
cd csv_paradise_papers
wget https://offshoreleaks-data.icij.org/offshoreleaks/csv/csv_paradise_papers.2018-02-14.zip
unzip csv_paradise_papers.2018-02-14.zip
cd ../..

echo "*************************************************"
echo "Fixing CSV header"
echo "*************************************************"
sed -i -E '1s/.*/":START_ID",":TYPE",":END_ID","link","start_date","end_date","sourceID","valid_until"/' import/csv_paradise_papers/paradise_papers.edges.csv
for file in import/csv_paradise_papers/*.nodes.*.csv 
do
  sed -i -E '1s/node_id/node_id:ID/' $file
done

echo "*************************************************"
echo "Downloading APOC"
echo "*************************************************"
cd plugins
wget https://github.com/neo4j-contrib/neo4j-apoc-procedures/releases/download/3.3.0.1/apoc-3.3.0.1-all.jar
cd ..

echo "*************************************************"
echo "Importing the data"
echo "*************************************************"
docker exec neo4j sh -c 'neo4j stop'
docker exec neo4j sh -c 'rm -rf data/databases/graph.db'
docker exec neo4j sh -c 'neo4j-admin import \
    --nodes:Address /import/csv_paradise_papers/paradise_papers.nodes.address.csv \
    --nodes:Entity /import/csv_paradise_papers/paradise_papers.nodes.entity.csv \
    --nodes:Intermediary /import/csv_paradise_papers/paradise_papers.nodes.intermediary.csv \
    --nodes:Officer /import/csv_paradise_papers/paradise_papers.nodes.officer.csv \
    --nodes:Other /import/csv_paradise_papers/paradise_papers.nodes.other.csv \
    --relationships /import/csv_paradise_papers/paradise_papers.edges.csv \
    --quote "\"" \
    --ignore-missing-nodes=true \
    --ignore-duplicate-nodes=true \
    --multiline-fields=true \
    --id-type=INTEGER'

docker restart neo4j

sleep 5
echo "*************************************************"
echo "...And now, there seems to be nothing..."
echo "*************************************************"
docker exec -it neo4j sh -c "echo 'MATCH (n) RETURN count(n);' | cypher-shell -u neo4j -p class"

docker exec -it neo4j sh -c "echo 'CALL apoc.meta.graph();' | cypher-shell -u neo4j -p class" 
