from yahooquery import Ticker

company = 'msft'
company = company.upper()
tickers = Ticker(company)

print(tickers.quotes[company]['shortName'])

# for i in tickers.quotes:
#     print(tickers.quotes['displayName'])