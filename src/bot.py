from telebot import types, TeleBot
import os
from dao import DAO
from cachetools import TTLCache
from database_updater import DatabaseUpdater
import traceback
import logging

CATEGORY_ID = 'category_id'
CITY_ID = 'city_id'
NEIGHBORHOOD_ID = 'neighborhood_id'

logging.basicConfig(level=logging.INFO)

class BOT:
    def __init__(self, token):
        self.bot = TeleBot(token)
        self.user_data = TTLCache(maxsize=1024, ttl=30)
        self.db_dao = DAO()
        self.db_updater = DatabaseUpdater()
        self.register_handlers()
        
    def handle_error(self, chat_id, error, message):
        traceback.print_exc()
        logging.error(f"Error: {error}")
        self.bot.send_message(chat_id, message)    
        
    def set_user_data(self, chat_id):
        self.user_data[chat_id] = {CATEGORY_ID: None, CITY_ID: None, NEIGHBORHOOD_ID: None}    

    def set_user_category(self, chat_id, category_id):
        self.user_data[chat_id][CATEGORY_ID] = category_id 
    
    def set_user_city(self, chat_id, city_id):
        self.user_data[chat_id][CITY_ID] = city_id         
    
    def set_user_neighborhood(self, chat_id, neighborhood_id):
        self.user_data[chat_id][NEIGHBORHOOD_ID] = neighborhood_id
    
    def get_user_data(self, chat_id, data_id):
        return self.user_data[chat_id][data_id]        
            
    def register_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.set_user_data(message.chat.id)
            self.bot.reply_to(message, "Benvenuto nel bot per la guida dei posti provati da Franchino Er Criminale. \nQuesto bot ti guiderà nella ricerca dei locali attravero tre fasi: categorie, citta, quartiere. Clicca su /categorie per iniziare")

        @self.bot.message_handler(commands=['categorie'])
        def categories_command(message):
            markup = types.InlineKeyboardMarkup(row_width=2)
            button1 = types.InlineKeyboardButton('Gelaterie', callback_data='1')
            button2 = types.InlineKeyboardButton('Forni', callback_data='2')
            button3 = types.InlineKeyboardButton('Rosticcerie', callback_data='3')
            button4 = types.InlineKeyboardButton('Panini', callback_data='4')
            markup.add(button1, button2, button3, button4)
            self.bot.send_message(message.chat.id, 'Scegli la categoria criminale di interesse:', reply_markup=markup)  

        @self.bot.callback_query_handler(func=lambda call: True)
        def callback_query(call):
            msg = ''
            if call.data == '1':
                msg += 'Hai selezionato Gelaterie.'
            elif call.data == '2':
                msg += 'Hai selezionato Forni.'
            elif call.data == '3':
                msg += 'Hai selezionato Rosticcerie.'
            elif call.data == '4':
                msg += 'Hai selezionato Panini.'
            self.user_data[call.message.chat.id][CATEGORY_ID] = call.data  
            self.bot.send_message(call.message.chat.id, msg+' Ora clicca su /citta')    

        @self.bot.message_handler(commands=['citta'])
        def city_command(message):
            sent_msg = self.bot.send_message(message.chat.id, "Inserisci la città di interesse:")
            self.bot.register_next_step_handler(sent_msg, city_handler)

        def city_handler(message):
            city = message.text
            try:
                foundCity = self.db_dao.find_city(city)
                if foundCity is not None:
                    self.set_user_city(message.chat.id, foundCity.id)
                    self.bot.send_message(message.chat.id, f"Hai inserito: {city}. Ora clicca /quartiere")
                else:
                    self.bot.send_message(message.chat.id, 'Nessuna città presente... riprova /citta') 
            except KeyError as ke:
                self.handle_error(message.chat.id, ke, 'Dati inconsistenti, forse è passato troppo tempo o hai saltato un passaggio... riprova ricominciando da /start')
            except Exception as e:
                self.handle_error(message.chat.id, e, 'Si è verificato un errore... riprova /start') 

        @self.bot.message_handler(commands=['quartiere'])
        def neighborhood_command(message):
            sent_msg = self.bot.send_message(message.chat.id, "Inserisci il quartiere di interesse")
            self.bot.register_next_step_handler(sent_msg, neighborhood_handler)

        def neighborhood_handler(message):
            neighborhood = message.text
            try:
                city_id = self.get_user_data(message.chat.id, CITY_ID)
                foundNeighborhood = self.db_dao.find_neighborhood(neighborhood, city_id)
                if foundNeighborhood is not None:
                    self.set_user_neighborhood(message.chat.id, foundNeighborhood.id)
                    self.bot.send_message(message.chat.id, f"Hai inserito: {neighborhood}.\nOra clicca /risultati per avere la lista dei locali relativi alle tue scelte, ordinati per voto")  
                else:
                    self.bot.send_message(message.chat.id, 'Non è stato trovato alcun quartiere... \nriprova /quartiere')   
            except KeyError as ke:
                self.handle_error(message.chat.id, ke, 'Dati inconsistenti, forse è passato troppo tempo o hai saltato un passaggio... riprova ricominciando da /start')
            except Exception as e:
                self.handle_error(message.chat.id, e, 'Si è verificato un errore... riprova /start')   

        @self.bot.message_handler(commands=['risultati'])
        def result_command(message):
            cat_id = None
            nei_id = None
            msg_result = ''
            stores = []
            try:
                cat_id = self.get_user_data(message.chat.id, CATEGORY_ID)
                nei_id = self.get_user_data(message.chat.id, NEIGHBORHOOD_ID)
            except Exception as e:
                self.bot.send_message(message.chat.id, 'Dati inconsistenti, forse è passato troppo tempo o hai saltato un passaggio... riprova ricominciando da /start')
                return
            stores = self.db_dao.get_stores(nei_id, cat_id)
            if len(stores) == 0:
                del self.user_data[message.chat.id]
                self.bot.send_message(message.chat.id, 'Non ci sono risultati per la tua ricerca... riprova ricominciando da /start')
                return
            for store in stores:
                msg_result += f"{store.name}\nin {store.address} con voto: {store.vote}{' pieno' if store.full_vote else ''}\n"
                if store.comment and store.comment.strip() and store.comment != 'NaN':
                  msg_result += f"Commento: {store.comment}\n"
                msg_result += "\n\n"
            msg_result += "Se vuoi fare un'altra ricerca, ricomincia da /start"    
            self.user_data.pop(message.chat.id)
            self.bot.send_message(message.chat.id, msg_result)

    def run(self):
        self.db_updater.pre_populateDB()
        self.bot.polling()

if __name__ == '__main__':
    token = os.getenv('BOT_TOKEN')
    if token:
        bot_instance = BOT(token)
        bot_instance.run()
    else:
        print("BOT_TOKEN environment variable not set.")

