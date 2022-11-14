#!/usr/bin/env python

import asyncio
import websockets
import pandas as pd
import uuid


def createFile(name,lines):
    try:
        df = pd.read_json(lines)
        df.to_csv(name)
    except Exception as e:
        print(e)

# create transformation for each connection
async def get_stream(websocket, path):
    data = await websocket.recv()
    print(data)
    result = "["
    count = 0
    unique_filename = str(uuid.uuid4())
    try:
        while True:
            contents = await websocket.recv()
            #contents = str(contents, 'utf-8')
            #print(result)
            if contents == "end":
                print("the number of record is "+str(count))
                result = result[:-1]
                result += "]"
                createFile(unique_filename+".csv",result) #change the file name
                # the name of file should be decided by the user
                reply = f"The transform ends successfully"
                await websocket.send(reply)
            result += contents
            result += ","
            count += 1
    except:
        print("Client disconnected")   

 
 
 
start_server = websockets.serve(get_stream, "localhost", 8000)
 
 
 
asyncio.get_event_loop().run_until_complete(start_server)
 
asyncio.get_event_loop().run_forever()