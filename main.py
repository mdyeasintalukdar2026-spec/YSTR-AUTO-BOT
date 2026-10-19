import os
import time
import requests
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # ব্রাউজার বা জাভাস্ক্রিপ্ট থেকে রিকোয়েস্ট গ্রহণের জন্য CORS এনেবল করা হলো

# Environment Variable থেকে Twelve Data API Key রিড করা হবে
API_KEY = os.environ.get('TWELVE_DATA_API_KEY')
SYMBOL = "EUR/USD"  # রিয়েল কারেন্সি পেয়ার
INTERVAL = "1min"

def fetch_market_data():
    """Twelve Data API থেকে রিয়েল-টাইম ক্যান্ডেলস্টিক ডাটা ফেচ করার ফাংশন"""
    if not API_KEY:
        print("Error: TWELVE_DATA_API_KEY is missing!")
        return None
    
    url = f"https://api.twelvedata.com/time_series?symbol={SYMBOL}&interval={INTERVAL}&outputsize=30&apikey={API_KEY}"
    try:
        response = requests.get(url)
        data = response.json()
        if "values" in data:
            return data["values"]
        else:
            print(f"API Error Response: {data}")
    except Exception as e:
        print(f"Connection Error: {e}")
    return None

def analyze_market_rules(values):
    """
    আন্তর্জাতিক মাল্টি-লেয়ার টেকনিক্যাল ইন্ডিকেটর এবং রুলস।
    এখানে কোনো ফেক বা রেন্ডম সিগন্যাল নেই; সম্পূর্ণ রিয়েল প্রাইস অ্যাকশন ভিত্তিক।
    """
    if not values or len(values) < 15:
        return "WAIT", "Insufficient Market Data for Analysis"
    
    # ক্লোজিং প্রাইসগুলো সাজানো
    closes = [float(v['close']) for v in values[::-1]]
    
    # শর্ট-টার্ম এবং লং-টার্ম মুভিং অ্যাভারেজ ক্যালকুলেশন
    sma_short = sum(closes[-5:]) / 5
    sma_long = sum(closes[-15:]) / 15
    
    current_price = closes[-1]
    previous_price = closes[-2]
    
    signal = "HOLD"
    reason = "Market consolidation phase. Waiting for strong confirmation."
    
    # নিখুঁত ট্রেন্ড ও মোমেন্টাম রুলস
    if current_price > sma_short and sma_short > sma_long and current_price > previous_price:
        signal = "CALL"  # আপ সিগন্যাল
        reason = "Strict Uptrend: Price above short & long SMA with valid momentum."
    elif current_price < sma_short and sma_short < sma_long and current_price < previous_price:
        signal = "PUT"   # ডাউন সিগন্যাল
        reason = "Strict Downtrend: Price below short & long SMA with valid momentum."
        
    return signal, reason

@app.route('/')
def home():
    """রেন্ডার সার্ভার ও বটের জন্য লাইভ এন্ডপয়েন্ট"""
    values = fetch_market_data()
    signal, reason = analyze_market_rules(values)
    
    return jsonify({
        "status": "Active & Secure",
        "symbol": SYMBOL,
        "signal": signal,
        "analysis_reason": reason,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
