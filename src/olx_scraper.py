import re
import time
import config
from decorators import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, StaleElementReferenceException


def model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code=0):
    # status_code is a search stage indicator that allows you to return to a specific search stage
    try:
        if status_code == 0:
            # We send the request
            driver.get("https://www.olx.ua/uk/transport/legkovye-avtomobili/")

            # Agree with using cookies
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/div[4]/div[3]/button"))).click()
            status_code += 1
            print("step 1 completed")

    except Exception:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency)

    try:
        if status_code == 1:
            # Input car brand
            car_brand_block = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "css-1qvyz1h")))[-1]
            car_brand_block.click()
            car_brand_list = (wait.until(EC.visibility_of_element_located((By.CLASS_NAME, "css-1bjsvqt")))
                              .find_elements(by=By.TAG_NAME, value="li")[1:])
            try:
                flag_brand = False
                for car_brand_element in car_brand_list:
                    if car_brand_element.find_element(by=By.TAG_NAME, value="span").text.lower() == car_brand:
                        car_brand_element.click()
                        flag_brand = True
                        break
                    else:
                        continue

                if flag_brand is False:
                    raise NoSuchElementException

            except NoSuchElementException:
                return False

            time.sleep(2)

            # We check the filter
            car_brand_text = car_brand_block.find_element(by=By.TAG_NAME, value="div").text
            if car_brand_text.lower() == car_brand:
                print("step 2 completed")
                status_code += 1
            else:
                return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)

    try:
        if status_code == 2:
            # Input car model
            car_model_block = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-7xjci5")))
            car_model_block.click()

            car_model_list = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "css-1rfy03l")))[1:]
            try:
                flag_model = False
                for car_model_element in car_model_list:
                    if car_model_element.find_element(by=By.TAG_NAME, value="p").text.lower() == car_model:
                        car_model_element.click()
                        flag_model = True
                        break
                    else:
                        continue

                if flag_model is False:
                    raise NoSuchElementException

            except NoSuchElementException:
                return False

            time.sleep(2)

            # We check the filter
            car_model_text = car_model_block.find_element(by=By.XPATH, value="./div/div/div[1]/div/span").text
            splited_car_model = car_model.split(" ")
            regular_expression = ""
            for i in splited_car_model:
                regular_expression = regular_expression + f"(?=.*{i})"
            if re.search(regular_expression, car_model_text, re.I):
                print("step 3 completed")
                status_code += 1
            else:
                return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)

    try:
        if status_code == 3:
            # Input area in which we will look for a car (optional)
            if area != "0":
                try:
                    search_area_filter = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-1euwasq")))
                except TimeoutException:
                    search_area_filter = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-ue5w3r")))
                search_area_filter.clear()
                search_area_filter.click()
                if re.search("Крим$", area, re.I):
                    area = re.sub("Крим", "Крим (АРК)", area)

                if re.search("^(Крим)\\s*\\((АРК)\\)$| обл$", area, re.I):
                    inspection_key = 1
                    if re.search("обл$", area, re.I):
                        area_corrected = area + "асть"
                    else:
                        area_corrected = area
                    area_table = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-jbjbe9")))
                    for table_string in area_table:
                        if area_corrected == table_string.text:
                            table_string.click()
                            wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-wdt9hf"))).click()
                            break
                        else:
                            continue
                else:
                    inspection_key = 2
                    search_area_filter.send_keys(area.split(", ")[-1])
                    wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-7lx9dr"))).click()

                time.sleep(2)

                # We check the filter
                area_filter_text = search_area_filter.get_attribute("value")

                if inspection_key == 1:
                    if area_filter_text == area_corrected:
                        status_code += 1
                        print("step 4 completed")
                    else:
                        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
                else:
                    if area_filter_text.split(",")[0] == area.split(", ")[-1]:
                        print("step 4 completed")
                        status_code += 1
                    else:
                        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
            else:
                print("step 4 completed")
                status_code += 1
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)

    try:
        if status_code == 4:
            # Input auto release interval (optional)
            if interval != "0":
                interval_values = interval.split("-")
                interval_block = wait.until(EC.visibility_of_all_elements_located((By.CLASS_NAME, "css-1lrk3cc")))[1]
                interval_child_blocks = interval_block.find_elements(by=By.CLASS_NAME, value="css-3f5a10")
                interval_child_blocks[0].clear()
                interval_child_blocks[0].send_keys(interval_values[0], Keys.ENTER)
                time.sleep(2)
                interval_child_blocks[1].clear()
                interval_child_blocks[1].send_keys(interval_values[1], Keys.ENTER)

                time.sleep(2)

                # Use custom wait for check the filter
                wait.until(config.element_value_matches((By.CLASS_NAME, "css-3f5a10"), interval_values))
                print("step 5 completed")
                status_code += 1
            else:
                print("step 5 completed")
                status_code += 1
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)

    time.sleep(2)

    try:
        if status_code == 5:
            if currency == "$":
                (wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "css-1e5mbis")))).click()

            # We check the filter
            currency_elements = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-1i0l121"))).find_elements(
                by=By.TAG_NAME, value="span"
            )
            currency_flag = False
            if currency == "$":
                for currency_element in currency_elements:
                    if currency_element.text == currency:
                        currency_flag = True
                        break

                if currency_flag is False:
                    return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
                else:
                    print("step 6 completed")
            else:
                for currency_element in currency_elements:
                    if currency_element.text.split(".")[0] == currency:
                        currency_flag = True
                        break

                if currency_flag is False:
                    return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
                else:
                    print("step 6 completed")
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, currency, status_code)

    # We get the search results automatically
    return True


def scraping(price_list, page_counter, car_counter, wait):
    # We find car prices
    car_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "css-1venxj6")))

    counter_iter = 1

    try:
        for car_card in car_cards:
            car_price_element = car_card.find_element(by=By.CLASS_NAME, value="css-13afqrm")

            # We format the price
            car_price_unformatted = (car_price_element.text.split(" "))
            if len(car_price_unformatted) < 2:
                print("\nОбмін / Договірна / Продано - пропускаємо\n")
                continue
            else:
                car_price_formatted = ""
                for i in car_price_unformatted[:-1]:
                    car_price_formatted += i
                car_price_formatted = int(car_price_formatted)

            price_list.append(car_price_formatted)  # We add value to list

            print(f"Ціна: {car_price_formatted}")
            print(f"Оброблено {counter_iter} на цій сторінці")
            counter_iter += 1
            car_counter += 1

        return price_list, car_counter
    except Exception as _ex:
        print(_ex)
        print(f"Знайдено {car_counter} авто")
        return price_list, car_counter
    finally:
        print(f"ОБРОБЛЕНО СТОРІНОК: {page_counter}! \n")


@retry(3)
def scrolling(price_list, page_counter, driver, wait, car_counter=0, func_status=0):
    # We search pages navigation elements
    try:
        nav_elements_list = (
            (wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-1vdlgt7"))))
            .find_elements(by=By.TAG_NAME, value="a"))
        next_page_element = None
        for nav_element in nav_elements_list:
            if nav_element.get_attribute("data-testid") == "pagination-forward":
                next_page_element = nav_element
                break
        if next_page_element is None:
            raise TimeoutException

    except TimeoutException:
        next_page_element = 0

    if next_page_element == 0:
        # We scroll a page
        element_for_scrolling = (wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-asqnhr")))
                                 .find_element(by=By.XPATH, value="./span/span"))
        # If no results are found, we stop work
        if func_status == 0:
            if re.search("0", element_for_scrolling.text):
                price_list.append(0)
                return price_list
            else:
                element_for_scrolling = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-11l6j54")))
        else:
            element_for_scrolling = wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-11l6j54")))
        driver.execute_script("arguments[0].scrollIntoView();", element_for_scrolling)

        page_counter += 1
        # We find car prices
        price_list, car_counter = scraping(price_list, page_counter, car_counter, wait)
        return price_list
    else:
        # We scroll a page
        driver.execute_script("arguments[0].scrollIntoView();", next_page_element)
        page_counter += 1
        time.sleep(1)

        # We find car prices
        price_list, car_counter = scraping(price_list, page_counter, car_counter, wait)

        try:
            next_page_element.click()
        except StaleElementReferenceException:
            # Re-search for an element if a stale element reference error occurs
            nav_elements_list = (
                (wait.until(EC.presence_of_element_located((By.CLASS_NAME, "css-1vdlgt7"))))
                .find_elements(by=By.TAG_NAME, value="a"))
            next_page_element = None
            for nav_element in nav_elements_list:
                if nav_element.get_attribute("data-testid") == "pagination-forward":
                    next_page_element = nav_element
                    break
            next_page_element.click()

        # Recursive function call
        func_status += 1
        scrolling(price_list, page_counter, driver, wait, car_counter, func_status)


def data_mining(driver, wait):
    # List with all prices
    car_prices = []

    scrolling(car_prices, 0, driver, wait)
    return car_prices


def olx_scraping(driver, wait, car_brand, car_model, area, interval, currency):
    main_flag = model_searching(driver, wait, car_brand, car_model, area, interval, currency)

    if main_flag is True:
        return data_mining(driver, wait)

    else:
        return [0]


def main():
    with config.WebDriverSetup() as session:
        driver = session.get_driver()
        wait = session.get_wait()
        olx_scraping(driver, wait, "honda", "accord", "Київська обл, Київ", "2007-2014", "$")


if __name__ == "__main__":
    main()
