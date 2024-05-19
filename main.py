import telebot
import pandas as pd
import math
from datetime import datetime
import os
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import string
import calendar

bot = telebot.TeleBot('')

curr_dir = os.getcwd()

@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text == "/help":
        bot.send_message(message.from_user.id,
                         "I am designed to analyze telegram chat with 2 people.\
                        Just send me your json file!")
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

            try:
                # Parsing the json file
                df = read_df(file_name)

                # Sending info to the user
                bot.send_message(message.from_user.id, get_info_bot_v(df, message))

                # Preprocessing df
                cloud_df = preprocess_for_cloud(df)
                wordcloud_file = make_a_wordcloud(cloud_df)

                # Sending a wordcloud photo to the user
                with open(wordcloud_file, 'rb') as photo:
                    bot.send_photo(message.from_user.id, photo)

            except:
                bot.send_message(message.from_user.id, 'Something went wrong, try again later!')

            finally:
                # Deleting the downloaded files
                os.remove(file_name)
                os.remove(wordcloud_file)

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
    # to do: maybe replace unix_to_date() with built-in function
    date = datetime.fromtimestamp(int(value))
    # _ = date.strftime('%Y-%m-%d %H:%M:%S')
    normal_date = date.strftime('%d.%m.%Y')

    return normal_date


def get_info_bot_v(df, message):
    first_person_msg = len(df[df['from'] == first_person])
    second_person_msg = len(df[df['from'] == second_person])
    message = f"This story began on {start_date} and ended on {end_date}. \n"
    message += f"The amount of messages in {time_between} days is {len(df)}.\n"
    message += f"{first_person} has sent {first_person_msg} messages, which makes {round(100*first_person_msg/len(df))}%.\n"
    message += f"{second_person} has sent {second_person_msg} message, which makes {round(100*second_person_msg/len(df))}%."

    return message


def preprocess_for_cloud(df):
    # deleting empty messages
    cloud_df = df.drop(df[df['text'] == ""].index)
    cloud_df = cloud_df[cloud_df['text'].apply(lambda x: isinstance(x, str))] 
    cloud_df = cloud_df[cloud_df['forwarded_from'].isnull()]
    cloud_df = cloud_df.drop(['forwarded_from'], axis = 1)
    cloud_df['text'] = cloud_df['text'].apply(lambda x: x.lower())
    cloud_df['text'] = cloud_df['text'].apply(lambda x: x.strip())
    cloud_df.reset_index(drop=True, inplace=True)
    return cloud_df


def make_a_wordcloud(cloud_df, n=2):
    message_words = []
    m = 0
    while m < len(cloud_df):
        for word in (cloud_df['text'].iloc[m]).split():
            word = word.translate(str.maketrans('', '', string.punctuation))
            if len(word) > n:
                message_words.append(word)
            m += 1
             
    text_data = ' '.join(message_words)

    wordcloud = WordCloud(width=800, 
                          height=400, 
                          background_color='white').generate(text_data)
    phrase = f"Wordcloud for {first_person} and {second_person}\nWith words longer than {n} letters"

    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.text(0.5, 1.07, 
             phrase, ha='center', va='center', 
             fontsize=15, color='black', transform=plt.gca().transAxes)
    wordcloud_file = f"{curr_dir}/wordcloud_{first_person}_{second_person}.png"
    plt.savefig(wordcloud_file)

    return wordcloud_file


bot.polling(none_stop=True, interval=0)
