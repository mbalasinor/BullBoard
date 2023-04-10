from customtkinter import *
from customtkinter import CTk
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
        self.color_mode = "dark"

        # initializes GUI
        self.root = CTk()
        self.root.geometry("300x375")
        self.root.title("BullBoard")

        set_appearance_mode(self.color_mode)
        set_default_color_theme("blue")
        set_widget_scaling(1)
        set_window_scaling(1)

        # creates and positions all visual elements of GUI
        CTkLabel(self.root, text="Please enter a ticker symbol:",
                 font=("Segoe UI", 16)).pack(pady=20)

        self.ticker_symbol = StringVar()
        ticker_symbol_entry = CTkEntry(
            self.root, width=60, font=("Segoe UI", 14), textvariable=self.ticker_symbol)
        ticker_symbol_entry.pack(padx=10)
        # focuses cursor to the text box to make the user experience more seamless
        ticker_symbol_entry.focus()

        CTkButton(self.root, text="Go", command=self.onButtonClick, font=("Segoe UI", 14),
                  width=60).pack(padx=10, pady=2)
        # binds pressing "enter" to the button
        self.root.bind("<Return>", self.onButtonClick)

        # frame that contains the company name, stock price, and logo image labels
        self.mainframe = CTkFrame(self.root, width=300, height=150, fg_color="transparent")
        self.mainframe.pack()
        self.mainframe.pack_forget()

        self.company_name_label = StringVar()
        CTkLabel(self.mainframe, textvariable=self.company_name_label, font=("Segoe UI", 14)).grid(
            column=0, row=0, padx=10)

        self.company_name = StringVar()
        CTkLabel(self.mainframe, textvariable=self.company_name, font=("Segoe UI", 14)).grid(
            column=1, row=0, sticky=E, padx=10)

        self.stock_price_label = StringVar()
        CTkLabel(self.mainframe, textvariable=self.stock_price_label, font=("Segoe UI", 14)).grid(
            column=0, row=1, sticky=W, padx=10)

        self.stock_price = StringVar()
        CTkLabel(self.mainframe, textvariable=self.stock_price, font=("Segoe UI", 14)).grid(
            column=1, row=1, sticky=E, padx=10)

        self.image = CTkImage(Image.open('bullboard.png'), size=(128, 128))
        self.main_image = CTkLabel(self.root, text="", image=self.image)
        self.main_image.pack(pady=(50,20))

        self.showColorModeButton()

        # initializes GUI
        self.root.mainloop()

    def showColorModeButton(self):
        self.color_mode_icon = CTkImage(Image.open('light_mode_icon.png'), size=(32, 32))
        self.color_mode_button = CTkButton(self.root, text="", image=self.color_mode_icon, width=8, fg_color="transparent")
        self.color_mode_button.pack(anchor=E)

    # method to
    def setQuestionMark(self):
        self.image = CTkImage(Image.open('question_mark.png'), size=(128, 128))
        self.main_image = CTkLabel(self.mainframe, text="", image=self.image)
        self.main_image.grid(column=0, row=3, columnspan=2)

    # uses API to find and display name of company using inputted ticker symbol. returns errors based on api rate limits and non-existant ticker symbols, respectively.
    def getCompanyName(self):
        ticker_symbol = str(self.ticker_symbol.get())

        company_name_url = "https://twelve-data1.p.rapidapi.com/stocks"
        querystring = {"exchange": "NASDAQ",
                       "symbol": ticker_symbol, "format": "json"}

        try:
            self.main_image.destroy()
            self.color_mode_button.destroy()
            self.root.geometry("300x420")
            self.mainframe.pack(pady=20)
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

            self.image = CTkImage(Image.open(
                'company_logo.png'), size=(128, 128))
            self.main_image = CTkLabel(
                self.mainframe, text="", image=self.image)
            self.main_image.grid(column=0, row=3, columnspan=2, pady=(20,0))

            self.showColorModeButton()
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
