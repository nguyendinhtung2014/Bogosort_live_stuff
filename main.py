from pyscript import document # pyright: ignore[reportMissingImports]
from pyscript import WebSocket as websockets # pyright: ignore[reportMissingImports]
element=document.querySelector("#output")
import asyncio
import json
from pyodide.http import pyfetch # pyright: ignore[reportMissingImports]
from decimal import Decimal,getcontext,MAX_EMAX
import datetime as dt
import math
import csv
CODE = "e9b9-5zxw-frkc-gqss"
URI = "wss://bogo.swapjs.dev/ws"
n=25
def D(n):
    if n:return n*D(n-1)-1+2*(1-n%2)
    return 1
def f(n,k):
    return math.comb(n,k)*D(n-k)
def uptof(n,k):
    return sum([f(n,i) for i in range(k,n+1)])
chances=[Decimal(uptof(n,k))/Decimal(math.factorial(n)) for k in range(1,26)]
def calc_chance(k,shuffles:int):
    getcontext().prec=30
    getcontext().Emax=MAX_EMAX
    f=chances[k-1]
    return 1-(Decimal(1)-f)**int(shuffles)

async def find_stuff(code):
    req = await pyfetch(
            "https://bogo.swapjs.dev/api/account/login",
            data=json.dumps({"code": code}).encode("utf-8"),
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            method="POST",
        )
    if req.status==200:
        data=await req.json()
        return data["uuid"],data["nickname"]
    return None, None

last_shuffles=0
def process(message, ws):
    global last_shuffles
    data = json.loads(message)
    msg_type = data.get("type")

    if msg_type == "ping":
        ws.send(json.dumps({"type": "pong", "t": data["t"]}))
    if msg_type == "welcome":
        print(data)
    if msg_type=="stats_tick":
        shuffles=data['total_crowd']
        output=""
        for k in range(1,26):
            rate=(shuffles-last_shuffles)
            output+=f"chance to get a {k}+ /25 up to now: {round(calc_chance(k,shuffles)*100,5)}%\n                       {" "if k>=10 else ""}each tick: {round(calc_chance(k,rate)*100,5)}%\n"
        last_shuffles=shuffles
        element.innerText=output



async def test():
    uuid='6387b259-f7a5-4c48-84f4-974a8e14a315'
    nickname='tungsten'
    ws=websockets(url=URI)
    def on_open(event):
        ws.send(
            json.dumps(
                {
                    "type":"hello",
                    "v":5,
                    "uuid":uuid,
                    "nickname":nickname,
                    "code":CODE,
                }
            )
        )
    ws.onopen=on_open
    def on_message(event):
        process(event.data, ws)
    ws.onmessage=on_message

CSV_URL="https://docs.google.com/spreadsheets/d/e/2PACX-1vTuPEsPcLX3dLRD66g81Qotpm0MpaxXyN8dU_SOg5ijDXAQBlc0kaBxzcGOoQl8MlndYJUe7fPN3bXM/pub?output=csv"
async def render_csv():
    table=document.querySelector("#table-body")
    res=await pyfetch(CSV_URL,method="GET")
    news=csv.reader((await res.string()).splitlines())
    htmlrows=[]
    for row in news:
        if(len(row)>=1):
            htmlrows.append(f"<tr><td>{row[0]}</td><td>{row[1]if len(row)>1 else ""}</td></tr>")
    table.innerHTML="".join(htmlrows[::-1])
if __name__ == "__main__":
    asyncio.ensure_future(test())
    asyncio.ensure_future(render_csv())
