#!/usr/bin/env python

import asyncio
 
import websockets

import json

import pandas as pd

 
# create handler for each connection

async def client():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        await websocket.send("start sending csv file") 
        path = input("Enter a csv file address: ")
        df = pd.read_csv(path)
        data = df.to_json(orient='index')
        my_dict=json.loads(data)

        for line in my_dict.items():
            data_string = json.dumps(line[1]) #data serialized
            await websocket.send(data_string)
            #await asyncio.sleep(1)

        
        await websocket.send("end")
        response = await websocket.recv()
        print(response)
        
asyncio.get_event_loop().run_until_complete(client())