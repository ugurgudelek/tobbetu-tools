from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By

import pandas as pd
import numpy as np
from tqdm import tqdm
from collections import OrderedDict
import time
import pickle
import os
import configparser
import argparse

def get_coursecode(course_name):
    driver.get(BASE_URL)
    course_form = driver.find_element_by_name('dersProgramForm')
    course_rows = course_form.find_element_by_class_name('row')
    courses_formcontrol = course_rows.find_element_by_class_name('form-control')
    options = courses_formcontrol.find_elements_by_tag_name('option')

    course_code = None
    for option in options:
        if option.text.find(course_name) != -1:
            course_code = option.get_attribute('value')

    if course_code is None:
        raise Exception('Course code is not found!')

    return course_code


def get_tablerows(driver, url):
    driver.get(url)
    time.sleep(1)  # wait for js code to run
    element = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.TAG_NAME, "tr")))

    # maybe be we have multiple sections
    tables = driver.find_elements_by_class_name('table')
    rows = []
    for table in tables:
        rows += table.find_elements_by_tag_name("tr")
    return rows


def get_student_nums(driver):
    student_nums = []
    for row in get_tablerows(driver, STUDENT_LIST_URL):

        cols = row.find_elements_by_tag_name("td")
        try:
            sn = cols[1].text
            try:
                sn = int(sn)
                student_nums.append(sn)
            except:
                continue
        except:
            continue
    print('This course has {} students'.format(student_nums.__len__()))
    return student_nums


def get_schedule_occupancy(driver, student_num):
    student_programme_url = SCHEDULE_URL.format(student_num=student_num)
    rows = get_tablerows(driver, student_programme_url)
    schedule = np.zeros((13, 6))
    for row_ix, row in enumerate(rows[1:]):
        for col_ix, col in enumerate(row.find_elements_by_tag_name("td")[1:]):
            # print("(ROW,COL) -> ({},{}) == {}".format(row_ix,col_ix,col.text))
            if col.text != '-':
                schedule[row_ix, col_ix] = 1
    return schedule


def mapdayhour2index(day, hour):
    daymap = {'Pazartesi': 0, 'Salı': 1, 'Çarşamba': 2, 'Perşembe': 3, 'Cuma': 4, 'Cumartesi': 5}
    hourmap = {hour: hour - 8 for hour in range(8, 21)}
    return hourmap[hour], daymap[day]


def is_valid(available_slot, student_schedule):
    return np.sum(available_slot * student_schedule) == 0


def schedule_fullness(student_schedule):
    return np.sum(student_schedule)


def get_student_schedules():
    student_occupancies = {}
    student_numbers = get_student_nums(driver)
    with tqdm(total=len(student_numbers)) as pbar:
        for student_num in student_numbers:
            student_occupancies[student_num] = get_schedule_occupancy(driver, student_num)
            fullness = schedule_fullness(student_occupancies[student_num])
            pbar.set_description('Student No: {}  || Fullness: {}'.format(student_num, fullness))
            pbar.update(1)
            if fullness == 0:
                raise Exception('Fullness should not be 0 for {}!'.format(student_num))
    return OrderedDict(sorted(student_occupancies.items(),
                              key=lambda item: schedule_fullness(item[1]),
                              reverse=True))


class Slot:
    def __init__(self, available_slots):
        self.available_slots = available_slots
        self.slot = np.zeros((13, 6))
        for available_slot in available_slots:
            self.slot[mapdayhour2index(available_slot[0], available_slot[1])] = 1
        self.bucket = []

    def __len__(self):
        return len(self.bucket)

    def append(self, value):
        self.bucket.append(value)

    def __str__(self):
        return str(self.available_slots)

    def __repr__(self):
        return self.__str__()

    def students(self):
        return self.bucket


def place_students():
    slots = []
    for requested_slot in REQUESTED_SLOTS:
        slots.append(Slot(requested_slot))
    garbage = []

    for id, schedule in student_occupancies.items():
        slots.sort(key=len)  # increasing order

        appended = False
        for slot in slots:
            if is_valid(available_slot=slot.slot, student_schedule=schedule):
                slot.append(id)
                appended = True
                break

        if not appended:
            garbage.append(id)

    print(COURSE_NAME)
    print('\n'.join(['{} --> {}'.format(str(slot), len(slot)) for slot in slots]))
    print('Garbage Slot Length: {} --> {}'.format(len(garbage), garbage))
    if len(garbage) == 0:
        print('\n\nYey! No more student left to place \m/\n\n')
    return slots, garbage


if __name__ == "__main__":

    # Argument Parser
    parser = argparse.ArgumentParser(description='TOBB ETU Student Lab Placement Tool')
    parser.add_argument('config', type=str, help='Filepath of config.ini')
    args = parser.parse_args()

    # Config Parser
    cp = configparser.ConfigParser()
    cp.read(args.config, encoding='UTF-8')

    COURSE_NAME = cp['course info']['course_name']
    REQUESTED_SLOTS = []
    for section_name, slot_str in cp['requested slots'].items():
        day,hour_interval = slot_str.strip('()').split(',')
        first_hour, last_hour = hour_interval.split('-')
        first_hour, last_hour = int(first_hour.split(':')[0]), int(last_hour.split(':')[0])
        hour_range = list(range(first_hour, last_hour))
        slot = [(day, hour) for hour in hour_range]
        REQUESTED_SLOTS.append(slot)

    # Program Logic
    BASE_URL = 'http://obs.etu.edu.tr:35/DersProgrami#/'
    OUTPUT_PREFIX = '../output/'
    os.makedirs(OUTPUT_PREFIX, exist_ok=True)
    PICKLE_FILEPATH = OUTPUT_PREFIX+COURSE_NAME+'_student_schedules.pkl'
    CSV_OUTPUT_PATH = OUTPUT_PREFIX+COURSE_NAME+'_placement.csv'
    if not os.path.exists(PICKLE_FILEPATH):
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome('../driver/chromedriver.exe', options=chrome_options)
        STUDENT_LIST_URL = BASE_URL + 'sube/ogrencilist/{course_code}/0'.format(course_code=get_coursecode(COURSE_NAME))
        SCHEDULE_URL = BASE_URL + 'dersprogrami/ogrenci/{student_num}'

        student_occupancies = get_student_schedules()
        with open(PICKLE_FILEPATH, 'wb') as f:
            pickle.dump(student_occupancies, f)

    else:
        with open(PICKLE_FILEPATH, 'rb') as f:
            student_occupancies = pickle.load(f)

    slots,garbages = place_students()

    # Save to the csv file
    df = pd.concat([pd.Series(slot.students()) for slot in slots], ignore_index=True, axis=1)
    df = pd.concat((df, pd.Series(garbages)), ignore_index=True, axis=1)
    df.columns = [str(slot) for slot in slots] + ['Garbage']
    df.to_csv(CSV_OUTPUT_PATH, index=False)
    print('Student list save in {}'.format(CSV_OUTPUT_PATH))
