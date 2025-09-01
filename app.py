# import os
# import re
# import time
# import feedparser
# import pandas as pd
# import streamlit as st
# from typing import List, Tuple, Dict
# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
# import plotly.express as px
# from urllib.parse import quote_plus, urlparse
# import requests
# from datetime import datetime, timedelta
# import uuid

# # --- Import yfinance ---
# import yfinance as yf

# # -------------------- PAGE CONFIG --------------------
# st.set_page_config(page_title="India Stock News Sentiment Screener (NSE & BSE)", layout="wide")

# # --- API KEY CONFIG ---
# ALPHA_VANTAGE_API_KEY = st.secrets.get("alpha_vantage_api_key", os.environ.get("ALPHA_VANTAGE_API_KEY", None))

# if not ALPHA_VANTAGE_API_KEY:
#     st.warning("⚠️ **Warning:** Alpha Vantage API Key not found. Daily price data will be mock.", icon="⚠️")

# # --- CLOCK JAVASCRIPT ---
# CLOCK_JS_TEMPLATE = """
# <div id="{clock_id}" style="text-align:center; color:gray; font-size:small;"></div>
# <script>
#     function updateClock_{unique_id}() {{
#         var now = new Date();
#         var options = {{ 
#             weekday: 'short', 
#             year: 'numeric', 
#             month: 'short', 
#             day: 'numeric', 
#             hour: '2-digit', 
#             minute: '2-digit', 
#             second: '2-digit', 
#             hour12: false 
#         }};
#         var timeString = now.toLocaleDateString('en-IN', options);
#         document.getElementById("{clock_id}").innerHTML = 'Current local time: ' + timeString;
#     }}
#     updateClock_{unique_id}();
#     setInterval(updateClock_{unique_id}, 1000);
# </script>
# """

# # --- MOCK STOCK PRICE DATA (as a fallback) ---
# mock_stock_prices = {
#     "GAIL": {
#         "today_low": 120.50, "today_high": 124.80, "52week_low": 95.00,
#         "52week_high": 135.20, "last_price": 123.15, "last_updated": datetime.now() - timedelta(minutes=15)
#     },
#     "RELIANCE": {
#         "today_low": 2800.00, "today_high": 2850.00, "52week_low": 2200.00,
#         "52week_high": 3000.00, "last_price": 2845.50, "last_updated": datetime.now() - timedelta(minutes=10)
#     },
#     "TCS": {
#         "today_low": 3900.00, "today_high": 3950.00, "52week_low": 3200.00,
#         "52week_high": 4100.00, "last_price": 3940.20, "last_updated": datetime.now() - timedelta(minutes=5)
#     },
#     "INFY": {
#         "today_low": 1500.00, "today_high": 1520.00, "52week_low": 1200.00,
#         "52week_high": 1600.00, "last_price": 1515.75, "last_updated": datetime.now() - timedelta(minutes=20)
#     },
#     "HDFCBANK": {
#         "today_low": 1600.00, "today_high": 1630.00, "52week_low": 1400.00,
#         "52week_high": 1700.00, "last_price": 1625.00, "last_updated": datetime.now() - timedelta(minutes=8)
#     },
#     "ICICIBANK": {
#         "today_low": 1000.00, "today_high": 1020.00, "52week_low": 850.00,
#         "52week_high": 1050.00, "last_price": 1018.50, "last_updated": datetime.now() - timedelta(minutes=12)
#     },
#     "SBIN": {
#         "today_low": 750.00, "today_high": 765.00, "52week_low": 600.00,
#         "52week_high": 780.00, "last_price": 762.25, "last_updated": datetime.now() - timedelta(minutes=7)
#     },
#     "LT": {
#         "today_low": 3500.00, "today_high": 3550.00, "52week_low": 2800.00,
#         "52week_high": 3600.00, "last_price": 3540.10, "last_updated": datetime.now() - timedelta(minutes=18)
#     },
#     "ITC": {
#         "today_low": 420.00, "today_high": 430.00, "52week_low": 350.00,
#         "52week_high": 450.00, "last_price": 428.80, "last_updated": datetime.now() - timedelta(minutes=2)
#     }
# }

# def get_mock_price_data(symbol: str, exchange: str) -> Dict:
#     """Returns mock price data for a given stock symbol as a fallback."""
#     return mock_stock_prices.get(symbol, {
#         "today_low": "N/A", "today_high": "N/A", "52week_low": "N/A",
#         "52week_high": "N/A", "last_price": "N/A", "last_updated": datetime.now()
#     })

# @st.cache_data(ttl=300, show_spinner="Fetching real-time stock prices...") # Cache for 5 minutes
# def get_real_time_price_data(symbol: str, exchange: str) -> Dict:
#     """
#     Fetches daily price data from Alpha Vantage and 52-week high/low from yfinance.
#     """
#     price_info = {
#         "today_low": "N/A", "today_high": "N/A", "52week_low": "N/A",
#         "52week_high": "N/A", "last_price": "N/A", "last_updated": datetime.now()
#     }

#     # --- Alpha Vantage for Global Quote (Current Price, Daily High/Low) ---
#     if ALPHA_VANTAGE_API_KEY:
#         av_symbol = symbol
#         if exchange == "NSE":
#             av_symbol = f"{symbol}.NSE"
#         elif exchange == "BSE":
#             av_symbol = f"{symbol}.BSE"
        
#         av_base_url = "https://www.alphavantage.co/query"

#         try:
#             params_quote = {
#                 "function": "GLOBAL_QUOTE",
#                 "symbol": av_symbol,
#                 "apikey": ALPHA_VANTAGE_API_KEY
#             }
            
#             response_quote = requests.get(av_base_url, params=params_quote, timeout=10)
#             response_quote.raise_for_status()
#             data_quote = response_quote.json()

#             if "Global Quote" in data_quote and data_quote["Global Quote"]:
#                 quote = data_quote["Global Quote"]
#                 try: price_info["last_price"] = float(quote.get("05. price"))
#                 except (ValueError, TypeError): pass
#                 try: price_info["today_high"] = float(quote.get("03. high"))
#                 except (ValueError, TypeError): pass
#                 try: price_info["today_low"] = float(quote.get("04. low"))
#                 except (ValueError, TypeError): pass
                
#                 price_info["last_updated"] = datetime.now()
#             elif "Note" in data_quote and "per minute" in data_quote["Note"]:
#                 st.warning(f"Alpha Vantage API rate limit hit for {av_symbol} (Global Quote). Displaying partial/mock daily data.", icon="⏱️")
#             elif "Error Message" in data_quote:
#                 st.error(f"Alpha Vantage API error for {av_symbol} (Global Quote): {data_quote['Error Message']}. Displaying partial/mock daily data.", icon="🚫")
#             else:
#                 st.warning(f"Alpha Vantage did not return expected Global Quote for {av_symbol}. Displaying mock data for daily prices.", icon="🔍")
#                 mock_daily_data = get_mock_price_data(symbol, exchange)
#                 price_info["today_low"] = mock_daily_data["today_low"]
#                 price_info["today_high"] = mock_daily_data["today_high"]
#                 price_info["last_price"] = mock_daily_data["last_price"]
#                 price_info["last_updated"] = mock_daily_data["last_updated"]
                
#         except requests.exceptions.Timeout:
#             st.error(f"Request to Alpha Vantage for {av_symbol} (Global Quote) timed out. Using mock data for daily prices.", icon="⏳")
#             mock_daily_data = get_mock_price_data(symbol, exchange)
#             price_info["today_low"] = mock_daily_data["today_low"]
#             price_info["today_high"] = mock_daily_data["today_high"]
#             price_info["last_price"] = mock_daily_data["last_price"]
#             price_info["last_updated"] = mock_daily_data["last_updated"]
#         except requests.exceptions.RequestException as e:
#             st.error(f"Network error fetching Alpha Vantage Global Quote for {av_symbol}: {e}. Using mock data for daily prices.", icon="🔌")
#             mock_daily_data = get_mock_price_data(symbol, exchange)
#             price_info["today_low"] = mock_daily_data["today_low"]
#             price_info["today_high"] = mock_daily_data["today_high"]
#             price_info["last_price"] = mock_daily_data["last_price"]
#             price_info["last_updated"] = mock_daily_data["last_updated"]
#         except Exception as e:
#             st.error(f"Unexpected error fetching Alpha Vantage Global Quote for {av_symbol}: {e}. Using mock data for daily prices.", icon="❓")
#             mock_daily_data = get_mock_price_data(symbol, exchange)
#             price_info["today_low"] = mock_daily_data["today_low"]
#             price_info["today_high"] = mock_daily_data["today_high"]
#             price_info["last_price"] = mock_daily_data["last_price"]
#             price_info["last_updated"] = mock_daily_data["last_updated"]
#     else:
#         st.info("Alpha Vantage API Key not configured. Using mock data for daily prices.", icon="ℹ️")
#         mock_daily_data = get_mock_price_data(symbol, exchange)
#         price_info["today_low"] = mock_daily_data["today_low"]
#         price_info["today_high"] = mock_daily_data["today_high"]
#         price_info["last_price"] = mock_daily_data["last_price"]
#         price_info["last_updated"] = mock_daily_data["last_updated"]


#     # --- yfinance for 52-Week High/Low ---
#     # yfinance often needs specific ticker formats for Indian exchanges
#     # E.g., RELIANCE.NS for NSE, RELIANCE.BO for BSE
#     yfinance_symbol = symbol
#     if exchange == "NSE":
#         yfinance_symbol = f"{symbol}.NS"
#     elif exchange == "BSE":
#         yfinance_symbol = f"{symbol}.BO"
    
#     # Introduce a short delay before yfinance call to avoid potential rate limit issues
#     # with Alpha Vantage if they share any underlying infrastructure or for general good practice.
#     time.sleep(1)

#     try:
#         ticker = yf.Ticker(yfinance_symbol)
#         # Fetch data for a bit more than 1 year to ensure we cover the full 52 weeks of trading days
#         hist = ticker.history(period="1y") 

#         if not hist.empty:
#             # Calculate 52-week high/low from the fetched historical data
#             price_info["52week_high"] = hist['High'].max()
#             price_info["52week_low"] = hist['Low'].min()
#         else:
#             st.warning(f"yfinance: No historical data found for {yfinance_symbol} in the last 52 weeks. Displaying N/A.", icon="📉")

#     except Exception as e:
#         st.error(f"Error fetching 52-week data for {yfinance_symbol} from yfinance: {e}. Using mock 52-week data.", icon="🚫")
#         mock_52week_data = get_mock_price_data(symbol, exchange)
#         price_info["52week_high"] = mock_52week_data["52week_high"]
#         price_info["52week_low"] = mock_52week_data["52week_low"]

#     return price_info


# # -------------------- HEADER --------------------
# st.markdown(
#     """
#     <div style="text-align:center">
#       <h1 style="margin-bottom:0">📊 India Stock News Sentiment Screener</h1>
#       <p style="color:gray;margin-top:6px">
#         NSE & BSE stocks · Free Google News RSS · VADER Sentiment · Buy/Hold/Sell signals
#       </p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )

# # Display data last processed time (server-side, updates on rerun)
# data_processed_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
# st.markdown(f"<p style='text-align:center; color:gray; font-size:small;'>Data last processed: {data_processed_time_str}</p>", unsafe_allow_html=True)

# # Display real-running client-side clock
# unique_clock_id = str(uuid.uuid4()).replace('-', '') # Generate a unique ID for the clock div and function
# st.html(CLOCK_JS_TEMPLATE.format(clock_id=f"live-clock-{unique_clock_id}", unique_id=unique_clock_id))


# # -------------------- HELPERS --------------------
# DATA_DIR = "data"
# os.makedirs(DATA_DIR, exist_ok=True) # Ensure the 'data' directory exists

# def safe_lower(s):
#     """Safely converts a value to lowercase string, handling NaN."""
#     return str(s).strip().lower() if pd.notna(s) else ""

# def load_symbol_file(path: str, expected_cols: List[str]) -> pd.DataFrame:
#     """
#     Loads stock symbols from a CSV or Excel file, flexibly mapping column names.
    
#     Args:
#         path (str): Path to the stock file (e.g., 'data/nse_stocks.csv').
#         expected_cols (List[str]): A list of expected column names,
#                                    can use '|' for alternatives (e.g., "symbol|scrip code").
#                                    The first name in each alternative is used as the target column.
#     Returns:
#         pd.DataFrame: A DataFrame with standardized column names ("symbol", "name"),
#                       or an empty DataFrame if the file cannot be loaded or columns not found.
#     """
#     if not os.path.exists(path):
#         return pd.DataFrame() # Return empty if file does not exist

#     df = pd.DataFrame()
#     try:
#         if path.endswith('.csv'):
#             df = pd.read_csv(path)
#         elif path.endswith(('.xls', '.xlsx')):
#             df = pd.read_excel(path)
#         else:
#             st.warning(f"Unsupported file format for {path}. Please use .csv or .xlsx.")
#             return pd.DataFrame()
#     except Exception as e:
#         st.error(f"Error loading file {path}: {e}. Please ensure it's a valid CSV or Excel.")
#         return pd.DataFrame()
    
#     out = pd.DataFrame()
#     found_cols_map = {c.lower(): c for c in df.columns} # Map lowercase column names to actual names

#     for want_spec in expected_cols:
#         target_col_name = want_spec.split('|')[0].lower() # E.g., 'symbol' from 'symbol|stock_id'
#         possible_source_names = [name.lower() for name in want_spec.split('|')]
        
#         hit_actual_col = None
        
#         # 1. Try exact lowercase match
#         for p_name_lower in possible_source_names:
#             if p_name_lower in found_cols_map:
#                 hit_actual_col = found_cols_map[p_name_lower]
#                 break
        
#         # 2. If not found, try regex search for partial or case-insensitive matches
#         if hit_actual_col is None:
#             for p_name_lower in possible_source_names:
#                 for actual_df_col_name in df.columns:
#                     # Use word boundary for more precise regex matching
#                     if re.search(r'\b' + re.escape(p_name_lower) + r'\b', actual_df_col_name, flags=re.IGNORECASE):
#                         hit_actual_col = actual_df_col_name
#                         break
#                 if hit_actual_col:
#                     break

#         if hit_actual_col is not None:
#             out[target_col_name] = df[hit_actual_col]
#         else:
#             st.warning(f"Could not find a column matching '{want_spec}' in {path}. "
#                        f"Please ensure your file contains columns like '{' or '.join(want_spec.split('|'))}'.")

#     return out


# @st.cache_data(show_spinner=False)
# def load_all_symbols() -> Tuple[pd.DataFrame, pd.DataFrame]:
#     """
#     Loads NSE and BSE stock lists, standardizing their column names to "SYMBOL" and "NAME".
#     Returns (nse_df, bse_df).
    
#     Expected CSV formats:
#     nse_stocks.csv: Needs columns like "SYMBOL" and "NAME OF COMPANY" (or "NAME").
#     bse_stocks.csv: Needs columns like "Security Id" (or "SCRIP CODE" or "SYMBOL")
#                     and "Security Name" (or "NAME").
#     """
#     nse_raw = load_symbol_file(
#         os.path.join(DATA_DIR, "nse_stocks.csv"),
#         expected_cols=["symbol", "name of company|name"] # Target names will be 'symbol', 'name of company'
#     )
#     bse_raw = load_symbol_file(
#         os.path.join(DATA_DIR, "bse_stocks.csv"),
#         expected_cols=["security id|scrip code|symbol", "security name|name"] # Target names will be 'security id', 'security name'
#     )

#     nse = pd.DataFrame(columns=["SYMBOL", "NAME"])
#     if not nse_raw.empty:
#         # After load_symbol_file, columns are lowercase based on the first part of expected_cols
#         sym_col = "symbol"
#         name_col = "name of company" if "name of company" in nse_raw.columns else "name"
        
#         if sym_col in nse_raw.columns and name_col in nse_raw.columns:
#             nse["SYMBOL"] = nse_raw[sym_col].astype(str).str.strip()
#             nse["NAME"] = nse_raw[name_col].astype(str).str.strip()
#             nse = nse.dropna(subset=["SYMBOL", "NAME"]).drop_duplicates(subset=["SYMBOL"])
#             st.sidebar.success(f"Loaded {len(nse)} NSE symbols.")
#         else:
#             st.sidebar.warning("NSE file loaded but required columns ('symbol', 'name of company' or 'name') not found or standardized correctly.")

#     bse = pd.DataFrame(columns=["SYMBOL", "NAME"])
#     if not bse_raw.empty:
#         sym_col_candidates = ["security id", "scrip code", "symbol"] # Prioritize order
#         sym_col = next((col for col in sym_col_candidates if col in bse_raw.columns), None)
#         name_col = "security name" if "security name" in bse_raw.columns else "name"

#         if sym_col and name_col and sym_col in bse_raw.columns and name_col in bse_raw.columns:
#             bse["SYMBOL"] = bse_raw[sym_col].astype(str).str.strip()
#             bse["NAME"] = bse_raw[name_col].astype(str).str.strip()
#             bse = bse.dropna(subset=["SYMBOL", "NAME"]).drop_duplicates(subset=["SYMBOL"])
#             st.sidebar.success(f"Loaded {len(bse)} BSE symbols.")
#         else:
#             st.sidebar.warning("BSE file loaded but required columns ('security id'/'scrip code'/'symbol', 'security name' or 'name') not found or standardized correctly.")

#     return nse, bse


# def google_news_rss_query(name_or_symbol: str) -> str:
#     """
#     Constructs a URL-encoded Google News RSS feed URL for a given stock.
#     Uses quote_plus for robust URL encoding of the query parameter.
#     """
#     # Build a modest query; quotes often help with company names for exact match
#     search_term = f'"{name_or_symbol}" stock'
#     # quote_plus converts spaces to '+' and other special characters to %xx
#     q = quote_plus(search_term) 
    
#     base_url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    
#     # Basic URL structure validation before attempting to fetch
#     try:
#         parsed_url = urlparse(base_url)
#         if not all([parsed_url.scheme, parsed_url.netloc]):
#             st.warning(f"Generated an invalid URL structure for '{name_or_symbol}': {base_url}")
#             return ""
#         # Additional check for control characters, though quote_plus should prevent it
#         if re.search(r'[\x00-\x1F\x7F]', base_url): 
#              st.warning(f"URL still contains control characters after encoding for '{name_or_symbol}': {base_url}")
#              return ""

#     except Exception as e:
#         st.warning(f"Error validating URL for '{name_or_symbol}': {e} - {base_url}")
#         return ""

#     return base_url

# # Initialize VADER sentiment analyzer
# analyzer = SentimentIntensityAnalyzer()

# def label_from_score(score: float) -> str:
#     """Categorizes sentiment score into 'Positive', 'Negative', or 'Neutral'."""
#     if score > 0.05:
#         return "Positive"
#     elif score < -0.05:
#         return "Negative"
#     return "Neutral"

# def predict_signal(pos: int, neg: int) -> str:
#     """Generates a simple Buy/Hold/Sell signal based on positive and negative headline counts."""
#     if pos > neg:
#         return "✅ Buy"
#     if neg > pos:
#         return "❌ Sell"
#     return "⚖️ Hold"

# # -------------------- SIDEBAR --------------------
# st.sidebar.header("⚙️ Controls")

# # Load stock symbols and display initial warnings/successes
# nse_df, bse_df = load_all_symbols()

# # Determine initial checkbox state based on whether data was loaded
# initial_use_nse = not nse_df.empty
# initial_use_bse = not bse_df.empty

# # Handle case where no files are found, use a default watchlist
# if nse_df.empty and bse_df.empty:
#     st.sidebar.warning(
#         "No NSE/BSE lists found. Add `data/nse_stocks.csv` and `data/bse_stocks.csv` for full coverage. "
#         "Using a small default watchlist for now."
#     )
#     default_list = pd.DataFrame({
#         "SYMBOL": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "LT", "ITC", "GAIL"],
#         "NAME":   ["Reliance Industries", "Tata Consultancy Services", "Infosys", "HDFC Bank",
#                    "ICICI Bank", "State Bank of India", "Larsen & Toubro", "ITC", "GAIL (India) Limited"],
#         "EXCHANGE": ["NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE"] # Default to NSE for consistency
#     })
#     nse_df = default_list.copy() # Assign default to NSE for selection purposes
#     initial_use_nse = True # Automatically select NSE if using default list
#     initial_use_bse = False # Ensure BSE is not selected by default if only default NSE is used

# # Exchange selection checkboxes
# use_nse = st.sidebar.checkbox("Use NSE List", value=initial_use_nse)
# use_bse = st.sidebar.checkbox("Use BSE List", value=initial_use_bse)

# # Build the universe of selected stocks
# universe = pd.DataFrame(columns=["SYMBOL", "NAME", "EXCHANGE"])
# if use_nse and not nse_df.empty:
#     tmp = nse_df.copy()
#     tmp["EXCHANGE"] = "NSE"
#     universe = pd.concat([universe, tmp], ignore_index=True)
# if use_bse and not bse_df.empty:
#     tmp = bse_df.copy()
#     tmp["EXCHANGE"] = "BSE"
#     universe = pd.concat([universe, tmp], ignore_index=True)

# # If no stocks are in the universe after selection, stop the app
# if universe.empty:
#     st.error("No stocks available for selection. Please check your data files or select at least one exchange in the sidebar.")
#     st.stop()


# # Prepare options for the multiselect widget
# options_display = []
# name_map = {}

# if "NAME" in universe.columns and universe["NAME"].notna().any() and "SYMBOL" in universe.columns and "EXCHANGE" in universe.columns:
#     for _, row in universe.iterrows():
#         display_str = f"{row['NAME']} ({row['SYMBOL']} · {row['EXCHANGE']})"
#         options_display.append(display_str)
#         name_map[display_str] = (row['NAME'], row['SYMBOL'], row['EXCHANGE'])
# elif "SYMBOL" in universe.columns and "EXCHANGE" in universe.columns: # Fallback if NAME is missing or all NaN
#     for _, row in universe.iterrows():
#         display_str = f"{row['SYMBOL']} ({row['EXCHANGE']})"
#         options_display.append(display_str)
#         name_map[display_str] = (row['SYMBOL'], row['SYMBOL'], row['EXCHANGE'])
# else:
#     st.error("Could not find 'SYMBOL' and 'EXCHANGE' columns in stock data. Please check your CSV/Excel files and ensure correct headers like 'SYMBOL' or 'Security Id'.")
#     st.stop()

# # Sort options for better user experience
# options_display = sorted(options_display, key=lambda s: s.lower())

# # Select Stocks multiselect widget
# selected_display = st.sidebar.multiselect(
#     "Select Stocks (search by name/symbol)",
#     options=options_display,
#     default=options_display[:min(5, len(options_display))] # Default to first 5, or fewer if not enough
# )

# # Sliders for configuration
# limit_per_stock = st.sidebar.slider("Headlines per stock", 3, 20, 10, 1)
# pause_ms = st.sidebar.slider("Fetch delay (ms, avoids rate-limit)", 0, 1000, 150, 50)

# st.sidebar.markdown("---")
# st.sidebar.markdown("**CSV setup (free):**")
# st.sidebar.caption(
#     "- Put NSE CSV at `data/nse_stocks.csv` (contains SYMBOL & NAME OF COMPANY)\n"
#     "- Put BSE CSV at `data/bse_stocks.csv` (contains Security Id/Code & Security Name)\n"
#     "Deploy to Streamlit Cloud: include these files in your repo."
# )

# # -------------------- DATA COLLECTION --------------------
# all_rows: List[Dict] = []
# if selected_display:
#     progress_text = "Fetching headlines & analyzing sentiment..."
#     my_bar = st.progress(0, text=progress_text) # Initialize progress bar
    
#     for i, display in enumerate(selected_display):
#         name, symbol, ex = name_map[display]
#         query_term = name if name and name != symbol else symbol
        
#         my_bar.progress((i + 1) / len(selected_display), text=f"Fetching news for {name} ({symbol})...")

#         rss_url = google_news_rss_query(query_term)

#         if pause_ms:
#             time.sleep(pause_ms / 1000)

#         if not rss_url: # Skip if URL generation failed (e.g., due to validation error)
#             st.warning(f"Skipping {name} ({symbol}) due to invalid RSS URL generation.")
#             continue

#         try:
#             # CRITICAL FIX: Use requests to fetch content, then feedparser to parse
#             headers = {
#                 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
#             }
#             # Fetch the content using requests
#             response = requests.get(rss_url, timeout=10, headers=headers)
#             response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
#             feed_content = response.text # Get the raw text content of the RSS feed
#             # Pass the raw content to feedparser, bypassing its internal URL fetching
#             feed = feedparser.parse(feed_content) 
            
#             if feed.bozo: # Check for well-formedness of the XML
#                 st.warning(f"Error parsing RSS feed for {name} ({symbol}): {feed.bozo_exception}. Skipping.")
#                 st.info(f"Problematic RSS URL: `{rss_url}`")
#                 continue

#             if not feed.entries:
#                 st.info(f"No headlines found for {name} ({symbol}) from Google News (URL: `{rss_url}`). "
#                         "This could be due to no recent news, or Google News filtering. Skipping.")
#                 continue

#             for entry in feed.entries[:limit_per_stock]:
#                 title = entry.get("title", "")
#                 if not title: # Skip entries without a title
#                     continue
#                 score = analyzer.polarity_scores(title)["compound"]
#                 sentiment = label_from_score(score)
#                 all_rows.append({
#                     "Stock": symbol,
#                     "Name": name,
#                     "Exchange": ex,
#                     "Headline": title,
#                     "Sentiment": sentiment,
#                     "Score": score,
#                     "Link": entry.get("link", "#") # Get the link to the news article
#                 })
#         except requests.exceptions.Timeout:
#             st.error(f"Request to Google News RSS for {name} ({symbol}) timed out after 10 seconds. URL: `{rss_url}`")
#         except requests.exceptions.RequestException as e:
#             st.error(f"Error fetching RSS feed for {name} ({symbol}): {e}. Check network connection or URL. URL: `{rss_url}`")
#         except Exception as e:
#             st.error(f"An unexpected error occurred while processing news for {name} ({symbol}): {e}")
#             st.info(f"The problematic RSS URL was: `{rss_url}`")
#             continue
    
#     my_bar.empty() # Clear the progress bar when done

# # -------------------- OUTPUT --------------------
# if not all_rows:
#     st.info("No headlines found yet. Try reducing your selection, pick well-known names, or check your stock list files. "
#             "Ensure your `data/nse_stocks.csv` and `data/bse_stocks.csv` are correctly formatted.")
# else:
#     df = pd.DataFrame(all_rows)

#     # ---------- Top Headlines Across Selection ----------
#     st.markdown("## 🌟 Top Headlines Across Selection")
#     c1, c2 = st.columns(2)
#     with c1:
#         st.markdown("### 🟢 Most Positive")
#         top_pos = df[df["Sentiment"] == "Positive"].nlargest(5, "Score")
#         if top_pos.empty:
#             st.write("No strong positive headlines.")
#         else:
#             for _, r in top_pos.iterrows():
#                 st.markdown(f"- **{r['Name']} ({r['Stock']})** — [{r['Headline']}]({r['Link']})")

#     with c2:
#         st.markdown("### 🔴 Most Negative")
#         top_neg = df[df["Sentiment"] == "Negative"].nsmallest(5, "Score")
#         if top_neg.empty:
#             st.write("No strong negative headlines.")
#         else:
#             for _, r in top_neg.iterrows():
#                 st.markdown(f"- **{r['Name']} ({r['Stock']})** — [{r['Headline']}]({r['Link']})")

#     # ---------- Per-Stock Sentiment & Signal ----------
#     st.markdown("---")
#     st.markdown("## 📊 Per-Stock Sentiment & Signal")

#     summary_records = []
#     # Group by all identifying columns for a robust summary
#     for (sym, name, ex), g in df.groupby(["Stock", "Name", "Exchange"]):
#         pos = (g["Sentiment"] == "Positive").sum()
#         neg = (g["Sentiment"] == "Negative").sum()
#         neu = (g["Sentiment"] == "Neutral").sum()
#         avg = g["Score"].mean()
#         signal = predict_signal(pos, neg)
#         summary_records.append({
#             "Stock": sym,
#             "Name": name,
#             "Exchange": ex,
#             "Positive": pos,
#             "Negative": neg,
#             "Neutral": neu,
#             "AvgScore": round(avg, 3),
#             "Prediction": signal
#         })

#     summary_df = pd.DataFrame(summary_records).sort_values(["Prediction", "AvgScore"], ascending=[True, False])
#     st.dataframe(summary_df, use_container_width=True)

#     # ---------- Overall Market Sentiment ----------
#     st.markdown("## 🌍 Overall Sentiment")
#     total_pos = (df["Sentiment"] == "Positive").sum()
#     total_neg = (df["Sentiment"] == "Negative").sum()
#     total_neu = (df["Sentiment"] == "Neutral").sum()

#     mcol1, mcol2, mcol3, mcol4 = st.columns(4)
#     mcol1.metric("Total Positive", total_pos)
#     mcol2.metric("Total Negative", total_neg)
#     mcol3.metric("Total Neutral", total_neu)

#     # Display market sentiment only if there's significant positive or negative news
#     if total_pos > 0 or total_neg > 0:
#         if total_pos > total_neg:
#             mkt_msg = "📈 Market Sentiment: **Bullish** (tilt Buy)"
#             mcol4.success(mkt_msg)
#         elif total_neg > total_pos:
#             mkt_msg = "📉 Market Sentiment: **Bearish** (tilt Sell/Avoid)"
#             mcol4.error(mkt_msg)
#         else:
#             mkt_msg = "⚖️ Market Sentiment: **Neutral** (Wait & Watch)"
#             mcol4.warning(mkt_msg)
#     else:
#         mcol4.info("Not enough positive/negative news to determine overall market sentiment based on selected stocks.")

#     # ---------- Visualizations (Charts) ----------
#     st.markdown("## 📈 Visualizations")

#     # Per-stock bar chart for sentiment distribution
#     bar_data = summary_df.melt(
#         id_vars=["Stock", "Name", "Exchange", "Prediction", "AvgScore"],
#         value_vars=["Positive", "Negative", "Neutral"],
#         var_name="Sentiment",
#         value_name="Count"
#     )
#     fig_bar = px.bar(
#         bar_data, x="Stock", y="Count", color="Sentiment",
#         hover_data={"Name":True, "Exchange":True, "Prediction":True, "AvgScore":":.3f", "Count":True},
#         barmode="group", title="Sentiment Distribution per Stock"
#     )
#     st.plotly_chart(fig_bar, use_container_width=True)

#     # Overall pie chart for sentiment share
#     overall_counts = df["Sentiment"].value_counts().reset_index()
#     overall_counts.columns = ["Sentiment", "Count"]
#     fig_pie = px.pie(overall_counts, names="Sentiment", values="Count", title="Overall Sentiment Share")
#     st.plotly_chart(fig_pie, use_container_width=True)

#     # ---------- Detailed Headlines by Stock with Price Info ----------
#     st.markdown("---")
#     st.markdown("## 📰 Detailed Headlines by Stock & Price Info")
    
#     # Indicate which APIs are being used
#     api_status_messages = []
#     if ALPHA_VANTAGE_API_KEY:
#         api_status_messages.append("Alpha Vantage API (Daily Price)")
#     # Since yfinance is not technically an "API" in the same key-protected sense,
#     # and is unofficial, we can mention it separately or integrate its status.
#     api_status_messages.append("yfinance (52-Week Range - Unofficial)")
    
#     if api_status_messages:
#         st.info(f"Using: {', '.join(api_status_messages)}. (Data may be delayed on free tiers; yfinance is unofficial).", icon="ℹ️")
#     else:
#         st.warning("No API keys configured. Using **MOCK DATA** for all stock price data.", icon="⚠️")

#     for (sym, name, ex), g in df.groupby(["Stock", "Name", "Exchange"]):
#         st.subheader(f"📌 {name} ({sym}) · {ex}")
        
#         # Call the single function that now handles both APIs internally
#         price_data = get_real_time_price_data(sym, ex) 

#         col1, col2, col3, col4 = st.columns(4)
#         with col1:
#             st.metric("Last Price", price_data["last_price"])
#         with col2:
#             st.metric("Daily Low", price_data["today_low"])
#         with col3:
#             st.metric("Daily High", price_data["today_high"])
#         with col4:
#             last_updated_time = price_data["last_updated"]
#             if isinstance(last_updated_time, datetime):
#                  st.metric("Price Updated", last_updated_time.strftime("%H:%M:%S"))
#             else:
#                  st.metric("Price Updated", last_updated_time)
            
#         st.info(f"**52 Week Range:** Low: {price_data['52week_low']}, High: {price_data['52week_high']}")

#         st.markdown("---") # Separator for headlines
#         st.markdown(f"**Recent News Headlines for {name} ({sym}):**")
#         for _, r in g.sort_values("Score", ascending=False).iterrows():
#             emoji = "🟢" if r["Sentiment"] == "Positive" else ("🔴" if r["Sentiment"] == "Negative" else "🟡")
#             st.markdown(f"- {emoji} **{r['Sentiment']}** — [{r['Headline']}]({r['Link']})")
#         st.markdown("---")


# # -------------------- FOOTER TIP --------------------
# st.caption(
#     "Tip: For full NSE/BSE coverage, add CSVs into the `data/` folder and redeploy. "
#     "Google News RSS is free; headlines & tone may vary. Combine with your own price/risk rules."
# )
import os
import re
import time
import feedparser
import pandas as pd
import streamlit as st
from typing import List, Tuple, Dict
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import plotly.express as px
from urllib.parse import quote_plus, urlparse
import requests
from datetime import datetime, timedelta
import uuid

# --- Import yfinance ---
import yfinance as yf

# -------------------- CONFIGURATIONS --------------------
# Cache TTL for API data and auto-refresh interval
REFRESH_INTERVAL_SECONDS = 30 # Refresh every 30 seconds

# -------------------- PAGE CONFIG --------------------
st.set_page_config(page_title="India Stock News Sentiment Screener (NSE & BSE)", layout="wide")

# --- API KEY CONFIG ---
ALPHA_VANTAGE_API_KEY = st.secrets.get("alpha_vantage_api_key", os.environ.get("ALPHA_VANTAGE_API_KEY", None))

if not ALPHA_VANTAGE_API_KEY:
    st.warning("⚠️ **Warning:** Alpha Vantage API Key not found. Daily price data will have limited API fallback.", icon="⚠️")

# --- CLOCK JAVASCRIPT ---
CLOCK_JS_TEMPLATE = """
<div id="{clock_id}" style="text-align:center; color:gray; font-size:small;"></div>
<script>
    function updateClock_{unique_id}() {{
        var now = new Date();
        var options = {{ 
            weekday: 'short', 
            year: 'numeric', 
            month: 'short', 
            day: 'numeric', 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit', 
            hour12: false 
        }};
        var timeString = now.toLocaleDateString('en-IN', options);
        document.getElementById("{clock_id}").innerHTML = 'Current local time: ' + timeString;
    }}
    updateClock_{unique_id}();
    setInterval(updateClock_{unique_id}, 1000);
</script>
"""

# --- MOCK STOCK PRICE DATA (as a fallback) ---
mock_stock_prices = {
    "GAIL": {
        "today_low": 120.50, "today_high": 124.80, "52week_low": 95.00,
        "52week_high": 135.20, "last_price": 123.15, "last_updated": datetime.now() - timedelta(minutes=15)
    },
    "RELIANCE": {
        "today_low": 2800.00, "today_high": 2850.00, "52week_low": 2200.00,
        "52week_high": 3000.00, "last_price": 2845.50, "last_updated": datetime.now() - timedelta(minutes=10)
    },
    "TCS": {
        "today_low": 3900.00, "today_high": 3950.00, "52week_low": 3200.00,
        "52week_high": 4100.00, "last_price": 3940.20, "last_updated": datetime.now() - timedelta(minutes=5)
    },
    "INFY": {
        "today_low": 1500.00, "today_high": 1520.00, "52week_low": 1200.00,
        "52week_high": 1600.00, "last_price": 1515.75, "last_updated": datetime.now() - timedelta(minutes=20)
    },
    "HDFCBANK": {
        "today_low": 1600.00, "today_high": 1630.00, "52week_low": 1400.00,
        "52week_high": 1700.00, "last_price": 1625.00, "last_updated": datetime.now() - timedelta(minutes=8)
    },
    "ICICIBANK": {
        "today_low": 1000.00, "today_high": 1020.00, "52week_low": 850.00,
        "52week_high": 1050.00, "last_price": 1018.50, "last_updated": datetime.now() - timedelta(minutes=12)
    },
    "SBIN": {
        "today_low": 750.00, "today_high": 765.00, "52week_low": 600.00,
        "52week_high": 780.00, "last_price": 762.25, "last_updated": datetime.now() - timedelta(minutes=7)
    },
    "LT": {
        "today_low": 3500.00, "today_high": 3550.00, "52week_low": 2800.00,
        "52week_high": 3600.00, "last_price": 3540.10, "last_updated": datetime.now() - timedelta(minutes=18)
    },
    "ITC": {
        "today_low": 420.00, "today_high": 430.00, "52week_low": 350.00,
        "52week_high": 450.00, "last_price": 428.80, "last_updated": datetime.now() - timedelta(minutes=2)
    }
}

def get_mock_price_data(symbol: str, exchange: str) -> Dict:
    """Returns mock price data for a given stock symbol as a fallback."""
    return mock_stock_prices.get(symbol, {
        "today_low": "N/A", "today_high": "N/A", "52week_low": "N/A",
        "52week_high": "N/A", "last_price": "N/A", "last_updated": datetime.now()
    })

def get_daily_price_from_yfinance(symbol: str, exchange: str) -> Dict:
    """
    Helper function to get daily price info (last, daily low/high) from yfinance.
    Returns: {"last_price": float, "today_low": float, "today_high": float, "last_updated": datetime}
    """
    yfinance_symbol = symbol
    if exchange == "NSE":
        yfinance_symbol = f"{symbol}.NS"
    elif exchange == "BSE":
        yfinance_symbol = f"{symbol}.BO"
    
    daily_info = {"last_price": "N/A", "today_low": "N/A", "today_high": "N/A", "last_updated": datetime.now()}

    try:
        ticker = yf.Ticker(yfinance_symbol)
        # Fetch intraday data for today, or daily data for a very short period
        # Intraday (1m, 5m, etc.) for '1d' period gives closest to current day's activity
        hist_today = ticker.history(period="1d", interval="5m") # 5-minute interval for today

        if not hist_today.empty:
            daily_info["last_price"] = hist_today['Close'].iloc[-1]
            daily_info["today_high"] = hist_today['High'].max()
            daily_info["today_low"] = hist_today['Low'].min()
            # yfinance's last close time is usually a good indicator of when the price was last updated
            daily_info["last_updated"] = hist_today.index[-1].to_pydatetime()
        else:
            st.warning(f"yfinance: No intraday data found for {yfinance_symbol} for today. Daily prices will be N/A.", icon="🔍")
            
    except Exception as e:
        st.error(f"Error fetching daily prices for {yfinance_symbol} from yfinance: {e}. Daily prices will be N/A.", icon="🚫")
    
    return daily_info


@st.cache_data(ttl=REFRESH_INTERVAL_SECONDS, show_spinner="Fetching real-time stock prices...")
def get_real_time_price_data(symbol: str, exchange: str) -> Dict:
    """
    Fetches daily price data (from Alpha Vantage or yfinance fallback)
    and 52-week high/low from yfinance.
    """
    price_info = {
        "today_low": "N/A", "today_high": "N/A", "52week_low": "N/A",
        "52week_high": "N/A", "last_price": "N/A", "last_updated": datetime.now()
    }

    # --- Attempt Alpha Vantage for Global Quote (Current Price, Daily High/Low) ---
    av_success = False
    if ALPHA_VANTAGE_API_KEY:
        av_symbol = symbol
        if exchange == "NSE":
            av_symbol = f"{symbol}.NSE"
        elif exchange == "BSE":
            av_symbol = f"{symbol}.BSE"
        
        av_base_url = "https://www.alphavantage.co/query"

        try:
            params_quote = {
                "function": "GLOBAL_QUOTE",
                "symbol": av_symbol,
                "apikey": ALPHA_VANTAGE_API_KEY
            }
            
            response_quote = requests.get(av_base_url, params=params_quote, timeout=10)
            response_quote.raise_for_status()
            data_quote = response_quote.json()

            if "Global Quote" in data_quote and data_quote["Global Quote"]:
                quote = data_quote["Global Quote"]
                try: price_info["last_price"] = float(quote.get("05. price"))
                except (ValueError, TypeError): pass
                try: price_info["today_high"] = float(quote.get("03. high"))
                except (ValueError, TypeError): pass
                try: price_info["today_low"] = float(quote.get("04. low"))
                except (ValueError, TypeError): pass
                
                price_info["last_updated"] = datetime.now() # Data fetched time
                av_success = True
            elif "Note" in data_quote and "per minute" in data_quote["Note"]:
                st.warning(f"Alpha Vantage API rate limit hit for {av_symbol} (Global Quote). Trying yfinance for daily prices.", icon="⏱️")
            elif "Error Message" in data_quote:
                st.error(f"Alpha Vantage API error for {av_symbol} (Global Quote): {data_quote['Error Message']}. Trying yfinance for daily prices.", icon="🚫")
            else:
                st.warning(f"Alpha Vantage did not return expected Global Quote for {av_symbol}. Trying yfinance for daily prices.", icon="🔍")
                
        except requests.exceptions.Timeout:
            st.error(f"Request to Alpha Vantage for {av_symbol} (Global Quote) timed out. Trying yfinance for daily prices.", icon="⏳")
        except requests.exceptions.RequestException as e:
            st.error(f"Network error fetching Alpha Vantage Global Quote for {av_symbol}: {e}. Trying yfinance for daily prices.", icon="🔌")
        except Exception as e:
            st.error(f"Unexpected error fetching Alpha Vantage Global Quote for {av_symbol}: {e}. Trying yfinance for daily prices.", icon="❓")
    else:
        st.info("Alpha Vantage API Key not configured. Trying yfinance for daily prices.", icon="ℹ️")

    # --- Fallback to yfinance for daily prices if AV failed or not configured ---
    if not av_success:
        daily_yfi_data = get_daily_price_from_yfinance(symbol, exchange)
        price_info.update(daily_yfi_data)
        if daily_yfi_data["last_price"] != "N/A":
            st.info(f"Successfully fetched daily prices for {symbol} from yfinance as Alpha Vantage fallback.", icon="✔️")
        else:
            # If both fail for daily, then we use mock data as final fallback
            st.warning(f"Failed to fetch daily prices from both Alpha Vantage and yfinance for {symbol}. Using mock data.", icon="❌")
            mock_data = get_mock_price_data(symbol, exchange)
            price_info.update(mock_data)


    # --- yfinance for 52-Week High/Low (always use yfinance for this) ---
    yfinance_symbol = symbol
    if exchange == "NSE":
        yfinance_symbol = f"{symbol}.NS"
    elif exchange == "BSE":
        yfinance_symbol = f"{symbol}.BO"
    
    time.sleep(1) # Small delay before yfinance call

    try:
        ticker = yf.Ticker(yfinance_symbol)
        hist = ticker.history(period="1y") 

        if not hist.empty:
            price_info["52week_high"] = hist['High'].max()
            price_info["52week_low"] = hist['Low'].min()
        else:
            st.warning(f"yfinance: No historical data found for {yfinance_symbol} in the last 52 weeks. Displaying N/A.", icon="📉")

    except Exception as e:
        st.error(f"Error fetching 52-week data for {yfinance_symbol} from yfinance: {e}. Using mock 52-week data.", icon="🚫")
        mock_52week_data = get_mock_price_data(symbol, exchange)
        price_info["52week_high"] = mock_52week_data["52week_high"]
        price_info["52week_low"] = mock_52week_data["52week_low"]

    return price_info


# -------------------- HEADER --------------------
st.markdown(
    """
    <div style="text-align:center">
      <h1 style="margin-bottom:0">📊 India Stock News Sentiment Screener</h1>
      <p style="color:gray;margin-top:6px">
        NSE & BSE stocks · Free Google News RSS · VADER Sentiment · Buy/Hold/Sell signals
      </p>
    </div>
    """,
    unsafe_allow_html=True
)

# Display data last processed time (server-side, updates on rerun)
data_processed_time_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
st.markdown(f"<p style='text-align:center; color:gray; font-size:small;'>Data last processed: {data_processed_time_str}</p>", unsafe_allow_html=True)

# Display real-running client-side clock
unique_clock_id = str(uuid.uuid4()).replace('-', '') # Generate a unique ID for the clock div and function
st.html(CLOCK_JS_TEMPLATE.format(clock_id=f"live-clock-{unique_clock_id}", unique_id=unique_clock_id))


# -------------------- HELPERS --------------------
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True) # Ensure the 'data' directory exists

def safe_lower(s):
    """Safely converts a value to lowercase string, handling NaN."""
    return str(s).strip().lower() if pd.notna(s) else ""

def load_symbol_file(path: str, expected_cols: List[str]) -> pd.DataFrame:
    """
    Loads stock symbols from a CSV or Excel file, flexibly mapping column names.
    
    Args:
        path (str): Path to the stock file (e.g., 'data/nse_stocks.csv').
        expected_cols (List[str]): A list of expected column names,
                                   can use '|' for alternatives (e.g., "symbol|scrip code").
                                   The first name in each alternative is used as the target column.
    Returns:
        pd.DataFrame: A DataFrame with standardized column names ("symbol", "name"),
                      or an empty DataFrame if the file cannot be loaded or columns not found.
    """
    if not os.path.exists(path):
        return pd.DataFrame() # Return empty if file does not exist

    df = pd.DataFrame()
    try:
        if path.endswith('.csv'):
            df = pd.read_csv(path)
        elif path.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(path)
        else:
            st.warning(f"Unsupported file format for {path}. Please use .csv or .xlsx.")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading file {path}: {e}. Please ensure it's a valid CSV or Excel.")
        return pd.DataFrame()
    
    out = pd.DataFrame()
    found_cols_map = {c.lower(): c for c in df.columns} # Map lowercase column names to actual names

    for want_spec in expected_cols:
        target_col_name = want_spec.split('|')[0].lower() # E.g., 'symbol' from 'symbol|stock_id'
        possible_source_names = [name.lower() for name in want_spec.split('|')]
        
        hit_actual_col = None
        
        # 1. Try exact lowercase match
        for p_name_lower in possible_source_names:
            if p_name_lower in found_cols_map:
                hit_actual_col = found_cols_map[p_name_lower]
                break
        
        # 2. If not found, try regex search for partial or case-insensitive matches
        if hit_actual_col is None:
            for p_name_lower in possible_source_names:
                for actual_df_col_name in df.columns:
                    # Use word boundary for more precise regex matching
                    if re.search(r'\b' + re.escape(p_name_lower) + r'\b', actual_df_col_name, flags=re.IGNORECASE):
                        hit_actual_col = actual_df_col_name
                        break
                if hit_actual_col:
                    break

        if hit_actual_col is not None:
            out[target_col_name] = df[hit_actual_col]
        else:
            st.warning(f"Could not find a column matching '{want_spec}' in {path}. "
                       f"Please ensure your file contains columns like '{' or '.join(want_spec.split('|'))}'.")

    return out


@st.cache_data(show_spinner=False)
def load_all_symbols() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Loads NSE and BSE stock lists, standardizing their column names to "SYMBOL" and "NAME".
    Returns (nse_df, bse_df).
    
    Expected CSV formats:
    nse_stocks.csv: Needs columns like "SYMBOL" and "NAME OF COMPANY" (or "NAME").
    bse_stocks.csv: Needs columns like "Security Id" (or "SCRIP CODE" or "SYMBOL")
                    and "Security Name" (or "NAME").
    """
    nse_raw = load_symbol_file(
        os.path.join(DATA_DIR, "nse_stocks.csv"),
        expected_cols=["symbol", "name of company|name"] # Target names will be 'symbol', 'name of company'
    )
    bse_raw = load_symbol_file(
        os.path.join(DATA_DIR, "bse_stocks.csv"),
        expected_cols=["security id|scrip code|symbol", "security name|name"] # Target names will be 'security id', 'security name'
    )

    nse = pd.DataFrame(columns=["SYMBOL", "NAME"])
    if not nse_raw.empty:
        # After load_symbol_file, columns are lowercase based on the first part of expected_cols
        sym_col = "symbol"
        name_col = "name of company" if "name of company" in nse_raw.columns else "name"
        
        if sym_col in nse_raw.columns and name_col in nse_raw.columns:
            nse["SYMBOL"] = nse_raw[sym_col].astype(str).str.strip()
            nse["NAME"] = nse_raw[name_col].astype(str).str.strip()
            nse = nse.dropna(subset=["SYMBOL", "NAME"]).drop_duplicates(subset=["SYMBOL"])
            st.sidebar.success(f"Loaded {len(nse)} NSE symbols.")
        else:
            st.sidebar.warning("NSE file loaded but required columns ('symbol', 'name of company' or 'name') not found or standardized correctly.")

    bse = pd.DataFrame(columns=["SYMBOL", "NAME"])
    if not bse_raw.empty:
        sym_col_candidates = ["security id", "scrip code", "symbol"] # Prioritize order
        sym_col = next((col for col in sym_col_candidates if col in bse_raw.columns), None)
        name_col = "security name" if "security name" in bse_raw.columns else "name"

        if sym_col and name_col and sym_col in bse_raw.columns and name_col in bse_raw.columns:
            bse["SYMBOL"] = bse_raw[sym_col].astype(str).str.strip()
            bse["NAME"] = bse_raw[name_col].astype(str).str.strip()
            bse = bse.dropna(subset=["SYMBOL", "NAME"]).drop_duplicates(subset=["SYMBOL"])
            st.sidebar.success(f"Loaded {len(bse)} BSE symbols.")
        else:
            st.sidebar.warning("BSE file loaded but required columns ('security id'/'scrip code'/'symbol', 'security name' or 'name') not found or standardized correctly.")

    return nse, bse


def google_news_rss_query(name_or_symbol: str) -> str:
    """
    Constructs a URL-encoded Google News RSS feed URL for a given stock.
    Uses quote_plus for robust URL encoding of the query parameter.
    """
    # Build a modest query; quotes often help with company names for exact match
    search_term = f'"{name_or_symbol}" stock'
    # quote_plus converts spaces to '+' and other special characters to %xx
    q = quote_plus(search_term) 
    
    base_url = f"https://news.google.com/rss/search?q={q}&hl=en-IN&gl=IN&ceid=IN:en"
    
    # Basic URL structure validation before attempting to fetch
    try:
        parsed_url = urlparse(base_url)
        if not all([parsed_url.scheme, parsed_url.netloc]):
            st.warning(f"Generated an invalid URL structure for '{name_or_symbol}': {base_url}")
            return ""
        # Additional check for control characters, though quote_plus should prevent it
        if re.search(r'[\x00-\x1F\x7F]', base_url): 
             st.warning(f"URL still contains control characters after encoding for '{name_or_symbol}': {base_url}")
             return ""

    except Exception as e:
        st.warning(f"Error validating URL for '{name_or_symbol}': {e} - {base_url}")
        return ""

    return base_url

# Initialize VADER sentiment analyzer
analyzer = SentimentIntensityAnalyzer()

def label_from_score(score: float) -> str:
    """Categorizes sentiment score into 'Positive', 'Negative', or 'Neutral'."""
    if score > 0.05:
        return "Positive"
    elif score < -0.05:
        return "Negative"
    return "Neutral"

def predict_signal(pos: int, neg: int) -> str:
    """Generates a simple Buy/Hold/Sell signal based on positive and negative headline counts."""
    if pos > neg:
        return "✅ Buy"
    if neg > pos:
        return "❌ Sell"
    return "⚖️ Hold"

# -------------------- SIDEBAR --------------------
st.sidebar.header("⚙️ Controls")

# Load stock symbols and display initial warnings/successes
nse_df, bse_df = load_all_symbols()

# Determine initial checkbox state based on whether data was loaded
initial_use_nse = not nse_df.empty
initial_use_bse = not bse_df.empty

# Handle case where no files are found, use a default watchlist
if nse_df.empty and bse_df.empty:
    st.sidebar.warning(
        "No NSE/BSE lists found. Add `data/nse_stocks.csv` and `data/bse_stocks.csv` for full coverage. "
        "Using a small default watchlist for now."
    )
    default_list = pd.DataFrame({
        "SYMBOL": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "SBIN", "LT", "ITC", "GAIL"],
        "NAME":   ["Reliance Industries", "Tata Consultancy Services", "Infosys", "HDFC Bank",
                   "ICICI Bank", "State Bank of India", "Larsen & Toubro", "ITC", "GAIL (India) Limited"],
        "EXCHANGE": ["NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE", "NSE"] # Default to NSE for consistency
    })
    nse_df = default_list.copy() # Assign default to NSE for selection purposes
    initial_use_nse = True # Automatically select NSE if using default list
    initial_use_bse = False # Ensure BSE is not selected by default if only default NSE is used

# Exchange selection checkboxes
use_nse = st.sidebar.checkbox("Use NSE List", value=initial_use_nse)
use_bse = st.sidebar.checkbox("Use BSE List", value=initial_use_bse)

# Build the universe of selected stocks
universe = pd.DataFrame(columns=["SYMBOL", "NAME", "EXCHANGE"])
if use_nse and not nse_df.empty:
    tmp = nse_df.copy()
    tmp["EXCHANGE"] = "NSE"
    universe = pd.concat([universe, tmp], ignore_index=True)
if use_bse and not bse_df.empty:
    tmp = bse_df.copy()
    tmp["EXCHANGE"] = "BSE"
    universe = pd.concat([universe, tmp], ignore_index=True)

# If no stocks are in the universe after selection, stop the app
if universe.empty:
    st.error("No stocks available for selection. Please check your data files or select at least one exchange in the sidebar.")
    st.stop()


# Prepare options for the multiselect widget
options_display = []
name_map = {}

if "NAME" in universe.columns and universe["NAME"].notna().any() and "SYMBOL" in universe.columns and "EXCHANGE" in universe.columns:
    for _, row in universe.iterrows():
        display_str = f"{row['NAME']} ({row['SYMBOL']} · {row['EXCHANGE']})"
        options_display.append(display_str)
        name_map[display_str] = (row['NAME'], row['SYMBOL'], row['EXCHANGE'])
elif "SYMBOL" in universe.columns and "EXCHANGE" in universe.columns: # Fallback if NAME is missing or all NaN
    for _, row in universe.iterrows():
        display_str = f"{row['SYMBOL']} ({row['EXCHANGE']})"
        options_display.append(display_str)
        name_map[display_str] = (row['SYMBOL'], row['SYMBOL'], row['EXCHANGE'])
else:
    st.error("Could not find 'SYMBOL' and 'EXCHANGE' columns in stock data. Please check your CSV/Excel files and ensure correct headers like 'SYMBOL' or 'Security Id'.")
    st.stop()

# Sort options for better user experience
options_display = sorted(options_display, key=lambda s: s.lower())

# Select Stocks multiselect widget
selected_display = st.sidebar.multiselect(
    "Select Stocks (search by name/symbol)",
    options=options_display,
    default=options_display[:min(5, len(options_display))] # Default to first 5, or fewer if not enough
)

# Sliders for configuration
limit_per_stock = st.sidebar.slider("Headlines per stock", 3, 20, 10, 1)
pause_ms = st.sidebar.slider("Fetch delay (ms, avoids rate-limit)", 0, 1000, 150, 50)

st.sidebar.markdown("---")
# New Auto-Refresh Checkbox
auto_refresh_enabled = st.sidebar.checkbox(f"Auto-refresh price data every {REFRESH_INTERVAL_SECONDS} seconds", value=False, 
                                           help=f"Automatically refreshes the entire page to fetch new price data from APIs every {REFRESH_INTERVAL_SECONDS} seconds.")
if st.sidebar.button("Clear Price Cache"):
    st.cache_data.clear()
    st.sidebar.success("Price data cache cleared!")
    st.rerun() # Rerun to reflect cleared cache and refetch new data
st.sidebar.markdown("---")

st.sidebar.markdown("**CSV setup (free):**")
st.sidebar.caption(
    "- Put NSE CSV at `data/nse_stocks.csv` (contains SYMBOL & NAME OF COMPANY)\n"
    "- Put BSE CSV at `data/bse_stocks.csv` (contains Security Id/Code & Security Name)\n"
    "Deploy to Streamlit Cloud: include these files in your repo."
)

# -------------------- DATA COLLECTION --------------------
all_rows: List[Dict] = []
if selected_display:
    progress_text = "Fetching headlines & analyzing sentiment..."
    my_bar = st.progress(0, text=progress_text) # Initialize progress bar
    
    for i, display in enumerate(selected_display):
        name, symbol, ex = name_map[display]
        query_term = name if name and name != symbol else symbol
        
        my_bar.progress((i + 1) / len(selected_display), text=f"Fetching news for {name} ({symbol})...")

        rss_url = google_news_rss_query(query_term)

        if pause_ms:
            time.sleep(pause_ms / 1000)

        if not rss_url: # Skip if URL generation failed (e.g., due to validation error)
            st.warning(f"Skipping {name} ({symbol}) due to invalid RSS URL generation.")
            continue

        try:
            # CRITICAL FIX: Use requests to fetch content, then feedparser to parse
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            # Fetch the content using requests
            response = requests.get(rss_url, timeout=10, headers=headers)
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            
            feed_content = response.text # Get the raw text content of the RSS feed
            # Pass the raw content to feedparser, bypassing its internal URL fetching
            feed = feedparser.parse(feed_content) 
            
            if feed.bozo: # Check for well-formedness of the XML
                st.warning(f"Error parsing RSS feed for {name} ({symbol}): {feed.bozo_exception}. Skipping.")
                st.info(f"Problematic RSS URL: `{rss_url}`")
                continue

            if not feed.entries:
                st.info(f"No headlines found for {name} ({symbol}) from Google News (URL: `{rss_url}`). "
                        "This could be due to no recent news, or Google News filtering. Skipping.")
                continue

            for entry in feed.entries[:limit_per_stock]:
                title = entry.get("title", "")
                if not title: # Skip entries without a title
                    continue
                score = analyzer.polarity_scores(title)["compound"]
                sentiment = label_from_score(score)
                all_rows.append({
                    "Stock": symbol,
                    "Name": name,
                    "Exchange": ex,
                    "Headline": title,
                    "Sentiment": sentiment,
                    "Score": score,
                    "Link": entry.get("link", "#") # Get the link to the news article
                })
        except requests.exceptions.Timeout:
            st.error(f"Request to Google News RSS for {name} ({symbol}) timed out after 10 seconds. URL: `{rss_url}`")
        except requests.exceptions.RequestException as e:
            st.error(f"Error fetching RSS feed for {name} ({symbol}): {e}. Check network connection or URL. URL: `{rss_url}`")
        except Exception as e:
            st.error(f"An unexpected error occurred while processing news for {name} ({symbol}): {e}")
            st.info(f"The problematic RSS URL was: `{rss_url}`")
            continue
    
    my_bar.empty() # Clear the progress bar when done

# -------------------- OUTPUT --------------------
if not all_rows:
    st.info("No headlines found yet. Try reducing your selection, pick well-known names, or check your stock list files. "
            "Ensure your `data/nse_stocks.csv` and `data/bse_stocks.csv` are correctly formatted.")
else:
    df = pd.DataFrame(all_rows)

    # ---------- Top Headlines Across Selection ----------
    st.markdown("## 🌟 Top Headlines Across Selection")
    # For mobile, it's better to stack these sections vertically.
    # Corrected: Use a single column object
    col_main_headlines = st.columns(1)[0] 
    
    with col_main_headlines: # Use the single column container
        st.markdown("### 🟢 Most Positive")
        top_pos = df[df["Sentiment"] == "Positive"].nlargest(5, "Score")
        if top_pos.empty:
            st.write("No strong positive headlines.")
        else:
            for _, r in top_pos.iterrows():
                st.markdown(f"- **{r['Name']} ({r['Stock']})** — [{r['Headline']}]({r['Link']})")

        # The second section will naturally appear below the first within the same column
        st.markdown("### 🔴 Most Negative")
        top_neg = df[df["Sentiment"] == "Negative"].nsmallest(5, "Score")
        if top_neg.empty:
            st.write("No strong negative headlines.")
        else:
            for _, r in top_neg.iterrows():
                st.markdown(f"- **{r['Name']} ({r['Stock']})** — [{r['Headline']}]({r['Link']})")

    # ---------- Per-Stock Sentiment & Signal ----------
    st.markdown("---")
    st.markdown("## 📊 Per-Stock Sentiment & Signal")

    summary_records = []
    # Group by all identifying columns for a robust summary
    for (sym, name, ex), g in df.groupby(["Stock", "Name", "Exchange"]):
        pos = (g["Sentiment"] == "Positive").sum()
        neg = (g["Sentiment"] == "Negative").sum()
        neu = (g["Sentiment"] == "Neutral").sum()
        avg = g["Score"].mean()
        signal = predict_signal(pos, neg)
        summary_records.append({
            "Stock": sym,
            "Name": name,
            "Exchange": ex,
            "Positive": pos,
            "Negative": neg,
            "Neutral": neu,
            "AvgScore": round(avg, 3),
            "Prediction": signal
        })

    summary_df = pd.DataFrame(summary_records).sort_values(["Prediction", "AvgScore"], ascending=[True, False])
    st.dataframe(summary_df, use_container_width=True) # use_container_width is good for responsiveness

    # ---------- Overall Market Sentiment ----------
    st.markdown("## 🌍 Overall Sentiment")
    total_pos = (df["Sentiment"] == "Positive").sum()
    total_neg = (df["Sentiment"] == "Negative").sum()
    total_neu = (df["Sentiment"] == "Neutral").sum()

    # Corrected: Use a single column object
    col_overall_sentiment = st.columns(1)[0]
    with col_overall_sentiment: 
        col_overall_sentiment.metric("Total Positive", total_pos)
        col_overall_sentiment.metric("Total Negative", total_neg)
        col_overall_sentiment.metric("Total Neutral", total_neu)

        # Re-evaluate the market message within the single column
        if total_pos > 0 or total_neg > 0:
            if total_pos > total_neg:
                mkt_msg = "📈 Market Sentiment: **Bullish** (tilt Buy)"
                col_overall_sentiment.success(mkt_msg) 
            elif total_neg > total_pos:
                mkt_msg = "📉 Market Sentiment: **Bearish** (tilt Sell/Avoid)"
                col_overall_sentiment.error(mkt_msg) 
            else:
                mkt_msg = "⚖️ Market Sentiment: **Neutral** (Wait & Watch)"
                col_overall_sentiment.warning(mkt_msg) 
        else:
            col_overall_sentiment.info("Not enough positive/negative news to determine overall market sentiment based on selected stocks.")


    # ---------- Visualizations (Charts) ----------
    st.markdown("## 📈 Visualizations")
    # Plotly charts are generally responsive and adapt well to container width
    # Per-stock bar chart for sentiment distribution
    bar_data = summary_df.melt(
        id_vars=["Stock", "Name", "Exchange", "Prediction", "AvgScore"],
        value_vars=["Positive", "Negative", "Neutral"],
        var_name="Sentiment",
        value_name="Count"
    )
    fig_bar = px.bar(
        bar_data, x="Stock", y="Count", color="Sentiment",
        hover_data={"Name":True, "Exchange":True, "Prediction":True, "AvgScore":":.3f", "Count":True},
        barmode="group", title="Sentiment Distribution per Stock"
    )
    st.plotly_chart(fig_bar, use_container_width=True)

    # Overall pie chart for sentiment share
    overall_counts = df["Sentiment"].value_counts().reset_index()
    overall_counts.columns = ["Sentiment", "Count"]
    fig_pie = px.pie(overall_counts, names="Sentiment", values="Count", title="Overall Sentiment Share")
    st.plotly_chart(fig_pie, use_container_width=True)

    # ---------- Detailed Headlines by Stock with Price Info ----------
    st.markdown("---")
    st.markdown("## 📰 Detailed Headlines by Stock & Price Info")
    
    # Indicate which APIs are being used
    api_status_messages = []
    if ALPHA_VANTAGE_API_KEY:
        api_status_messages.append("Alpha Vantage API (Daily Price)")
    api_status_messages.append("yfinance (52-Week Range - Unofficial)")

    if api_status_messages:
        st.info(f"Using: {', '.join(api_status_messages)}. (Prices refresh every {REFRESH_INTERVAL_SECONDS}s. Data may be delayed on free tiers; yfinance is unofficial).", icon="ℹ️")
    else:
        st.warning("No API keys configured. Using **MOCK DATA** for all stock price data.", icon="⚠️")

    for (sym, name, ex), g in df.groupby(["Stock", "Name", "Exchange"]):
        st.subheader(f"📌 {name} ({sym}) · {ex}")
        
        price_data = get_real_time_price_data(sym, ex) 

        # Adjusted to 2 columns for better mobile stacking (Last/DailyLow, DailyHigh/PriceUpdated)
        col1_p, col2_p = st.columns(2)
        with col1_p:
            st.metric("Last Price", price_data["last_price"])
        with col2_p:
            st.metric("Daily Low", price_data["today_low"])
        
        col3_p, col4_p = st.columns(2)
        with col3_p:
            st.metric("Daily High", price_data["today_high"])
        with col4_p:
            st.metric("Price Data Fetched At", price_data["last_updated"].strftime("%H:%M:%S") if isinstance(price_data["last_updated"], datetime) else price_data["last_updated"])
            
        st.info(f"**52 Week Range:** Low: {price_data['52week_low']:.2f}, High: {price_data['52week_high']:.2f}" 
                if isinstance(price_data['52week_low'], (float, int)) and isinstance(price_data['52week_high'], (float, int))
                else f"**52 Week Range:** Low: {price_data['52week_low']}, High: {price_data['52week_high']}")


        st.markdown("---") # Separator for headlines
        st.markdown(f"**Recent News Headlines for {name} ({sym}):**")
        for _, r in g.sort_values("Score", ascending=False).iterrows():
            emoji = "🟢" if r["Sentiment"] == "Positive" else ("🔴" if r["Sentiment"] == "Negative" else "🟡")
            st.markdown(f"- {emoji} **{r['Sentiment']}** — [{r['Headline']}]({r['Link']})")
        st.markdown("---")


# -------------------- FOOTER TIP --------------------
st.caption(
    "Tip: For full NSE/BSE coverage, add CSVs into the `data/` folder and redeploy. "
    "Google News RSS is free; headlines & tone may vary. Combine with your own price/risk rules."
)

# --- Auto-refresh mechanism ---
if auto_refresh_enabled:
    time.sleep(REFRESH_INTERVAL_SECONDS)
    st.rerun()