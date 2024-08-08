import re
import time
import config
from decorators import retry
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException


def model_searching(driver, wait, car_brand, car_model, area, interval, status_code=0):
    # We create pointer of exit
    flag = True

    # status_code is a search stage indicator that allows you to return to a specific search stage
    try:
        if status_code == 0:

            # I send the request
            driver.get("https://auto.ria.com/uk/")

            # I agree with using cookies
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".js-close.c-notifier-btn"))).click()
            print("step 1 completed")
            status_code += 1
    except Exception:
        return model_searching(driver, wait, car_brand, car_model, area, interval)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 1:
            # Input car brand
            car_brand_filter = wait.until(EC.visibility_of_element_located((By.ID,
                                                                            "brandTooltipBrandAutocompleteInput-brand"))
                                          )
            car_brand_filter.clear()
            car_brand_filter.send_keys(car_brand)
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[3]/div[1]/form/div[2]/\
                                                    div[1]/div[2]/div/div[2]/div/ul/li/a"))).click()

            car_brand_filter_data = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[3]\
            /div[1]/form/div[2]/div[1]/div[2]/div/div[2]/div/label"))).get_attribute("data-text")

            # I check the filter
            if car_brand_filter_data.lower() == car_brand:
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
            car_model_filter = wait.until(EC.visibility_of_element_located((By.ID,
                                                                            "brandTooltipBrandAutocompleteInput-model"))
                                          )
            car_model_filter.clear()
            car_model_filter.send_keys(car_model)
            wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[3]/div[1]/form/div[2]/\
                                                                div[1]/div[3]/div/div[2]/div/ul/li[1]/a"))).click()

            # I check the filter
            car_model_filter_data = wait.until(EC.presence_of_element_located((By.XPATH, "/html/body/div[1]/main/div[3]\
                        /div[1]/form/div[2]/div[1]/div[3]/div/div[2]/div/label"))).get_attribute("data-text")
            splited_car_model = car_model.split(" ")
            regular_expression = ""
            for i in splited_car_model:
                regular_expression = regular_expression + f"(?=.*{i})"
            if re.search(regular_expression, car_model_filter_data, re.I):
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
                search_area_filter = wait.until(
                    EC.presence_of_element_located((By.ID, "brandTooltipBrandAutocompleteInput-region"))
                )

                if re.search("обл$", area, re.I):
                    inspection_key = 1
                    search_area_filter.clear()
                    search_area_filter.send_keys(f"{area}.")
                    time.sleep(1)
                    wait.until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/div[1]/main/div[3]/div[1]/form/div[2]/\
                                                            div[2]/div[1]/div/div/div[2]/div/ul/li[1]"))
                    ).click()

                else:
                    inspection_key = 2
                    search_area_filter.clear()
                    search_area_filter.send_keys(area.split(", ")[-1])
                    time.sleep(1)
                    wait.until(EC.element_to_be_clickable(
                        (By.XPATH, "/html/body/div[1]/main/div[3]/div[1]/form/div[2]\
                                    /div[2]/div[1]/div/div/div[2]/div/ul/li[1]"))
                    ).click()

                # I check the filter
                area_filter_elements = wait.until(
                    EC.presence_of_all_elements_located((By.XPATH,
                                                         "/html/body/div[1]/main/div[3]/div[1]/form/div[2]\
                                                         /div[2]/div[1]/div/div/div[2]/div/ul/li"))
                )

                for area_filter_element in area_filter_elements:
                    if inspection_key == 1:
                        if area_filter_element.get_attribute("class") == "list-item active check":
                            filter_text = driver.execute_script("return arguments[0].textContent;", area_filter_element)
                            if filter_text == f"{area}.":
                                print("step 4 completed")
                                status_code += 1
                            break
                        else:
                            continue

                    else:
                        if area_filter_element.get_attribute("class") == "list-item active check":
                            filter_text = driver.execute_script("return arguments[0].textContent;", area_filter_element)
                            if filter_text == area.split(", ")[-1]:
                                print("step 4 completed")
                                status_code += 1
                            break
                        else:
                            continue

                if status_code == 3:
                    return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
            else:
                print("step 4 completed")
                status_code += 1
    except TimeoutException:
        flag = False
        return flag
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 4:
            # Input auto release interval (optional)
            if interval != "0":
                interval_values = interval.split("-")
                wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".pseudoelement._grey"))).click()
                interval_min_value = wait.until(EC.presence_of_element_located((By.ID, "yearFrom")))
                interval_min_value.send_keys(interval_values[0])
                interval_max_value = wait.until(EC.presence_of_element_located((By.ID, "yearTo")))
                interval_max_value.send_keys(interval_values[1])
                wait.until(EC.element_to_be_clickable((By.CLASS_NAME, "fold"))).click()

                # I check the filter
                filter_min_element = wait.until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div[1]/main/div[3]/div[1]/\
                                                    form/div[2]/div[2]/div[2]/div/div/label/span[2]"))
                )
                filter_max_element = wait.until(
                    EC.presence_of_element_located((By.XPATH,
                                                    "/html/body/div[1]/main/div[3]/div[1]/\
                                                    form/div[2]/div[2]/div[2]/div/div/label/span[4]"))
                )

                filter_min_text = driver.execute_script("return arguments[0].textContent;", filter_min_element)
                filter_max_text = driver.execute_script("return arguments[0].textContent;", filter_max_element)

                if filter_min_text == interval_values[0] and filter_max_text == interval_values[1]:
                    print("step 5 completed")
                    status_code += 1
                else:
                    return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

            else:
                print("step 5 completed")
                status_code += 1
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)

    try:
        if status_code == 5:
            # I get the search results
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".button.full"))).click()
            print("step 6 completed")
    except TimeoutException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    except ElementClickInterceptedException:
        return model_searching(driver, wait, car_brand, car_model, area, interval, status_code)
    return flag


def scraping(price_list, page_counter, car_counter, wait, currency):

    try:
        # I find car prices
        car_cards = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "ticket-item ")))
        counter_iter = 1
        for car_card in car_cards:
            if not car_card.get_attribute("data-search-position"):
                continue
            car_price_block = car_card.find_element(by=By.CLASS_NAME, value="size15")
            # We choose the currency
            if currency == "$":
                car_price_element = car_price_block.find_element(by=By.CSS_SELECTOR, value=".bold.size22.green")

                # I format the price
                car_price_un_formatted = car_price_element.text.split(" ")
                car_price_formatted = ""
                for i in car_price_un_formatted:
                    car_price_formatted += i
                car_price_formatted = int(car_price_formatted)

            else:
                car_price_element = car_price_block.find_element(by=By.CLASS_NAME, value="i-block").find_element(
                    by=By.TAG_NAME, value="span"
                )

                # I format the price
                car_price_unformatted = car_price_element.text.split(" ")
                car_price_formatted = ""
                for i in car_price_unformatted:
                    car_price_formatted += i
                car_price_formatted = int(car_price_formatted)

            price_list.append(car_price_formatted)  # We add value to list

            print(f"Ціна: {car_price_formatted}")
            print(f"Оброблено {counter_iter} на цій сторінці")
            counter_iter += 1
            car_counter += 1

        return price_list, car_counter
    except Exception:
        print(f"Знайдено {car_counter} авто")
        return price_list, car_counter
    finally:
        print(f"ОБРОБЛЕНО СТОРІНОК: {page_counter}! \n")


@retry(3)
def scrolling(price_list, page_counter, driver, wait, currency, car_counter=0):
    # If no results are found, we stop work
    try:
        if wait.until(EC.presence_of_element_located((By.ID, "subscribesEmptyTitle"))).get_attribute("class") == "hide":
            price_list.append(0)
            return price_list
    except Exception:
        pass

    # I search pages navigation elements
    next_page_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-link.js-next")))

    # Here I used attribute "href" because "class" doesn't work correctly
    next_page_element_href_value = next_page_element.get_attribute("href")

    # I scroll a page
    driver.execute_script("arguments[0].scrollIntoView();", next_page_element)
    time.sleep(5)
    page_counter += 1

    # I find car prices
    price_list, car_counter = scraping(price_list, page_counter, car_counter, wait, currency)

    print(next_page_element_href_value)

    # Check if it's the last page
    if re.search(r"javascript:void\(0\)", next_page_element_href_value, re.I):
        return price_list
    else:
        try:
            next_page_element.click()
            # Wait for new elements to load after clicking next page
            wait.until(EC.staleness_of(next_page_element))
            # Wait until the old element is stale (no longer attached to the DOM)
            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".page-link.js-next")))
        except Exception as _ex:
            print(_ex)
        scrolling(price_list, page_counter, driver, wait, currency, car_counter)


def data_mining(driver, wait, currency):

    # List with all prices
    car_prices = []

    scrolling(car_prices, 0, driver, wait, currency)
    return car_prices


def autoria_scraping(driver, wait, car_brand, car_model, area, interval, currency):

    flag = model_searching(driver, wait, car_brand, car_model, area, interval)

    if flag == True:
        return data_mining(driver, wait, currency)
    else:
        return [0]


def main():
    with config.WebDriverSetup() as session:
        driver = session.get_driver()
        wait = session.get_wait()
        autoria_scraping(driver, wait, "bmw", "4 series", "Київська обл, Київ", "2020-2024", "$")


if __name__ == "__main__":
    main()
