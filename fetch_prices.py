import os
import yfinance as yf
from supabase import create_client

url = os.environ["SUPABASE_URL"].strip().split("/rest")[0].rstrip("/")
key = os.environ["SUPABASE_SERVICE_KEY"].strip()
print("URL check:", repr(url[:14]), "...", repr(url[-12:]), "length", len(url))

sb = create_client(url, key)
instruments = sb.table("instruments").select("id,symbol").execute().data

rows = []
for inst in instruments:
    try:
        hist = yf.Ticker(inst["symbol"]).history(period="5d")
        if hist.empty:
            print("No data:", inst["symbol"])
            continue
        price = float(hist["Close"].iloc[-1])
        rows.append({"instrument_id": inst["id"], "price": price})
        print(inst["symbol"], price)
    except Exception as e:
        print("Failed:", inst["symbol"], e)

if rows:
    sb.table("prices").insert(rows).execute()
    print(f"Saved {len(rows)} prices")
