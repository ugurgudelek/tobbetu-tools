from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import OrderedDict
import time
import pickle
import os
import configparser
import argparse
import re

SESSION_NO = '973FF64C-D83C-4024-B3B0-79CB4B224FE4'
BASE_URL = f'https://program.etu.edu.tr/DersProgrami/?oturumNo={SESSION_NO}#/'

chrome_options = Options()
# chrome_options.add_argument("--headless")
driver = webdriver.Chrome('../driver/chromedriver.exe', options=chrome_options)
driver.get(BASE_URL)

def force_find_element_by_xpath(xpath):
    while True:
        try:
            element = driver.find_element_by_xpath(xpath)
            return element
        except:
            time.sleep(1)

courses_form_control = force_find_element_by_xpath('//*[@id="panelLatestMovies"]/div[2]/form/div[1]/div/div[2]/select')
options = courses_form_control.find_elements_by_tag_name('option')

courses = dict()  # 1234:'bil133'
for i, option in enumerate(options):
    if i == 0: continue # drop first undefined course
    course_name = option.text
    code = option.get_attribute('value')
    courses[code] = course_name

# courses = {21252: 'BİL 133 Kombinatorik ve Çizge Kuramı'}

def course_schedule_to_csv(course_schedule_link):
    driver.get(course_schedule_link)
    time.sleep(2)

    dataframes = pd.read_html(driver.page_source)

    for dataframe in dataframes:
        section_info = dataframe.iloc[0, 0]
        section_num, section_lecturer, section_capacity = extract_section_info(section_info)

        df = pd.DataFrame(dataframe.iloc[2:, :].values,
                          columns=dataframe.iloc[1, :].values)
        df = df.set_index('Saat')

        slots = []
        arr = df.values
        for i,_ in enumerate(arr):
            for j,_ in enumerate(arr[i]):
                if arr[i][j] != '-':
                    day = df.columns[j]
                    hour = df.index[i]
                    place = df.iloc[i, j]

                    slots += [Slot(day, hour, place)]


        section_dir = os.path.join(course_dir, str(section_num))
        os.makedirs(section_dir, exist_ok=True)

        with open(os.path.join(section_dir, 'info.txt'), 'a') as f:
            for slot in slots:
                f.write("\n")
                f.write(str(slot))



class Slot:
    def __init__(self, day, hour, place):
        self.day = day
        self.hour = hour
        self.place = place

    def __str__(self):
        return " - ".join(map(str, [self.day, self.hour, self.place]))


def extract_section_info(section_info):

    section_num = int(section_info.split('-')[0].split(':')[1].strip())  # Şube: 1 -> 1
    section_lecturer = section_info.split('-')[1].strip()  # OĞUZ ERGİN
    section_capacity = None
    if section_info.split('-').__len__() == 3:
        section_capacity = int(section_info.split('-')[-1].split(':')[-1].strip())  # Toplam:45 -> 45
    return section_num, section_lecturer, section_capacity

def student_lists_to_csv(student_list_link):
    driver.get(student_list_link)
    time.sleep(2)

    student_list_dataframes = pd.read_html(driver.page_source)

    for student_list_dataframe in student_list_dataframes:
        section_info = student_list_dataframe.iloc[0, 0]
        section_num, section_lecturer, section_capacity = extract_section_info(section_info)

        df = pd.DataFrame(student_list_dataframe.iloc[2:, 1:].values,
                          columns=student_list_dataframe.iloc[1, 1:])

        section_dir = os.path.join(course_dir, str(section_num))
        os.makedirs(section_dir, exist_ok=True)

        with open(os.path.join(section_dir, 'info.txt'), 'w') as f:
            f.write(section_info)
        df.to_csv(os.path.join(section_dir, f"{section_num}.csv"))


with tqdm(total=len(courses)) as pbar:
    for code, course_name in courses.items():
        pbar.set_description(f"Course: {course_name}")

        course_dir = os.path.join('..', 'course_student_list', f"{code}")
        os.makedirs(course_dir, exist_ok=True)

        with open(os.path.join(course_dir, 'info.txt'), 'w') as f:
            f.write(course_name)

        course_schedule_link = BASE_URL + f"ders/dersprogram/{code}/0"
        student_list_link = BASE_URL+f"sube/ogrencilist/{code}/0"

        try:
            student_lists_to_csv(student_list_link)
            course_schedule_to_csv(course_schedule_link)
        except:
            print(f"{courses[code]} could not be crawled!")

        pbar.update(1)









# for code in codes:
#
#     # Select(courses_form_control).select_by_visible_text(u"{}".format(course_name))
#     # print(course_name)
#     # force_find_element_by_xpath('//*[@id="panelLatestMovies"]/div[2]/form/div[7]/div/div/button').click()
#     driver.get(BASE_URL+f"sube/ogrencilist/{code}/0")
#     time.sleep(2)



# form.click()