# coding=utf-8
import time
import csv
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
from datetime import datetime

"""
def init_webdriver_local():
    print("init_webdriver_local()")
    return webdriver.Chrome(ChromeDriverManager().install())
"""


def init_webdriver_docker():
    print("init_webdriver_docker()")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome("/usr/local/bin/chromedriver", options=options)


def init_webdriver_headless():
    print("Running headless chrome")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)


def login_to_page(driver):
    print("login_to_page(driver)")
    driver.get("https://www.brainville.com/PublicPage/Login")
    log_in_form = driver.find_element_by_tag_name("form")
    user_name_input = log_in_form.find_element_by_id("UserName")
    password_input = log_in_form.find_element_by_id("Password")
    user_name_input.send_keys("carlmichael.lonnberg@addq.se")
    password_input.send_keys("!Carlmichael")
    log_in_form.submit()


def assert_login(driver):
    print("assert_login(driver)")
    if driver.current_url == "https://www.brainville.com/Market/RequisitionSearchResult":
        print("Successfully logged in to: " + driver.current_url)
    else:
        print("Login failed, at page: " + driver.current_url)


def select_standard_filter(driver):
    print("select_standard_filter(driver)")
    driver.find_element_by_id("toggleAdvancedFilter").click()
    select = Select(driver.find_element_by_id('SearchProfileId'))
    select.select_by_value("25951")


def close_active_filters(driver):
    print("close_active_filters(driver)")
    competence_filters = driver.find_elements_by_css_selector(".competenceAreaTag")
    for i in competence_filters:
        if i.get_attribute("class") == "competenceAreaTag tag activeFilter":
            i.click()


def activate_search_filters(driver):
    print("activate_search_filters(driver)")
    it_and_telecom = "1"
    competence_filters = driver.find_elements_by_css_selector(".competenceAreaTag")
    for i in competence_filters:
        if i.get_attribute("data-competenceid") == it_and_telecom:
            print("Search competencies: ", i.text)
            i.click()


def search_locations(driver):
    location_filters = driver.find_elements_by_id("LocationFilter")
    locations = []
    for i in location_filters:
        print("Search locations: ", i.text)
        locations.append(i.text)
    return locations


def find_adds(driver):
    print("find_adds(driver)")
    adds = driver.find_elements_by_class_name("feedItemFlex")
    print("Total no of adds: ", len(adds))
    new_adds = []
    for i in adds:
        if "Ny" in i.text:
            # if "igår" in i.text:
            new_adds.append(i)
    print("New adds: ", len(new_adds))
    return new_adds


def get_links(new_adds):
    print("get_links(newAdds)")
    add_links = []
    for add in new_adds:
        add_links.append(add.find_element_by_class_name("feedHead").find_element_by_tag_name("a").get_attribute("href"))
    print("Collected links: ", len(add_links))
    return add_links


def get_competencies(add_links, driver):
    print("get_competencies(addLinks, driver)")
    competencies = []
    # for link in addLinks:
    for link in add_links[:2]:
        print("Opening link: ", link)
        driver.get(link)
        competence_tags = driver.find_elements_by_class_name("tagNoPointer")
        print("No of competencies collected: ", len(competence_tags))
        for tag in competence_tags:
            competencies.append(tag.text.lower())
        driver.back()
    return competencies


def make_dir():
    print("make_dir()")
    if not os.path.isdir('/data/'):
        os.mkdir('/data/')


def store_data(competencies, locations):
    print("store_data(competencies, locations)")
    date = datetime.now().date().strftime("%Y-%m-%d")
    hour_of_day = datetime.now().strftime("%H:%M")
    filename = date + ".csv"
    path = "data/"
    file = path + filename
    print("Saving data to file: ", file)
    with open(file, 'a') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow([hour_of_day, date, locations, competencies])


def main():
    print("Starting: main()")

    driver = init_webdriver_docker()
    # driver = init_webdriver_local()
    # driver = init_webdriver_headless()

    login_to_page(driver)
    assert_login(driver)
    select_standard_filter(driver)
    close_active_filters(driver)
    activate_search_filters(driver)
    locations = search_locations(driver)
    new_adds = find_adds(driver)
    add_links = get_links(new_adds)
    competencies = get_competencies(add_links, driver)
    make_dir()
    store_data(competencies, locations)
    driver.close()


start_time = time.time()
main()
print("%s seconds" % (time.time() - start_time))