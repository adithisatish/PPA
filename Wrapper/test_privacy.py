import os
import sys
import time
import display
import transform	
import psycopg2 as pg
import pandas as pd
import pandas.io.sql as psql

def privacy(db_name,query,mode):
    try:
        # Setup Connections
        connection = pg.connect(user = "postgres",password = "getup",host = "127.0.0.1",port = "5432",database = db_name)
        cursor = connection.cursor()
        #query= query.lower()
        
        dtype=transform.find(query)
        
        if mode == "normal" or mode == "":# Normal Query 
            start_time = time.time()
            cursor.execute(query)
            end_time = time.time()

            record = cursor.fetchone()
            normal_time = (end_time-start_time)*1000
            return [record[0],normal_time]

        elif mode == 'bounded':# Differential Privacy with bounds
            tquery=transform.bounded(query,dtype)
            start_time = time.time()
            cursor.execute(tquery)
            end_time = time.time()

            record = cursor.fetchone()
            bounded_time = (end_time-start_time)*1000
            return [record[0], bounded_time]
        
        elif mode == "fastbounded":# Differential Privacy with fastbounds
            tquery=transform.fastbounded(query,dtype)
            start_time = time.time()
            cursor.execute(tquery)
            end_time = time.time()

            record = cursor.fetchone()
            fastbounded_time = (end_time-start_time)*1000
            return [record[0],fastbounded_time]

        elif mode=='winsorized':# Differential Privacy with winsorized bounds
            tquery=transform.winsorized(query,dtype)
            start_time = time.time()
            cursor.execute(tquery)
            end_time = time.time()

            record = cursor.fetchone()
            winsorized_time = (end_time-start_time)*1000
            return [record[0],winsorized_time]
        
        #return [normal_time,bounded_time,fastbounded_time,winsorized_time]


    except (Exception, psycopg2.Error) as error :
        print ("Error while connecting to PostgreSQL", error)
    finally:
        #Closing Connection.
            if(connection):
                cursor.close()
                connection.close()


def isstr(s):
    try:
        s.lower()
        return True
    except:
        return False

def exec_query(query,mode):
    time = []
    result = []
    for i in range(10):
        val = privacy("uber",query,mode)
        time.append(val[1])
        result.append(val[0])
    
    avg_time = sum(time)/10
    if None in result:
        avg_result = None
    elif isstr(result[0]):
        if mode!="normal":
            avg_result = None
        else:
            avg_result = result[0]
    else:
        avg_result = sum(result)/10
    
    return [avg_result,avg_time]


cwd = os.getcwd().split("/") #change to "/" in Linux
del(cwd[-1])
file_path = "/".join(cwd) + "/Queries/" + sys.argv[1] + ".txt"

file = open(file_path,'r')
queries = file.readlines()

data = {"query" : [],"query_id":[], "result":[],"exec_time":[],"mode":[]}

'''norm = {"query":[],"result":[],"exec_time":[]}
bound =  {"query":[],"result":[],"exec_time":[]}
fbnded =  {"query":[],"result":[],"exec_time":[]}
win =  {"query":[],"result":[],"exec_time":[]}'''
count = 0
for i in queries:
    data["query"].append(i)
    data["query_id"].append(count)
    normal = exec_query(i,"normal")
    data["result"].append(normal[0])
    data["exec_time"].append(normal[1])
    data["mode"].append("normal")

    data["query"].append(i)
    data["query_id"].append(count)
    bounded = exec_query(i,"bounded")
    data["result"].append(bounded[0])
    data["exec_time"].append(bounded[1])
    data["mode"].append("bounded")

    data["query"].append(i)
    data["query_id"].append(count)
    fastbounded = exec_query(i,"fastbounded")
    data["result"].append(fastbounded[0])
    data["exec_time"].append(fastbounded[1])
    data["mode"].append("fastbounded")

    data["query"].append(i)
    data["query_id"].append(count)
    winsorized = exec_query(i,"winsorized")
    data["result"].append(winsorized[0])
    data["exec_time"].append(winsorized[1])
    data["mode"].append("winsorized")

    count+=1

df = pd.DataFrame(data)
print("\n\nDataframe:\n\n",df.head(10))

df.to_csv(sys.argv[1] + ".csv")

'''
print("\nNORMAL\n",df[df.mode=="normal",:-1].head(10))
print("\n-------------------------------------------------\n")


print("\nBOUNDED\n",df[df.mode=="bounded",:-1].head(10))
print("\n-------------------------------------------------\n")


print("\nFAST BOUNDED\n",df[df.mode=="fastbounded",:-1].head(10))
print("\n-------------------------------------------------\n")


print("\nWIDENED WINSORIZED\n",df[df.mode=="winsorized",:-1].head(10))
print("\n-------------------------------------------------\n")
'''
file.close()
