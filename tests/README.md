# TAKE CARE!!! WIPES YOUR NEO4J DATABASE COMPLETELY!!!

Running this test suite is meant for development. It contains Cypher queries such as `MATCH (n) DETACH DELETE n;` to clean the database before running the tests. Otherwise, I cannot say anything about expected query results.
