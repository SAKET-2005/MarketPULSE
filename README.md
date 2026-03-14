# MarketPULSE

MarketPULSE is a full-stack stock analysis platform that provides real-time financial insights, technical indicators, and market data visualization.

## Features

• Real-time stock data retrieval using the yfinance API  
• Interactive candlestick charts and technical indicators  
• FastAPI backend providing stock data and news APIs  
• Streamlit dashboard for interactive financial visualization  
• User authentication with bcrypt and MySQL  
• USD to INR price conversion  

## Tech Stack

Frontend  
- Streamlit  
- Plotly  

Backend  
- FastAPI  
- Python  

Database  
- MySQL  

APIs  
- yfinance  

## Project Structure
```
MarketPULSE
│
├── frontend
├── backend
├── database
├── data
└── requirements.txt
```

## Running the Project

### Start Backend
```
uvicorn backend.backend:app --reload
```

### Run Frontend
```
streamlit run frontend/marketpulse_gui.py
```

## Future Improvements

- AI-based stock prediction models
- Portfolio tracking
- Advanced financial indicators
