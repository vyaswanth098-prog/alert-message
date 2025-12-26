from twilio.rest import Client
from dotenv import load_dotenv
import os
import yfinance as yf
import pandas as pd

top_companies_data = pd.read_csv(
    "https://archives.nseindia.com/content/indices/ind_nifty500list.csv",
    encoding="utf-8"
)

top_companies_symbols = [symbol + ".NS" for symbol in top_companies_data["Symbol"]]

records = {}

def per(current, previous):
    if current is None or previous in (None, 0):
        return None
    return ((current - previous) / previous) * 100

for i in top_companies_symbols:
    try:
        point = yf.Ticker(i)
        details = point.info

        if details:
            records[i] = {
                "previous_close": details.get("regularMarketPreviousClose"),
                "last_price": details.get("regularMarketPrice"),
                "percentage": per(details.get("regularMarketPrice"), details.get("regularMarketPreviousClose"))
            }
    except:
        pass

message_text = ""

for i, data in records.items():
    if data["percentage"] is not None and data["percentage"] > 5:
        symbol = i.replace(".NS", "")

        company_row = top_companies_data[ top_companies_data["Symbol"] == symbol]["Company Name"]

        if not company_row.empty:
            company_name = company_row.values[0]

            message_text += (
                f"{company_name} increased by {data['percentage']:.2f}%\n"
                f"and its current price is {data['last_price']}\n\n"
            )
if message_text != "":
    load_dotenv()

    account_sid = os.getenv("TWILIO_ACCOUNT_SID")
    auth_token = os.getenv("TWILIO_AUTH_TOKEN")
    from_number = os.getenv("TWILIO_NUMBER")
    to_number = os.getenv("MY_NUMBER")

    client = Client(account_sid, auth_token)

    sms = client.messages.create(
        body=message_text,
        from_=from_number,
        to=to_number
    )

    print(f"Message SID: {sms.sid}")
else:
    print("No stocks increased today.")


