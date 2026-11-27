import os
import yfinance as yf
from supabase import create_client

sb = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])
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
