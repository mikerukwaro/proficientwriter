from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from requests.auth import HTTPBasicAuth
from datetime import datetime, timezone
import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium import webdriver
from dateutil import parser
from time import sleep
import platform
import requests
import config
import uuid
import sys
import os

maxInt = sys.maxsize
api_name = 'writerslab'


def get_computer_licence():
    my_system = platform.uname()
    address: str = f"{my_system.node}pythrackbots{my_system.machine}{my_system.processor}".replace(" ", "")
    licence: str = str(uuid.uuid3(uuid.NAMESPACE_DNS, "%s" % address)).replace('-', '')
    print(licence)
    return licence


def get_provided_licence_details(session_, licence):
    global api_name
    details = session_.get(f'http://pythrack.com/licence/{licence}').json()
    try:
        if details['detail']:
            licence_det = session_.post(f'http://pythrack.com/licence/',
                                        data={'licence': f'{licence}'}).json()
            id_ = licence_det['id']
            session_.post(f'http://pythrack.com/licence/{api_name}/',
                          data={'licence': id_, 'active': True}).json()
            details = session_.get(f'http://pythrack.com/licence/{licence}').json()

    except Exception as e:
        try:
            if details[api_name]['active']:
                pass

        except Exception as e:
            id_ = details['id']
            session_.post(f'http://pythrack.com/licence/{api_name}/',
                          data={'licence': id_, 'active': True})
            details = session_.get(f'http://pythrack.com/licence/{licence}').json()
    active = details[api_name]['active']
    td = parser.parse(details[api_name]['expiry']) - datetime.now(timezone.utc)
    if td.days < 0:
        time_remaining = '0 Days, 0 Hours, 0 Minutes'
    else:
        time_remaining = '{} Days, {} Hours, {} Minutes'.format(td.days, td.seconds // 3600,
                                                                (td.seconds // 60) % 60)
        print(time_remaining)
    return active, time_remaining

def data_path(account_name):
    try:
        cwd = os.getcwd()
        path = os.path.join(cwd, account_name)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    except Exception as e:
        pass


class proficient:
    def __init__(self):
        self.url = 'https://www.proficientwriters.com/aval_orders'
        self.running = True
        self.session = requests.Session()
        self.minimum_characters = 250
        self.blacklist_list = []
        self.blacklist_titles = ["Not Specified"]

    def get_path(self):
        folder_name = "chrome_profile"
        try:
            path = os.path.join(os.getcwd(), folder_name)
            if not os.path.exists(path):
                os.umask(0)
                os.mkdir(path, mode=0o777)
            return path
        except Exception as e:
            return None

    def sign_in(self):
        getting_url = self.driver.get(self.url)
        try:
            email_provision = WebDriverWait(self.driver, 4, poll_frequency=0.2).until(
                EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Email"]')))
            email_provision.send_keys(config.email)
            sleep(2)
            password_provision = WebDriverWait(self.driver, 4, poll_frequency=0.2).\
                until(EC.visibility_of_element_located((By.XPATH, '//input[@placeholder="Password"]')))
            password_provision.send_keys(config.password)
            sleep(3)
            sign_in_button = WebDriverWait(self.driver, 4, poll_frequency=0.2).\
                until(EC.visibility_of_element_located((By.XPATH, '//input[@type="submit"]')))
            sign_in_button.click()
            sleep(1)
        except:
            pass
        self.setup()

    def setup(self):
        for cookie in self.driver.get_cookies():
            self.session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'])
        self.blacklisting_ids()
        while self.running:
            response = self.session.get(self.url).text
            soup = BeautifulSoup(response, "html.parser")
            questions_section = soup.find_all('div', class_="dashboard-main-section__order-wrapper")
            questions_href = []
            for question_section in questions_section:
                if self.running:
                    try:
                        id = question_section.find('p', class_="dashboard-order__id").text
                        id_number = id.split(':')[-1]
                        if id_number not in self.blacklist_list:
                            self.blacklist_list.append(id_number)
                            tasks_url_path = question_section.find('p', class_="dashboard-order__id").find("a").get("href")
                            task_url = "https://www.proficientwriters.com" + tasks_url_path
                            questions_href.append(task_url)
                    except:
                        pass

            self.content_searching(questions_href)
            sleep(150)

    def content_searching(self, questions_href):
        for href_link in questions_href:
            if self.running:
                try:
                    response2 = self.session.get(href_link).text
                    soup2 = BeautifulSoup(response2, "html.parser")
                    order_title = soup2.find('div', class_="dashboard-order__header-wrapper").find('p').text.strip()
                    if order_title in self.blacklist_titles:
                        pass
                    else:
                        order_description_to_be_saved = soup2.find('p', class_="order__paper-details-content").text
                        order_description= soup2.find('p', class_="order__paper-details-content")
                        subject = soup2.find_all('span', class_="service-type__val")[2]
                        if len(order_description_to_be_saved) > self.minimum_characters:
                            self.post_specified_chunk_to_each_account(order_title, order_description)
                            sleep(2)
                            self.expertwriter_poster(order_title, subject, order_description)
                except:
                    pass

    def load_post_accounts(self):
        try:
            with open("{}/accountdetails.txt".format(self.poster_data_path), "r") as file:
                return [x.strip("\n") for x in file.readlines()]
        except Exception as e:
            return False

    def post_specified_chunk_to_each_account(self, order_title, order_description):
        try:
            for acct in self.post_accounts:
                try:
                    single_account_details_as_list = acct.split(",")
                    try:
                        self.post_single_question_to_authenticated_account(
                            order_title, order_description, single_account_details_as_list
                        )
                    except:
                        pass
                except:
                    pass
        except:
            pass
        # except Exception as e:
        #     print(e)
        #     del e

    def post_single_question_to_authenticated_account(self, order_title, order_description,
                                                      single_account_details_as_list
                                                      ):
        try:
            authentication = HTTPBasicAuth(
                single_account_details_as_list[1], single_account_details_as_list[2]
            )
            post_body = {
                "title": order_title,
                "content": order_description,
                "status": "publish",
            }
            self.session.post(
                url="{}/wp-json/wp/v2/posts".format(single_account_details_as_list[0]),
                auth=authentication,
                data=post_body,
            )
        except:
            pass
        # except Exception as e:
        #     print(e)  # "last post section")
        #     del e
        sleep(2)


    def blacklisting_ids(self):
        response = self.session.get('https://www.proficientwriters.com/home_page').text
        soup = BeautifulSoup(response, "html.parser")
        questions_section = soup.find_all('div', class_="dashboard-main-section__order-wrapper")
        for question_section in questions_section:
            id = question_section.find('p', class_="dashboard-order__id").text
            id_number = id.split(':')[-1]
            self.blacklist_list.append(id_number)

    def expertwriter_poster(self, order_title, subject, order_description):
        params = {
            "title": order_title,
            "content": order_description,
            "subject": subject
        }
        response = self.session.post('https://expertwrites.com/api/g4p9pmjbf2cj4rg9b3oxuw0zsu9athdh', data=params)


    def run(self):
        self.poster_data_path = data_path("PosterData")
        self.post_accounts = self.load_post_accounts()
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument(f'--user-data-dir={self.get_path()}')
        self.driver = uc.Chrome(options=chrome_options, use_subprocess=True, suppress_welcome=False)
        active, licence_details = get_provided_licence_details(requests.session(), get_computer_licence())
        if active:
            self.sign_in()
        else:
            print("CONTACT +254792186745 FOR ACTIVATION")

    def terminate(self):
        print("Bot terminating")
        self.running = False
        print("Bot succesfully terminated")


# if __name__ == "__main__":
#     scraper = proficient()
#     scraper.run()
