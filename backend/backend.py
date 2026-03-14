from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from pydantic import BaseModel
import pandas as pd

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class UserSchema(BaseModel):
    username: str
    password: str

fake_user_db = {"testuser": "testpass"}

@app.post("/api/signup")
async def signup(user: UserSchema):
    if user.username in fake_user_db:
        return {"message": "Username already exists"}
    fake_user_db[user.username] = user.password
    return {"message": "User created"}

@app.post("/api/login")
async def login(user: UserSchema):
    if fake_user_db.get(user.username) == user.password:
        return {"message": "Login successful"}
    return HTTPException(status_code=401, detail="Invalid username or password")

@app.get("/api/stock/history/{symbol}")
async def get_stock_history(symbol: str, days: int = 90):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period=f"{days}d")
    if hist.empty:
        raise HTTPException(status_code=404, detail="No historical data found")
    hist.reset_index(inplace=True)
    hist['Date'] = hist['Date'].astype(str)
    data = hist[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')
    return data

@app.get("/api/stock/quote/{symbol}")
async def get_stock_quote(symbol: str):
    ticker = yf.Ticker(symbol)
    info = ticker.info
    if not info:
        raise HTTPException(status_code=404, detail="No quote data found")
    return {
        "lastPrice": info.get("regularMarketPrice"),
        "currency": info.get("currency", "USD"),
        "previousClose": info.get("previousClose"),
        "open": info.get("open"),
        "dayHigh": info.get("dayHigh"),
        "dayLow": info.get("dayLow"),
        "volume": info.get("volume"),
        "marketCap": info.get("marketCap"),
    }

@app.get("/api/news/{symbol}")
async def get_news(symbol: str):
    ticker = yf.Ticker(symbol)
    try:
        news = ticker.news
        return {"articles": news}
    except:
        return {"articles": []}
