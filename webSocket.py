#!/usr/bin/env python

import asyncio
 
import websockets
 

def createFile(name,lines):
    try:
        fp = open(name, 'w')
        for line in lines:
            fp.write(str(line, 'utf-8'))
        fp.close()
    except Exception as e:
        print(e)

# create transformation for each connection
async def get_stream(websocket, path):
    data = await websocket.recv()
    print(data)
    result = []
    try:
        while True:
            contents = await websocket.recv()
            
            print(str(contents, 'utf-8'))
            if contents == bytes("end",'utf-8'):
                createFile('example.xml',result) 
                # the name of file should be decided by the user
                reply = f"The transform ends successfully"
                await websocket.send(reply)
            result.append(contents)
    except:
        print("Client disconnected")   

 
 
 
start_server = websockets.serve(get_stream, "localhost", 8000)
 
 
 
asyncio.get_event_loop().run_until_complete(start_server)
 
asyncio.get_event_loop().run_forever()