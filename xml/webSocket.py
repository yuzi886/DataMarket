#!/usr/bin/env python

import asyncio
import websockets
from bs4 import BeautifulSoup
 

def createFile(name,lines):
    try:
        fp = open(name, 'w')
        fp.write(lines)
        fp.close()
    except Exception as e:
        print(e)

def count(lines):# count the number of record in the xml file
    try:
        line = lines.split('\n')
        row = line[2].split()
        tag = row[0].strip('>').strip('<') 
        Bs_data = BeautifulSoup(lines, "xml")
        record = Bs_data.find_all(tag)
        return len(record)
    except Exception as e:
        print(e)
    

# create transformation for each connection
async def get_stream(websocket, path):
    data = await websocket.recv()
    print(data)
    result = ""
    try:
        while True:
            contents = await websocket.recv()
            contents = str(contents, 'utf-8')
            print(contents)
            if contents == "end":
                print("the number of record is "+str(count(result)))
                createFile('example.xml',result) 
                # the name of file should be decided by the user
                reply = f"The transform ends successfully"
                await websocket.send(reply)
            result += contents
    except:
        print("Client disconnected")   

 
 
 
start_server = websockets.serve(get_stream, "localhost", 8000)
 
 
 
asyncio.get_event_loop().run_until_complete(start_server)
 
asyncio.get_event_loop().run_forever()
