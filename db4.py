#!/usr/bin/python
import psycopg2
from config4 import config
from datetime import datetime, timezone
from psycopg2.extras import RealDictCursor

def connect():
    conn = None
    try:
        params = config()

        print('Connecting to the PostgreSQL database')
        conn = psycopg2.connect(**params)

        cur = conn.cursor()

        print('PostgreSQL database version')
        cur.execute('SELECT version()')

        db_version = cur.fetchone()
        print(db_version)

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
            print('Database connection refused.')


def execsql(sql):
    conn = None
    id = None
    try:
        params = config()
        print('Connection to the PostgreSQL database')
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            try:
                cur.execute(sql)
            except Exception as exec:
                print(exec)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return id


def insert(sql, values):
    conn = None
    id = None
    res = True
    try:
        params = config()
        print('Connection to the PostgreSQL database')
        conn = psycopg2.connect(**params)
        with conn.cursor() as cur:
            try:
                cur.execute(sql, values)
            except Exception as exec:
                res = False
                print(exec)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        res = False
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return res



def insert_with_returning(sql, values):
    conn = None
    id = None
    result = []
    try:
        params = config()
        print('Connection to the PostgreSQL database')
        conn = psycopg2.connect(**params)
        with conn.cursor() as cur:
            try:
                cur.execute(sql, values)
                row = cur.fetchone()[0]
                result.append(row)
            except Exception as exec:
                print(exec)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result    


def select(sql):
    ### query data from given table ### 
    conn = None
    result = []
    try:
        params = config()
        #print('Connection to the PostgreSQL database')
        conn = psycopg2.connect(**params, cursor_factory=RealDictCursor)

        with conn.cursor() as cur:
            try:
                cur.execute(sql)
                row = cur.fetchone()
        
                while row is not None:
                    result.append(row)
                    row = cur.fetchone()
            except Exception as exec:
                print(exec)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return result

def update(sql, values):
    ### update table with given values ###
    conn = None
    updated_rows = 0
    try:
        params = config()
        print('Connecting to the PostgreSQL database')
        conn = psycopg2.connect(**params)

        with conn.cursor() as cur:
            try:
                cur.execute(sql, values)
                updated_rows = cur.rowcount
            except Exception as exec:
                print(exec)
        conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return updated_rows


if __name__== '__main__':
    connect()
