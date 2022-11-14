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
        df = pd.read_csv(path,encoding = 'ISO-8859-1')
        #data = df.to_json(orient='index')
        #if use column to transfer,it will be quick.
        data = df.to_json(orient='index')
        my_dict=json.loads(data)

        """with open(path[0][0], 'r') as csv_file:
                                reader_obj = csv.reader(csv_file)  ##use the csv may increase the speed, but just for row reading
                                for row in reader_obj:
                                    print(row)"""

        for line in my_dict.items():
            data_string = json.dumps(line[1]) #data serialized
            await websocket.send(data_string)
            #await asyncio.sleep(1)
            await asyncio.sleep(0)

        
        await websocket.send("end")
        response = await websocket.recv()
        print(response)
        
asyncio.get_event_loop().run_until_complete(client())