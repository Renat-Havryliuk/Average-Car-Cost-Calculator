import re
import time
import config
from decorators import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException


def model_searching(driver, wait, car_brand, car_model, area, interval, status_code=0):
    # status_code is a search stage indicator that allows you to return to a specific search stage
    try:
        if status_code == 0:
            # We send the request
            driver.get("https://rst.ua/ukr/")
            print("step 1 completed")
            status_code += 1
    except Exception:
        return model_searching(driver, wait, car_brand, car_model, area, interval)

    try:
        if status_code == 1:
            # Input car brand
            car_brand_filter = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[1]/\
                                                                        div/div[1]/form/div[3]/div/div[2]/select")))
            car_brand_filter.send_keys(car_brand)

            # We check the filter
            time.sleep(0.2)
            page_head_data = wait.until(EC.visibility_of_element_located((By.ID, "rst-h-help"))).text

            if re.search(f"{car_brand}", page_head_data, re.I):
                print("step 2 completed")
                status_code += 1
            else:
                return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 2:
            # Input car model
            car_model_filter = wait.until(EC.visibility_of_element_located((By.XPATH, "/html/body/div[1]/div[3]/div[1]\
                                                                        /div/div[1]/form/div[3]/div/div[3]/select")))
            car_model_filter.send_keys(car_model)

            # We check the filter
            time.sleep(0.2)
            page_head_data = wait.until(EC.visibility_of_element_located((By.ID, "rst-h-help"))).text
            splited_car_model = car_model.split(" ")
            regular_expression = ""
            for i in splited_car_model:
                regular_expression = regular_expression + f"(?=.*{i})"
            if re.search(regular_expression, page_head_data, re.I):
                print("step 3 completed")
                status_code += 1
            else:
                return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 3:
            # Input area in which we will look for a car (optional)
            if area != "0":
                if re.search("^Київська обл", area, re.I):    # We adjust the value entered by the user
                    area = re.sub("^Київська обл", "Київ та обл.", area)
                    area_values = area.split(", ")
                elif re.search("^Крим", area, re.I):    # We adjust the value entered by the user
                    area = re.sub("^Крим", "АР Крим", area)
                    area_values = area.split(", ")
                else:
                    area_values = area.split(", ")
                    area_values[0] = area_values[0].split(" ")[0]

                wait.until(EC.element_to_be_clickable((By.ID, "sf-region-bmodal"))).click()
                area_table = (wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".list-unstyled.row.m-0.fs-2")))
                              .find_elements(by=By.TAG_NAME, value="label"))

                for area_string in area_table:
                    if area_string.text == area_values[0]:
                        area_string.click()
                        area_button = wait.until(EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, ".col-12.col-lg-8.offset-lg-2.mt-4.mb-2"))
                        ).find_element(by=By.TAG_NAME, value="button")
                        area_button.click()
                        break
                    else:
                        continue

                if len(area_values) > 1:
                    inspection_key = 2
                    city_filter = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[1]/\
                                                                                div/div[1]/form/div[1]/div/select[2]")))
                    city_filter.send_keys(area_values[1])
                else:
                    inspection_key = 1

                # We check the filter
                time.sleep(0.2)
                page_head_data = wait.until(EC.visibility_of_element_located((By.ID, "rst-h-help"))).text

                if inspection_key == 1:
                    if re.search(area, page_head_data, re.I):
                        print("step 3 completed")
                        status_code += 1
                    else:
                        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
                if inspection_key == 2:
                    if re.search(f"{area_values[1]}", page_head_data, re.I):
                        print("step 3 completed")
                        status_code += 1
                    else:
                        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
            else:
                print("step 3 completed")
                status_code += 1
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 4:
            # Input auto release interval (optional)
            if interval != "0":
                interval_values = interval.split("-")
                interval_min_value = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[1]/\
                                                                            div/div[1]/form/div[3]/div/div[4]/select")))
                interval_min_value.click()
                for year_from in interval_min_value.find_elements(by=By.TAG_NAME, value="option"):
                    if year_from.get_attribute("value") == interval_values[0]:
                        year_from.click()
                        break
                    else:
                        continue

                interval_max_value = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[3]/div[1]/\
                                                                            div/div[1]/form/div[3]/div/div[5]/select")))
                interval_max_value.click()
                for year_from in interval_max_value.find_elements(by=By.TAG_NAME, value="option"):
                    if year_from.get_attribute("value") == interval_values[1]:
                        year_from.click()
                        break
                    else:
                        continue

                # We check the filter
                time.sleep(0.2)
                page_head_data = wait.until(EC.visibility_of_element_located((By.ID, "rst-h-help"))).text
                if re.search(f"{interval_values[0]} - {interval_values[1]}", page_head_data, re.I):
                    print("step 4 completed")
                    status_code += 1
                else:
                    return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
            else:
                print("step 4 completed")
                status_code += 1
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 5:
            # We get the search results
            wait.until(EC.element_to_be_clickable((By.ID, "rst-head"))).click()
            print("step 6 completed")
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)


# Function to encrypt page numbers for RST
def encrypt_page_number(n):

    encryption_table = [1, 2, 3, 1, 2, 1, 2, 3, 1, 2]
    index = (n - 1) % len(encryption_table)

    return encryption_table[index]


def scraping(price_list, page_counter, car_counter, driver, wait, currency, flag=True):
    # We find car prices
    counter_iter = 1
    try:
        car_cards = (wait.until(EC.presence_of_element_located((By.ID, f"p-{page_counter}")))
                     .find_elements(by=By.CSS_SELECTOR, value=".i.car-i.mb-3.bg-white.br-md-2.shadow"))
        if len(car_cards) < 1:
            raise TimeoutException

    except TimeoutException:
        flag = False
        return price_list, flag, car_counter

    try:
        for car_card in car_cards:
            # We filter cards with cars
            if "archive" in car_card.get_attribute("class"):
                flag = False
                raise StopIteration
            try:
                car_flag = car_card.find_element(by=By.CLASS_NAME, value="bgs")
                if re.search("під замовлення", car_flag.text, re.I):
                    get_price_flag = False
                    print("під замовлення")
                    print(f"Оброблено {counter_iter} на цій сторінці")
                else:
                    get_price_flag = True
            except NoSuchElementException:
                get_price_flag = True

            if get_price_flag is True:
                # We format the price
                if currency == "$":
                    car_price_unformatted = wait.until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[1]/div[3]/div\
                    [1]/div/div[2]/div[{encrypt_page_number(page_counter) + 1}]/article[{counter_iter}]/div[2]/div[1]/div/b"))).text
                    car_price_unformatted = car_price_unformatted.split("=")[0][1:-1].split("'")
                else:
                    car_price_unformatted = wait.until(EC.presence_of_element_located((By.XPATH, f"/html/body/div[1]/div[3]/div\
                    [1]/div/div[2]/div[{encrypt_page_number(page_counter) + 1}]/article[{counter_iter}]/div[2]/div[1]/div/b/i"))).text[2:-3].split("'")
                car_price_formatted = ""
                for i in car_price_unformatted:
                    car_price_formatted += i
                car_price_formatted = int(car_price_formatted)

                price_list.append(car_price_formatted)  # We add value to list
                print(f"Ціна: {car_price_formatted}")
                print(f"Оброблено {counter_iter} на цій сторінці")
            counter_iter += 1

        return price_list, flag, car_counter

    except StopIteration:
        return price_list, flag, car_counter

    finally:
        print(f"ОБРОБЛЕНО СТОРІНОК: {page_counter}! \n")


@retry(3)
def scrolling(price_list, driver, wait, currency, flag=True, page_counter=0, car_counter=0):
    page_counter += 1
    time.sleep(0.5)

    if flag is False:
        f"Знайдено {car_counter} авто"
        return price_list
    else:

        # We search next page navigation element
        try:
            next_page_element = (wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".next.ms-auto")))
                                 .find_element(by=By.TAG_NAME, value="a"))
        except Exception:
            next_page_element = 0

        if next_page_element == 0:
            # We scroll a page
            driver.execute_script("arguments[0].scrollIntoView();",
                                  wait.until(EC.presence_of_element_located((By.ID, "rst-footer"))))

            # We find car prices
            price_list, flag, car_counter = scraping(price_list, page_counter, car_counter, driver, wait, currency, flag)

        else:

            # We scroll a page
            driver.execute_script("arguments[0].scrollIntoView();", next_page_element)

            # We find car prices
            price_list, flag, car_counter = scraping(price_list, page_counter, car_counter, driver, wait, currency, flag)

            if flag is True:
                next_page_element.click()

        # Recursive function call
        scrolling(price_list, driver, wait, currency, flag, page_counter, car_counter)


def data_mining(driver, wait, currency):

    # List with all prices
    car_prices = []

    scrolling(car_prices, driver, wait, currency)
    if len(car_prices) == 0:
        car_prices.append(0)

    return car_prices


def rst_scraping(driver, wait, car_brand, car_model, area, interval, currency):
    model_searching(driver, wait, car_brand, car_model, area, interval)

    return data_mining(driver, wait, currency)


def main():
    with config.WebDriverSetup() as session:
        driver = session.get_driver()
        wait = session.get_wait()
        rst_scraping(driver, wait, "audi", "a4", "Київська обл, Київ", "2018-2024", "$")


if __name__ == "__main__":
    main()
