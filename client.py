#!/usr/bin/env python

import asyncio
 
import websockets

import json
 
# create handler for each connection

async def client():
    uri = "ws://localhost:8000"
    async with websockets.connect(uri) as websocket:
        await websocket.send("start sending xml file") 
        # Allow user to enter xml file path into command line
        path = input("Enter a xml file address: ")
        with open(path, 'r') as f:
            lines = f.readlines()
        f.close()

        #lines record all line in the xml file
        for line in lines:
            line = bytes(line, 'utf-8')
            await websocket.send(line)
            await asyncio.sleep(1)
        
        await websocket.send(bytes("end",'utf-8'))
        response = await websocket.recv()
        print(response)
        
asyncio.get_event_loop().run_until_complete(client())