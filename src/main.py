import re
import json
import config
import cache_db
from autoria_scraper import autoria_scraping
from olx_scraper import olx_scraping
from rst_scraper import rst_scraping
from calculator import calculating
import telebot
from telebot import types

bot = telebot.TeleBot("YOUR-TELEBOT-TOKEN")
user_status = {}
previous_user_status = {}
info = [0, 0, 0, 0, 0]

# We load car models and area data from JSON files
with open("D:/Python/Selenium_lessons/data/car_models.json", "r", encoding="utf-8") as file:
    car_models = json.load(file)

with open("D:/Python/Selenium_lessons/data/area.json", "r", encoding="utf-8") as file:
    area_dict = json.load(file)


@bot.message_handler(commands=["start"])
def start_command_handler(message):
    previous_user_status[message.chat.id] = None
    user_status[message.chat.id] = "awaiting_car_brand"
    bot.send_message(message.chat.id, "Вкажіть назву автомобільного бренду.")
    bot.register_next_step_handler(message, car_brand_message_handler)


def create_reply_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Назад ⬅️")
    markup.add(back_button)
    return markup


def clear_previous_step_handlers(message):
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)


@bot.message_handler(func=lambda message: message.text == "Назад ⬅️")
def handle_back_button(message):
    previous_status = previous_user_status.get(message.chat.id)
    clear_previous_step_handlers(message)
    if previous_status:
        user_status[message.chat.id] = previous_status
        fake_call = types.CallbackQuery(
            id=message.message_id,
            from_user=message.from_user,
            data="",
            chat_instance=message.chat.id,
            message=message,
            json_string={}
        )
        clear_previous_step_handlers(message)
        if previous_status == "awaiting_car_brand":
            info[0] = 0
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            bot.send_message(message.chat.id, "Вкажіть назву автомобільного бренду.")
            start_command_handler(message)
        elif previous_status == "awaiting_car_model":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            bot.send_message(message.chat.id, "Супер! Тепер мені потрібна модель, яка вас цікавить.",
                             reply_markup=create_reply_keyboard())
            info[1] = 0
            car_model_message_handler(message)
        elif previous_status == "the_main_parameters_are_entered":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            bot.send_message(message.chat.id, "Обов'язкові параметри. Але ви можете звузити діапазон пошуку!",
                             reply_markup=create_reply_keyboard())
            additional_parameters_handler(message)
        elif previous_status == "awaiting_area_selection":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            info[2] = 0
            area_selection_callback_handler(fake_call)
        elif previous_status == "awaiting_city_selection":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            region_selection_callback_handler(fake_call)
        elif previous_status == "awaiting_min_value":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            info[3] = 0
            interval_selection_handler(message)
        elif previous_status == "awaiting_max_value":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            bot.send_message(message.chat.id, "Вкажіть дату кінця випуску!", reply_markup=create_reply_keyboard())
            max_value_message_handler(message)
        elif previous_status == "awaiting_currency":
            bot.send_message(message.chat.id, "Ви повернулися до попереднього етапу.")
            info[4] = 0
            currency_selection_handler(message)
    else:
        bot.send_message(message.chat.id, "Ви знаходитесь на початковому етапі.")
        start_command_handler(message)


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'awaiting_car_brand')
def car_brand_message_handler(message):
    user_brand = message.text.lower()

    if user_brand.strip() in car_models.keys():
        info[0] = user_brand.strip()
        previous_user_status[message.chat.id] = user_status[message.chat.id]
        user_status[message.chat.id] = "awaiting_car_model"
        bot.send_message(message.chat.id, "Супер! Тепер мені потрібна модель, яка вас цікавить.",
                         reply_markup=create_reply_keyboard())
        bot.register_next_step_handler(message, car_model_message_handler)
    else:
        if user_brand.strip() == "/start":
            return start_command_handler(message)
        elif user_brand.strip() == "назад ⬅️":
            bot.send_message(message.chat.id,
                             "Це початковий етап!")
        else:
            bot.send_message(message.chat.id,
                             "Я не знаю такої марки.\nПеревірте чи назва вказана коректно та спробуйте ще раз.")
        user_status[message.chat.id] = "awaiting_car_brand"


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == "awaiting_car_model")
def car_model_message_handler(message):
    user_model = message.text.lower()

    if user_model.strip() in car_models[info[0]]:
        info[1] = user_model.strip()
        previous_user_status[message.chat.id] = user_status[message.chat.id]
        user_status[message.chat.id] = "the_main_parameters_are_entered"
        bot.send_message(message.chat.id, "Обов'язкові параметри отримано. Але ви можете звузити діапазон пошуку!",
                         reply_markup=create_reply_keyboard())
        additional_parameters_handler(message)
    elif user_model.strip() == "/start":
        return start_command_handler(message)
    elif user_model.strip() == "назад ⬅️":
        user_status[message.chat.id] = previous_user_status[message.chat.id]
    else:
        bot.send_message(message.chat.id,
                         f"Я не знаю такої моделі від бренду {info[0].upper()}.\nПеревірте чи назва вказанакоректно та спробуйте ще раз.")
        previous_user_status[message.chat.id] = user_status[message.chat.id]
        user_status[message.chat.id] = "awaiting_car_model"


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == "the_main_parameters_are_entered")
def additional_parameters_handler(message):
    markup = types.InlineKeyboardMarkup()
    but1 = types.InlineKeyboardButton("Додати регіон", callback_data="add_area")
    but2 = types.InlineKeyboardButton("Додати роки випуску", callback_data="add_interval")
    but3 = types.InlineKeyboardButton("Почнімо!", callback_data="start_search")
    markup.add(but1, but2, but3, row_width=2)

    bot.send_message(message.chat.id, "Додайте параметри пошуку(якщо бажаєте) або почнімо!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data in ["add_area", "add_interval", "start_search"])
def additional_parameters_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    if call.data == "add_area":
        previous_user_status[call.message.chat.id] = user_status[call.message.chat.id]
        user_status[call.message.chat.id] = "awaiting_area_selection"
        area_selection_callback_handler(call)
    elif call.data == "add_interval":
        previous_user_status[call.message.chat.id] = user_status[call.message.chat.id]
        user_status[call.message.chat.id] = "awaiting_interval_filter"
        interval_selection_handler(call.message)
    else:
        currency_selection_handler(call)


def area_selection_callback_handler(call):
    if call.message.text.strip() == "/start":
        return start_command_handler(call.message)
    markup = types.InlineKeyboardMarkup()
    for region in area_dict.keys():
        markup.add(types.InlineKeyboardButton(region, callback_data=f"{region} обл"), row_width=2)

    bot.send_message(call.message.chat.id, "Обери область з запропонованих:", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.search("обл$", call.data))
def region_selection_callback_handler(call):
    if call.message.text.strip() == "/start":
        return start_command_handler(call.message)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    if re.search("^АР", call.data):
        region = call.data[:-4]
        info[2] = region
    else:
        region = call.data.split(" ")[0]
        info[2] = call.data

    markup = types.InlineKeyboardMarkup()
    for city in area_dict[region]:
        markup.add(types.InlineKeyboardButton(city, callback_data=f", {city}"), row_width=2)

    bot.send_message(call.message.chat.id, "Обери місто з запропонованих або Вся область:", reply_markup=markup)
    previous_user_status[call.message.chat.id] = user_status[call.message.chat.id]
    user_status[call.message.chat.id] = "awaiting_city_selection"


@bot.callback_query_handler(func=lambda call: re.search("^, ", call.data))
def city_selection_callback_handler(call):
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)

    if call.data == ", Вся область":
        pass
    else:
        info[2] = f"{info[2]}{call.data}"

    for i in range(0, 4):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - i)

    bot.send_message(call.message.chat.id, f"Ви обрали: {info[2]}")

    previous_user_status[call.message.chat.id] = user_status[call.message.chat.id]
    user_status[call.message.chat.id] = "the_main_parameters_are_entered"
    additional_parameters_handler(call.message)


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == "awaiting_interval_filter")
def interval_selection_handler(message):
    bot.send_message(message.chat.id, "Вкажи дату початку випуску!", reply_markup=create_reply_keyboard())
    user_status[message.chat.id] = "awaiting_min_value"
    bot.register_next_step_handler(message, min_value_message_handler)


def min_value_message_handler(message):
    if message.text.strip() == "/start":
        return start_command_handler(message)
    if message.text.lower() == "назад ⬅️":
        user_status[message.chat.id] = previous_user_status[message.chat.id]
        return handle_back_button(message)
    else:
        try:
            start = int(message.text.strip())
            years_of_car_production = car_models[info[0]][info[1]]

            if start < years_of_car_production[1] and start > years_of_car_production[0]:
                info[3] = start
                bot.send_message(message.chat.id, "Вкажи дату кінця випуску!", reply_markup=create_reply_keyboard())
                previous_user_status[message.chat.id] = user_status[message.chat.id]
                user_status[message.chat.id] = "awaiting_max_value"
                bot.register_next_step_handler(message, max_value_message_handler)
            else:
                bot.send_message(message.chat.id,
                                 "Обрана модель не випускалась у вказаному році. Введіть коректне значення!")
                bot.register_next_step_handler(message, min_value_message_handler)
        except Exception:
            bot.send_message(message.chat.id, "Введіть коректне значення!", reply_markup=create_reply_keyboard())
            bot.register_next_step_handler(message, min_value_message_handler)


def max_value_message_handler(message):
    if message.text.strip() == "/start":
        return start_command_handler(message)
    if message.text.lower() == "назад ⬅️":
        user_status[message.chat.id] = previous_user_status[message.chat.id]
        return handle_back_button(message)
    else:
        try:
            stop = int(message.text.strip())
            years_of_car_production = car_models[info[0]][info[1]]

            if stop < years_of_car_production[1] and stop > info[3]:
                info[3] = f"{info[3]}-{stop}"
                previous_user_status[message.chat.id] = user_status[message.chat.id]
                user_status[message.chat.id] = "the_main_parameters_are_entered"
                for i in range(0, 5):
                    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - i)

                bot.send_message(message.chat.id, f"Ви обрали: {info[3]}")
                additional_parameters_handler(message)
            else:
                bot.send_message(message.chat.id,
                                 "Обрана модель не випускалась у вказаному році або вказаний рік менший за попереднє значення. Введіть коректне значення!",
                                 reply_markup=create_reply_keyboard())
                bot.register_next_step_handler(message, max_value_message_handler)
        except Exception:
            bot.send_message(message.chat.id, "Введіть коректне значення!", reply_markup=create_reply_keyboard())
            bot.register_next_step_handler(message, max_value_message_handler)


def currency_selection_handler(call):
    markup = types.InlineKeyboardMarkup()
    previous_user_status[call.message.chat.id] = user_status[call.message.chat.id]
    user_status[call.message.chat.id] = "awaiting_currency"
    but1 = types.InlineKeyboardButton("$", callback_data="$")
    but2 = types.InlineKeyboardButton("грн", callback_data="грн")
    markup.add(but1, but2)

    bot.send_message(call.message.chat.id, "Оберіть валюту в якій хочете отримати результат!", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: re.search(r"(^\$$)|(^грн$)", call.data))
def handling_callback_of_currency_selection(call):
    info[4] = call.data

    for i in range(0, 2):
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - i)

    bot.send_message(call.message.chat.id,
                     f"Виконуємо підрахунок середньої вартості автомобіля {info[0].upper()} {info[1].upper()}. Будь ласка, зачекайте!")
    user_status[call.message.chat.id] = "awaiting_calculation"
    handling_received_data(call.message)


@bot.message_handler(func=lambda message: user_status.get(message.chat.id) == 'awaiting_calculation')
def handling_received_data(message):
    res, currency = data_receiving(info)
    cleaning_info()

    if res is not None:
        bot.send_message(message.chat.id, f"Середня ціна вказаного автомобіля по рикну: {res} {currency}")
    else:
        bot.send_message(message.chat.id,
                         "На жаль, за вашим запитом оголошень не знайдено. Спробуйте змінити критерій пошуку, щоб я показав на що здатен!")

    user_status[message.chat.id] = "awaiting_car_brand"


def cleaning_info():
    global info
    info = [0, 0, 0, 0, 0]


def data_receiving(data_list):
    price_list = []
    car_brand = data_list[0]
    car_model = data_list[1]
    area = str(data_list[2])
    interval = str(data_list[3])
    currency = data_list[4]

    average_price_from_cache, data_flag = cache_db.data_searching_in_the_cache(
        car_brand,
        car_model,
        area,
        interval,
        currency)
    if data_flag == 0:
        return average_price_from_cache, currency
    else:
        with config.WebDriverSetup() as session:
            driver = session.get_driver()
            wait = session.get_wait()
            price_list.append(autoria_scraping(driver, wait, car_brand, car_model, area, interval, currency))
            price_list.append(olx_scraping(driver, wait, car_brand, car_model, area, interval, currency))
            price_list.append(rst_scraping(driver, wait, car_brand, car_model, area, interval, currency))
            average_price = calculating(price_list)
        if data_flag == 1:
            cache_db.data_updating_into_the_cache(average_price, car_brand, car_model, area, interval, currency)
            return average_price, currency
        else:
            cache_db.data_adding_into_the_cache(average_price, car_brand, car_model, area, interval, currency)
            return average_price, currency


def main():
    bot.polling()


if __name__ == "__main__":
    main()
