import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import os
import openai
from linkedin_api import Linkedin
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By


options = Options()
options.headless = True
driver = webdriver.Chrome('../chromedriver')
driver.get("https://www.linkedin.com/")


def login(email, psswd):
    email=driver.find_element(By.XPATH,"//input[@name='session_key']")
    user_id=email
    email.send_keys(user_id)
    password=driver.find_element(By.XPATH,"//input[@name='session_password']")
    psswd=psswd
    password.send_keys(psswd)
    time.sleep(3)
    submit = driver.find_element(By.XPATH,"//button[@type='submit']").click()
    time.sleep(3)
    return {"connection_code":"login successful!!!"}


#consider on making an openAi class
#personal bloggger


class OpenAI:
    def __init__(self, api_key):
        openai.api_key = api_key

    def personal_blog_post(prompt):
        response=openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
                {"role": "system", "content": "LinkedIn Blog Post"},
                {"role": "user", "content": prompt}
            ])
        return response["choices"][0]["message"]["content"]


    def message_post(self, prompt):
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=f"Message Request\n\n{prompt}",
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )
        return response.choices[0].text.strip()

    def blog_post(self, prompt):
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            temperature=0.7,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["\n\n"],
        )
        return response.choices[0].text






#post content on LinkedIN
def pub_content(blog_entry):
    button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Start a post']")))
    button.click()
    time.sleep(1)
    y=driver.find_element(By.CLASS_NAME, "ql-editor.ql-blank")
    y.send_keys(OpenAI.blog_post(blog_entry+", with an article link").replace("\n", " "))
    time.sleep(2)
    z= WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//span[text()='Post']")))
    z.click()
    return {"connection_code":"you've got new content"}




industry_selec="Information Technology and Services"
school='University of Wisconsin-Madison'

def make_con():
    network_url = "https://www.linkedin.com/mynetwork/"  
    driver.get(network_url)
    attempt_list=[]
    see_elements = driver.find_elements(By.TAG_NAME, "button")
    for i in range(len(see_elements)-1, -1,-1):
        if see_elements[i].text=="See all":
            see_elements[i].click  
            discover_person_cards=driver.find_elements(By.CLASS_NAME, 'app-aware-link')
            for i in range(len(discover_person_cards)):
                if i==len(discover_person_cards)-2:
                    break
                elif i==0 or i%2==0:
                    href = discover_person_cards[i].get_attribute('href')
                    name = discover_person_cards[i].text
                    attempt_list.append((name, href))
    return attempt_list

def clean_and_connect(attempt_list, industry_selec, school, email, psswd):
    example_list=[item  for item in attempt_list if 'MEMBER_PROFILE_CANNED_SEARCH' not in item[1] ]
    new_list=[]

    application = Linkedin(email, psswd)

    for item in example_list:
        if item[1].split("/")[-2]=="in":
            new_list.append(item)
    time.sleep(2)

    for item in new_list:
        person_profile=application.get_profile(item[1].split("/")[-1])

        try:
            industry=person_profile['industryName']
            educ_list=[True for dicte in person_profile["education"] if school in dicte.values()]

        except:
            educ_list=[True for dicte in person_profile["education"] if school in dicte.values()]

        if True in educ_list or industry==industry_selec:

            driver.get(item[1])
            time.sleep(2)
            button_elements = driver.find_elements(By.TAG_NAME, "button")
            try:
                button_elements[[item.text for item in button_elements].index("Connect")].click()
            except:
                continue
            time.sleep(3)
            new_button_elements = driver.find_elements(By.TAG_NAME, "button")
            new_button_elements[[item.text for item in new_button_elements].index("Add a note")].click()
            time.sleep(3)
            textarea_element = driver.find_element(By.ID, "custom-message")
            textarea_element.send_keys(OpenAI.message_post("Hey, I'm excited to connect!"))
            time.sleep(3)
            new_new_button_elements = driver.find_elements(By.TAG_NAME, "button")
            new_button_elements[[item.text for item in new_new_button_elements].index("Send")].click()
            time.sleep(3)

            break
        else:
            new_list.remove(item)

            continue

    return{"connection_code":"you've got new friends!!!"}


