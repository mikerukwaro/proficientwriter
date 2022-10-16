import tkinter as tk
from threading import Thread
from tkinter.ttk import Button
from engine import proficient, get_provided_licence_details, get_computer_licence

proficient_scrapper = proficient()
def start_bot():
    global bot_running
    if not bot_running:
        print("Starting the bot")
        scrapper_thread = Thread(target=proficient_scrapper.run)
        scrapper_thread.start()
        bot_running = True
    else:
        print("Bot is already running")

def stop_bot():
    if bot_running:
        proficient_scrapper.terminate()


sweet_study = tk.Tk()
sweet_study.geometry('250x300')
sweet_study.title("proficient GUI")
bot_running = False
label = tk.Label(sweet_study, text='This is your licence')
label.pack(ipadx=10, ipady=10)
button = Button(sweet_study, text='Start', command=start_bot)
button.pack(side=tk.TOP, pady=5)
button_stop = Button(sweet_study, text='Stop', command=stop_bot)
button_stop.pack(side=tk.TOP, pady=5)
name_var = tk.StringVar()
sweet_study.mainloop()
