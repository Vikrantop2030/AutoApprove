from os import getenv

from dotenv import load_dotenv

#Necessary Variables 
API_ID = int(getenv("API_ID", 29400566))
API_HASH = getenv("API_HASH", "8fd30dc496aea7c14cf675f59b74ec6f")
BOT_TOKEN = getenv("BOT_TOKEN") #Put your bot token here
# CHANNEL = getenv("CHANNEL", "ZenBotX") #Your public channel username without @ for force subscription.
MONGO = getenv("MONGO") #Put mongo db url here
#Optional Variables
DELAY = int(getenv("DELAY", 5)) #Delay in secondsbefore join request should be accepted default to 5 seconds. Enter 0 to disable it
OWNER_ID = int(getenv("OWNER_ID", 1344569458)) 
FSUB = bool(getenv("FSUB", False)) #Set this True if you want to enable force subscription from users else set to False.
CHANNEL_ID = int(getenv("Channel_ID")) #Id of channel from where you want to automatically broadcast messages
SESSION = getenv("SESSION", False) #Telegram string session optional though
START_PIC = getenv("START_PIC", "https://i.ibb.co/87q5Ccy/Saccept.jpg")