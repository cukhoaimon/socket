# socket

## A basic web client

Author: 

- Nguyen Hoang Phuc

- Dang An Nguyen

## How to build

- First you need to activate virtual enviroment.

```cmd
<your current directory to project>/venv/Scripts/activate
```

- Install all needed package:

```cmd
  pip install -r requirements.txt
```

- If you want to close project, deactivate it:

```cmd
<your current directory to project>/venv/Scripts/deactivate
```

## Some function

- Download single file: Download a specific file with TCP protocol, case content-length or transfer-encoding.

- Multiple request: Send many request to one connection. This function I built follow by Persistent connection with pipelining

- Multiple connection: Multiple thread to download many file

## Error handling code

323: `InterruptedError`

324: `UnicodeDecodeError`

325: Error when downloading chunked file

326: `AttributeError` when getting content length

327: Error when receiving data and the returning packet was `deviated`

329: Error when parsing url to get folders directory

330: Cannot parsing html page to get file name in a folder

331: `Exception` when downloading folder
