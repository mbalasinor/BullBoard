from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from PIL import Image
from dotenv import load_dotenv
import requests
import os


class BullBoard:
    def __init__(self):
        load_dotenv()

        # defines headers for api usage
        self.api_headers = {
            "X-RapidAPI-Key": os.getenv('X-RapidAPI-Key'),
            "X-RapidAPI-Host": "twelve-data1.p.rapidapi.com"
        }

        self.error_status = False

        # initializes GUI
        self.root = Tk()
        self.root.geometry("300x300")
        self.root.title("BullBoard")

        # creates and positions all visual elements of GUI
        ttk.Label(self.root, text="Please enter a ticker symbol:",
                  font=("Segoe UI", 9)).pack(pady=10)

        self.ticker_symbol = StringVar()
        ticker_symbol_entry = ttk.Entry(
            self.root, width=10, textvariable=self.ticker_symbol)
        ticker_symbol_entry.pack(padx=10)
        # focuses cursor to the text box to make the user experience more seamless
        ticker_symbol_entry.focus()

        ttk.Button(self.root, text="Go", command=self.onButtonClick,
                   width=10).pack(padx=10)
        # binds pressing "enter" to the button
        self.root.bind("<Return>", self.onButtonClick)

        # frame that contains the company name, stock price, and logo image labels
        self.mainframe = Frame(self.root)
        self.mainframe.pack(pady=10)

        self.company_name_label = StringVar()
        ttk.Label(self.mainframe, textvariable=self.company_name_label).grid(
            column=0, row=0)

        self.company_name = StringVar()
        ttk.Label(self.mainframe, textvariable=self.company_name).grid(
            column=1, row=0, sticky=E)

        self.stock_price_label = StringVar()
        ttk.Label(self.mainframe, textvariable=self.stock_price_label).grid(
            column=0, row=1, sticky=W)

        self.stock_price = StringVar()
        ttk.Label(self.mainframe, textvariable=self.stock_price).grid(
            column=1, row=1, sticky=E)

        self.image = PhotoImage(file='bullboard.png')
        main_image = ttk.Label(self.mainframe, image=self.image)
        main_image.grid(column=0, row=2)

        # initializes GUI
        self.root.mainloop()

    # method to
    def setQuestionMark(self):
        self.image = PhotoImage(file='question_mark.png')
        main_image = ttk.Label(self.mainframe, image=self.image)
        main_image.grid(column=0, row=3, columnspan=2)

    # uses API to find and display name of company using inputted ticker symbol. returns errors based on api rate limits and non-existant ticker symbols, respectively.
    def getCompanyName(self):
        ticker_symbol = str(self.ticker_symbol.get())

        company_name_url = "https://twelve-data1.p.rapidapi.com/stocks"
        querystring = {"exchange": "NASDAQ",
                       "symbol": ticker_symbol, "format": "json"}

        try:
            company_name = requests.request(
                "GET", company_name_url, headers=self.api_headers, params=querystring).json()
            self.company_name.set(company_name['data'][0]['name'])
            self.company_name_label.set("Showing information for: ")
        except KeyError:
            self.setQuestionMark()
            messagebox.showinfo(
                "Error", "On cooldown, please try again later.")
            self.error_status = True
        except IndexError:
            self.setQuestionMark()
            messagebox.showinfo("Error", "Ticker symbol not found.")
            self.error_status = True

    # uses API to find and display the stock price of company using inputted ticker symbol. displays nothing in cases of error.
    def getStockPrice(self):
        ticker_symbol = str(self.ticker_symbol.get())
        stock_price_url = "https://twelve-data1.p.rapidapi.com/price"
        querystring = {"symbol": ticker_symbol}
        try:
            stock_price = requests.request(
                "GET", stock_price_url, headers=self.api_headers, params=querystring).json()
            stock_price = str(round(float(stock_price['price']), 2))
            self.stock_price.set(f"${stock_price}")
            self.stock_price_label.set("Latest price per share: ")
        except:
            self.stock_price.set("")

    # uses API to find and display the logo of company using inputted ticker symbol. displays an image of a question mark in cases of error.
    def getCompanyLogo(self):
        ticker_symbol = str(self.ticker_symbol.get())

        url = "https://twelve-data1.p.rapidapi.com/logo"
        querystring = {"symbol": ticker_symbol}

        try:  # first block gets logo image link with API, second block saves image locally, third block displays the image in the program and deletes it locally
            company_logo_url = requests.request(
                "GET", url, headers=self.api_headers, params=querystring).json()
            company_logo_url = company_logo_url['url']

            response = requests.get(company_logo_url)
            with open("company_logo.png", 'wb') as f:
                f.write(response.content)

            Image.open('company_logo.png').resize(
                (128, 128)).save('company_logo.png')

            self.image = PhotoImage(file='company_logo.png')
            main_image = ttk.Label(self.mainframe, image=self.image)
            main_image.grid(column=0, row=3, columnspan=2)

            os.remove('company_logo.png')
        except (IndexError, KeyError):
            self.setQuestionMark()

    # method that calls all other methods of the program when the user presses the button.
    def onButtonClick(self, event=None):
        self.error_status = False

        self.company_name_label.set("")
        self.company_name.set("")
        self.stock_price_label.set("")
        self.stock_price.set("")

        while True:
            self.getCompanyName()
            if self.error_status == True:
                break
            self.getStockPrice()
            self.getCompanyLogo()
            break


BullBoard()
