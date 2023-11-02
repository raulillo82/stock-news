import requests
from auth import *

STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
THRESHOLD = 5

def get_price_increase(ticker):
    """Returns the price increase % of the stock represented by the ticker
    between the dates of yesterday and the day before, both at the end of the
    day
    """
    url = "https://www.alphavantage.co/query"
    params = {
        #"function": "GLOBAL_QUOTE",
        "function": "TIME_SERIES_DAILY",
        "symbol": ticker,
        "apikey": APIKEY_ALPHAVANTAGE,
        }
    response = requests.get(url=url, params=params)
    response.raise_for_status()
    data = response.json()
    #print(data)

    #Despite the "raise_for_status()", there is still an empty response when 25 hits
    #per day are exceeded. This will be handled in a try-catch block
    try:
        #price_yesterday = float(data["Time Series (Daily)"][yesterday]["4. close"])
        #price_day_before_yesterday = float(data["Time Series (Daily)"][day_before_yesterday]["4. close"])
        #increment_percentage = float("{:.2f}".format((price_day_before_yesterday-price_yesterday) * 100 / price_day_before_yesterday))

        prices_list = [value for (key, value) in data["Time Series (Daily)"].items()]
        price_yesterday = float(prices_list[0]["4. close"])
        price_day_before_yesterday = float(prices_list[1]["4. close"])
        increment_percentage = float("{:.2f}".format((price_day_before_yesterday-price_yesterday) * 100 / price_day_before_yesterday))

        #Probly easier to do using "GLOBAL_QUOTE" with this line instead of the
        #previous block:
        #increment_percentage = float(data["Global Quote"].strip("%"))/100

    except KeyError:
        print("No relevant stock info retrieved, probably exceeded the 25 hits per day limit")
        print("Will make up an imaginary increase percentage of 5.01%")
        #should probably exit at this point, but for the sake of testing will
        #continue the program with fake data
        #exit(1)
        increment_percentage = 5.01

    return increment_percentage

def get_news(company):
    """Uses the API from newsapi to fetch news about "company"
    Returns a list of dictionaries
    """
    url = "https://newsapi.org/v2/everything"
    params = {
            "qInTitle": company,
            "sortBy": "popularity",
            "apiKey": APIKEY_NEWSAPI,
            }

    response = requests.get(url=url, params=params)
    response.raise_for_status()

    data = response.json()["articles"][:3]
    return data

def news_entry_to_string(news):
    """Converts the list of dictionaries passed as parameters into a string
    with the desired format, which is then returned"""
    message = ""
    for news_entry in news:
        message += f"*Headline:* {news_entry['title']}"
        message += "\n"
        message += f"*Brief:* {news_entry['description']}"
        message += "\n\n"
    return message

def telegram_bot_sendtext(bot_message):
    """Sends the text message passed as parameter to the telegram bot.
    Returns the response code"""
    params = {
            "chat_id": bot_chatID,
            "text": bot_message,
            "parse_mode": "MARKDOWN",
            }
    url = "https://api.telegram.org/bot" + bot_token + "/sendMessage"
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

#Main program start
price_increase = get_price_increase(STOCK)
if abs(price_increase) > THRESHOLD:
    if price_increase >= 0:
        symbol = "🔺"
    else:
        symbol = "🔻"
    news_summary = f"{STOCK}: {symbol}{price_increase}%" + "\n" + news_entry_to_string(get_news(COMPANY_NAME))
    test = telegram_bot_sendtext(news_summary)
    #print(test)
