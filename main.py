import telebot
import pandas as pd
import math
from datetime import datetime
import os

bot = telebot.TeleBot('')


@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/help":
        bot.send_message(message.from_user.id,
                         "I am designed to analyze telegram chat with 2 people.\
                        Just send me your json file!")
    elif message.text:
        bot.send_message(message.from_user.id,
                         "Hi! Send me a json file \
                         containing exported data \
                         from a telegram chat (with only 2 interlocutors).")
    else:
        bot.send_message(message.from_user.id,
                         "Type /help")


@bot.message_handler(content_types=['document'])
def handle_document(message):
    # Checking if the message contains a document
    if message.document:
        file_info = bot.get_file(message.document.file_id)
        file_path = file_info.file_path
        file_extension = file_path.split('.')[-1]
        downloaded_file = bot.download_file(file_path)

        if file_extension.lower() == 'json':
            bot.send_message(message.from_user.id,
                             "Starting the script...")
            # Where to save the downloaded file
            file_name = 'downloaded_file.json'

            # Save the downloaded file
            with open(file_name, 'wb') as new_file:
                new_file.write(downloaded_file)

            # Parsing the json file
            df = read_df(file_name)
            # Sending info to the user
            get_info_bot_v(df, message)

            # Deleting the downloaded file
            os.remove(file_name)

        else:
            bot.send_message(message.from_user.id,
                             "Format is not json!")


def read_df(dataframe):
    df = pd.read_json(dataframe)
    df = pd.DataFrame(df['messages'].tolist())
    df = df[df['type'] == 'message']
    # Keeping only interesting columns 
    df = df[['id', 'type', 'date_unixtime',
            'from', 'from_id', 'text', 'forwarded_from']] 
    df.reset_index(drop=True, inplace=True)
    global first_person
    first_person = (list(df['from'].unique()))[0]
    global second_person
    second_person = (list(df['from'].unique()))[1]
    time_s = int(df['date_unixtime'].iloc[len(df)-1]) - int(df['date_unixtime'].iloc[0])
    global start_date, end_date, time_between
    time_between = math.ceil(time_s / 86400)
    start_date = unix_to_date(df['date_unixtime'].iloc[0])
    end_date = unix_to_date(df['date_unixtime'].iloc[len(df)-1])
    df['date'] = pd.to_datetime(df['date_unixtime'].astype(int), unit='s')

    return df


def unix_to_date(value):
    # to do: replace unix_to_date() with built-in function
    date = datetime.fromtimestamp(int(value))
    # _ = normal_date.strftime('%Y-%m-%d %H:%M:%S')
    normal_date = date.strftime('%d.%m.%Y')

    return normal_date


def get_info_bot_v(df, message):
    first_person_msg = len(df[df['from'] == first_person])
    second_person_msg = len(df[df['from'] == second_person])
    bot.send_message(message.from_user.id,
                     f"This story began on {start_date} and ended on {end_date}. \nThe amount of messages in {time_between} days is {len(df)}. \n{first_person} has sent {first_person_msg} messages, which makes {round(100*first_person_msg/len(df))}%.\n{second_person} has sent {second_person_msg} message, which makes {round(100*second_person_msg/len(df))}%.")


bot.polling(none_stop=True, interval=0)
