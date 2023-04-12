from customtkinter import *
from customtkinter import CTk
from tkinter import messagebox
from PIL import Image, UnidentifiedImageError
from yahooquery import Ticker
import requests
import re
import os


class BullBoard:
    def __init__(self):
        # sets values for error checking and color mode changing
        self.error_status = False
        self.color_mode = "dark"
        self.color_mode_icon_path = "light_mode_icon.png"

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
                 font=("Segoe UI", 18, "bold")).pack(pady=20)

        self.ticker_symbol_input = StringVar()
        ticker_symbol_entry = CTkEntry(
            self.root, width=80, font=("Segoe UI", 16), textvariable=self.ticker_symbol_input)
        ticker_symbol_entry.pack(padx=10)
        # focuses cursor to the text box to make the user experience more seamless
        ticker_symbol_entry.focus()

        CTkButton(self.root, text="Go", command=self.onButtonClick, font=("Segoe UI", 16, "bold"),
                  width=80).pack(padx=10, pady=3)
        # binds pressing "enter" to the button
        self.root.bind("<Return>", self.onButtonClick)

        # frame that contains the company name, stock price, and logo image labels
        self.mainframe = CTkFrame(
            self.root, width=300, height=150, fg_color="transparent")
        self.mainframe.pack()
        self.mainframe.pack_forget()

        self.company_name_label = StringVar()
        CTkLabel(self.mainframe, textvariable=self.company_name_label, font=("Segoe UI", 16)).grid(
            column=0, row=0, padx=10)

        self.company_name = StringVar()
        CTkLabel(self.mainframe, textvariable=self.company_name, font=("Segoe UI", 16)).grid(
            column=1, row=0, sticky=E, padx=10)

        self.stock_price_label = StringVar()
        CTkLabel(self.mainframe, textvariable=self.stock_price_label, font=("Segoe UI", 16)).grid(
            column=0, row=1, sticky=W, padx=10)

        self.stock_price = StringVar()
        CTkLabel(self.mainframe, textvariable=self.stock_price, font=("Segoe UI", 16)).grid(
            column=1, row=1, sticky=E, padx=10)

        self.image = CTkImage(Image.open('bullboard.png'), size=(128, 128))
        self.main_image = CTkLabel(self.root, text="", image=self.image)
        self.main_image.pack(pady=(50, 20))

        self.showColorModeButton()

        # initializes GUI
        self.root.mainloop()

    # method to display color mode change button
    def showColorModeButton(self):
        self.color_mode_icon = CTkImage(Image.open(
            self.color_mode_icon_path), size=(32, 32))
        self.color_mode_button = CTkButton(
            self.root, text="", command=self.changeColorMode, image=self.color_mode_icon, width=8, fg_color="transparent")
        self.color_mode_button.pack(anchor=E)

    # method to display question mark image in cases of error
    def setQuestionMarkImage(self):
        try:
            self.main_image.destroy()
        except:
            pass
        try:
            self.color_mode_button.destroy()
        except:
            pass

        self.image = CTkImage(Image.open("question_mark.png"), size=(128, 128))
        self.main_image = CTkLabel(self.mainframe, text="", image=self.image)
        self.main_image.grid(column=0, row=3, columnspan=2)

    # uses API to find and display name of company using inputted ticker symbol. returns errors in cases of non-existant ticker symbols or the DJIA (not currently supported).
    def getCompanyName(self):
        self.ticker_symbol = str(self.ticker_symbol_input.get())
        self.company = Ticker(self.ticker_symbol)

        b = 1
        if self.ticker_symbol == "":
            b = 0

        try:
            1 / b
            self.mainframe.pack(pady=20)

            self.company_website = self.company.asset_profile[self.ticker_symbol]["website"]

            match = re.search(
                r"(?<=\/\/)(www\.)?([^\/]+)\.([^\/]+)", self.company_website)
            self.company_website = match.group(2) + '.' + match.group(3)

            try:
                self.name = self.company.quotes[self.ticker_symbol.upper(
                )]['displayName']
            except:
                self.name = self.company.quotes[self.ticker_symbol.upper(
                )]['shortName']

            x = 240 + 8 * len(self.name)
            self.root.geometry(f"{x}x420")

            self.company_name.set(self.name)
            self.company_name_label.set("Showing information for: ")
        except ZeroDivisionError:
            self.root.geometry("300x175")
            self.setQuestionMarkImage()
            self.showColorModeButton()
            messagebox.showinfo(
                "Error", "Please enter a ticker symbol.")
            self.error_status = True
        except KeyError:
            self.root.geometry("300x400")
            self.setQuestionMarkImage()
            self.showColorModeButton()
            messagebox.showinfo(
                "Error", "The Dow Jones Industrial Average is not currently supported :(")
            self.error_status = True
        except TypeError:
            self.root.geometry("300x400")
            self.setQuestionMarkImage()
            self.showColorModeButton()
            messagebox.showinfo("Error", "Ticker symbol not found.")
            self.error_status = True

    # uses API to find and display the stock price of company using inputted ticker symbol. displays nothing in cases of error.
    def getStockPrice(self):
        stock_price = self.company.summary_detail[self.ticker_symbol]['open']
        stock_price = str(round(float(stock_price), 2))
        self.stock_price.set(f"${stock_price}")
        self.stock_price_label.set("Opening price per share: ")

    # uses API to find and display the logo of company using inputted ticker symbol. displays an image of a question mark in cases of error.
    def getCompanyLogo(self):
        try:
            try:
                self.main_image.destroy()
            except:
                pass

            try:
                self.color_mode_button.destroy()
            except:
                pass

            response = requests.get(
                f'https://logo.uplead.com/{self.company_website}')
            with open("company_logo.png", 'wb') as f:
                f.write(response.content)

            Image.open('company_logo.png').resize(
                (128, 128)).save('company_logo.png')

            self.image = CTkImage(Image.open(
                'company_logo.png'), size=(128, 128))
            self.main_image = CTkLabel(
                self.mainframe, text="", image=self.image)
            self.main_image.grid(column=0, row=3, columnspan=2, pady=(20, 0))

            self.showColorModeButton()
            os.remove('company_logo.png')
        except (IndexError, KeyError):
            self.setQuestionMarkImage()
        except UnidentifiedImageError:
            self.root.geometry("300x270")
            self.showColorModeButton()

    # method to change GUI if user wants to change the color mode (light/dark)
    def changeColorMode(self):
        if self.color_mode == "dark":
            self.color_mode = 'light'
            set_appearance_mode(self.color_mode)
            self.color_mode_button.destroy()
            self.color_mode_icon_path = 'dark_mode_icon.png'
            self.showColorModeButton()
        elif self.color_mode == "light":
            self.color_mode = 'dark'
            set_appearance_mode(self.color_mode)
            self.color_mode_button.destroy()
            self.color_mode_icon_path = 'light_mode_icon.png'
            self.showColorModeButton()

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

        try:
            os.remove('company_logo.png')
        except:
            pass


BullBoard()
