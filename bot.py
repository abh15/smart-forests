#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
A telegram Bot to keep track of split bills in a group

"""

import logging
import libfwi
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from influxdb import InfluxDBClient

my_dict={}
new_dic={}
user = ""
password = ""
dbname = "ruuvi1"
dbuser = ""
dbuser_password = ""
host='10.84.109.148'
port=8086
client = InfluxDBClient(host, port, user, password, dbname)

roovi_rev_locs={"Tjallmo":"F91E573C41F8","Hastveda":"CFFC1D652E98","Gnosjo":"F8A7DB587E2D","Ljusdal":"F0E9505C25A4","Norrkoping":"F47B8890C50A","Ronneby":"F26D5323ED83"} 


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

def getfwi(t_stamp,humidity,temp):
    fwi=libfwi.calcFWI(5,temp,humidity,10,0,85,6,15,60.20)  # Calulate FWI data assuming some constants
    #(month, temperature, relative humidity, wind speed, rain, previous FFMC, DMC, DC, and latitude)
    return fwi

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.


def start(bot, update):
    """Send a message when the command /start is issued."""
    update.message.reply_text('Hei!')
    update.message.reply_text('Tell me the desired location to get fire weather e.g /fwi Ljusdal')
    update.message.reply_text('Use /help to get list of more available locations')

def fwi(bot, update):   #Parse incoming string and send it to ledger updater func
        s=update.message.text
        print (s.split()[1])
        mac=roovi_rev_locs.get(s.split()[1])
        query = "select last(humidity),temperature, time from ruuvi_measurements where mac = "+"\'"+mac+"\'" #filter temp, humidity data across all ruuvitags
        result = client.query(query)
        cpu_points = list(result.get_points(measurement='ruuvi_measurements'))   #convert datatype to list
        for points in cpu_points:
            val= getfwi(points.get('time'),points.get('last'),points.get('temperature'))
            print(val)
        if 0<=val<=5:
            risk="Very low"
        elif 5<=val<=10:
            risk="Low"
        elif 10<=val<=20:
            risk="Medium"
        elif 20<=val<=30:
            risk="High"
        elif 30<=val:
            risk="Very high"
        else:
            risk="Error, check FWI value"
        update.message.reply_text("Latest FWI at "+s.split()[1]+" is "+str(val)+"\nRisk of fire is "+risk)
        #update.message.reply_text("Risk of fire is "+risk)     


def help(bot, update):
    """Send a message when the command /help is issued."""
    msg=str()
    msg +=    """  
        /start - Initialize Bot\n
        /fwi - Send place name to get fire weather e.g /fwi Tjallmo, /fwi Ljusdal,  /fwi Ljusdal,  /fwi Gnosjo,  /fwi Norrkoping
        
     """
     

    bot.send_message(chat_id=update.message.chat_id, text=msg,parse_mode="Markdown")
    #update.message.reply_text(text=msg)   


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    """Start the bot."""
    # Create the EventHandler and pass it your bot's token.
    updater = Updater("<your token here>")

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
 
    dp.add_handler(CommandHandler("fwi", fwi))
   
    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
