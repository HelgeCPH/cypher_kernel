# This code does not come from me. It is adapted from CJ Sullivan's code:
# https://gist.github.com/cj2001/30f993b482994c6908db04915115d688#file-neo4j_python_connection_class-py
# https://towardsdatascience.com/create-a-graph-database-in-neo4j-using-python-4172d40f89c4
from neo4j import GraphDatabase


class Neo4jConnection:
    def __init__(self, uri="neo4j://localhost:7687", user="neo4j", pwd="pwd"):
        self.__uri = uri
        self.__user = user
        self.__pwd = pwd
        self.__driver = None
        try:
            self.__driver = GraphDatabase.driver(self.__uri, auth=(self.__user, self.__pwd))
        except Exception as e:
            print("Failed to create the driver:", e)

    def close(self):
        if self.__driver is not None:
            self.__driver.close()

    def query(self, query, parameters=None, db=None):
        assert self.__driver is not None, "Driver not initialized!"
        session = None
        response = None
        try:
            session = self.__driver.session(database=db) if db is not None else self.__driver.session()
            response = list(session.run(query, parameters))
        except Exception as e:
            raise e
        finally:
            if session is not None:
                session.close()
        return response
