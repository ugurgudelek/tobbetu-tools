import os
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

import configparser
import argparse

import crawler
import pickle
import numpy as np

class Schedule:


    def schedule_row(self, hour, row_arr=None):
        if row_arr is None:
            row_arr = ['-' for day in range(6)]
        return """
    
          <tr>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
            <td>{}</td>
          </tr>
    
        """.format(hour, *row_arr)

    def schedule_header(self):
        return """
        <tr>
            <td><strong>Saat</strong></td>
            <td><strong>Pazartesi</strong></td>
            <td><strong>Salı</strong></td>
            <td><strong>Çarşamba</strong></td>
            <td><strong>Perşembe</strong></td>
            <td><strong>Cuma</strong></td>
            <td><strong>Cumartesi</strong></td>
            </tr>
        """


    def output(self, student, week_arr=None):
        if week_arr is None:
            week_arr = [['-' for day in range(6)] for hour in range(13)]

        TEMPLATE_STR = "<html>"
        TEMPLATE_STR += "<head>"
        TEMPLATE_STR += "<title>Schedule</title>"
        TEMPLATE_STR += "<style>table, th, td { border: 1px solid black; }</style>"
        TEMPLATE_STR += "</head>"
        TEMPLATE_STR += "<body>"
        TEMPLATE_STR += "<table>"
        TEMPLATE_STR += self.schedule_header()
        TEMPLATE_STR += self.schedule_row(hour='8:30-9:20',   row_arr=week_arr[0])
        TEMPLATE_STR += self.schedule_row(hour='9:30-10:20',  row_arr=week_arr[1])
        TEMPLATE_STR += self.schedule_row(hour='10:30-11:20', row_arr=week_arr[2])
        TEMPLATE_STR += self.schedule_row(hour='11:30-12:20', row_arr=week_arr[3])
        TEMPLATE_STR += self.schedule_row(hour='12:30-13:20', row_arr=week_arr[4])
        TEMPLATE_STR += self.schedule_row(hour='13:30-14:20', row_arr=week_arr[5])
        TEMPLATE_STR += self.schedule_row(hour='14:30-15:20', row_arr=week_arr[6])
        TEMPLATE_STR += self.schedule_row(hour='15:30-16:20', row_arr=week_arr[7])
        TEMPLATE_STR += self.schedule_row(hour='16:30-17:20', row_arr=week_arr[8])
        TEMPLATE_STR += self.schedule_row(hour='17:30-18:20', row_arr=week_arr[9])
        TEMPLATE_STR += self.schedule_row(hour='18:30-19:20', row_arr=week_arr[10])
        TEMPLATE_STR += self.schedule_row(hour='19:30-20:20', row_arr=week_arr[11])
        TEMPLATE_STR += self.schedule_row(hour='20:30-21:20', row_arr=week_arr[12])
        TEMPLATE_STR += "</table>"
        TEMPLATE_STR += "</body>"
        TEMPLATE_STR += "</html>"

        os.makedirs('../schedule/', exist_ok=True)
        with open(f'../schedule/{student.no}.html', 'w', encoding='utf-8') as f:
            f.write(TEMPLATE_STR)




class Student:
    def __init__(self, no, name, dep, grade):
        self.no = no  # öğrenci no
        self.name = name  # ad soyad
        self.dep = dep  # bölüm
        self.grade = grade  # sınıf

        self.sections = list()

        self.binary_week_arr = None

    def register_section(self, section):
        self.sections.append(section)

    def get_week_arr(self):
        return self.week_dict_to_arr(self.get_week_dict())

    @staticmethod
    def week_dict_to_arr(week_dict):
        week_arr = []
        for hour, row in week_dict.items():
            row_arr = []
            for day, place in row.items():
                row_arr.append(place)
            week_arr.append(row_arr)
        return week_arr


    def week_arr_to_bin(self, week_arr):
        for i, row in enumerate(week_arr):
            for j, cell in enumerate(row):
                if cell == '-':
                    week_arr[i][j] = 0
                else:
                    week_arr[i][j] = 1

        self.binary_week_arr = np.array(week_arr)
        return self.binary_week_arr

    def get_week_dict(self):
        days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
        hours = ['8:30-9:20',
                 '9:30-10:20',
                 '10:30-11:20',
                 '11:30-12:20',
                 '12:30-13:20',
                 '13:30-14:20',
                 '14:30-15:20',
                 '15:30-16:20',
                 '16:30-17:20',
                 '17:30-18:20',
                 '18:30-19:20',
                 '19:30-20:20',
                 '20:30-21:20']
        week_dict = defaultdict(dict)
        for hour in hours:
            for day in days:
                week_dict[hour][day] = '-'

        for section in self.sections:
            for slot in section.slots:
                week_dict[fix_hour_range(slot.hour)][slot.day] = slot.place

        return week_dict

def fix_hour_range(hour_range):
    first, second = hour_range.split('-')
    fhour,fmin = first.split(':')
    shour, smin = second.split(':')

    # str(int()) for 08:30 -> 8:30
    fhour = str(int(fhour))
    shour = str(int(shour))

    return f"{fhour}:{fmin}-{shour}:{smin}"

class Slot:
    def __init__(self, day, hour, place):
        self.day = day
        self.hour = hour
        self.place = place

    @classmethod
    def parser(cls, schedule_str):
        arr = schedule_str.split('-')
        day = arr[0].strip()
        hour = arr[1].strip() + '-' + arr[2].strip()
        place = arr[3].strip()
        return cls(day, hour, place)

class Section:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.slots = list()

    def add_slot(self, slot):
        self.slots.append(slot)

class Course:
    def __init__(self, code, name):
        self.code = code
        self.name = name
        self.sections = list()


    def add_section(self, section):
        self.sections.append(section)


class University:
    def __init__(self):
        self.students = dict()
        self.courses = dict()



    def read(self, base_dir):
        codes = os.listdir(base_dir)
        for code in tqdm(codes):
            course_dir = os.path.join(base_dir, code)
            with open(os.path.join(course_dir, 'info.txt'), 'r', encoding='utf-8') as f:
                course_name = f.readline()

            course_sample = Course(code=code, name=course_name.strip())

            sections = os.listdir(course_dir)[:-1]  # drop info.txt
            for section in sections:
                section_dir = os.path.join(course_dir, section)
                with open(os.path.join(section_dir, 'info.txt'), 'r', encoding='utf-8') as f:
                    section_schedule_str_list = f.readlines()[1:]  # drop section info

                section_sample = Section(id=section, name=course_name)

                for section_schedule_str in section_schedule_str_list:
                    slot_sample = Slot.parser(section_schedule_str)
                    section_sample.add_slot(slot_sample)

                course_sample.add_section(section_sample)


                section_student_df = pd.read_csv(os.path.join(section_dir, f"{section}.csv"), index_col=0)

                self.add_section_to_students(section_student_df=section_student_df,
                                             section=section_sample)

            self.courses[code] = course_sample


    def add_section_to_students(self, section_student_df, section):

        for index, row in section_student_df.iterrows():

            student = self.students.get(row['Öğrenci No'], None)  # already exist

            if student is None:  # new student
                student = Student(no=row['Öğrenci No'],
                                    name=row['Ad Soyad'],
                                    dep=row['Bölüm'],
                                    grade=row['Sınıf'])

            student.register_section(section=section)

            self.students[row['Öğrenci No']] = student




# Argument Parser
parser = argparse.ArgumentParser(description='TOBB ETU Student Lab Placement Tool')
parser.add_argument('config', type=str, help='Filepath of config.ini')
args = parser.parse_args()

# Config Parser
cp = configparser.ConfigParser()
cp.read(args.config, encoding='UTF-8')

COURSE_CODE = cp['course info']['course_code']
COURSE_NAME = cp['course info']['course_name']
REQUESTED_SLOTS = []
for section_name, slot_str in cp['requested slots'].items():
    day, hour_interval = slot_str.strip('()').split(',')
    first_hour, last_hour = hour_interval.split('-')
    first_hour, last_hour = int(first_hour.split(':')[0]), int(last_hour.split(':')[0])
    hour_range = list(range(first_hour, last_hour))
    slot = [(day, f"{hour}:30-{hour+1}:20") for hour in hour_range]
    REQUESTED_SLOTS.append(slot)


university = University()

if not os.path.exists('university.pickle'):
    university.read('../course_student_list')
    with open('university.pickle', 'wb') as f:
        pickle.dump(university, f)
else:
    with open('university.pickle', 'rb') as f:
        university = pickle.load(f)

course_students_pickle_path = f'{COURSE_CODE}_students.pickle'
if not os.path.exists(course_students_pickle_path):
    crawler.driver_init()
    student_list_link = crawler.BASE_URL+f"sube/ogrencilist/{COURSE_CODE}/0"
    student_list = crawler.student_lists_to_csv(student_list_link, to_csv=False)
    with open(course_students_pickle_path, 'wb') as f:
        pickle.dump(student_list, f)
else:
    with open(course_students_pickle_path, 'rb') as f:
        student_list = pickle.load(f)



def to_week_arrays(requested_slots):
    days = ['Pazartesi', 'Salı', 'Çarşamba', 'Perşembe', 'Cuma', 'Cumartesi']
    hours = ['8:30-9:20',
             '9:30-10:20',
             '10:30-11:20',
             '11:30-12:20',
             '12:30-13:20',
             '13:30-14:20',
             '14:30-15:20',
             '15:30-16:20',
             '16:30-17:20',
             '17:30-18:20',
             '18:30-19:20',
             '19:30-20:20',
             '20:30-21:20']

    week_arrays = []
    for section in requested_slots:
        week_dict = defaultdict(dict)
        for hour in hours:
            for day in days:
                week_dict[hour][day] = 0


        for slot in section:
            week_dict[slot[1]][slot[0]] = 1

        week_arrays.append(Student.week_dict_to_arr(week_dict=week_dict))


    return np.array(week_arrays)


class StudentBucket:
    def __init__(self, name, section_bin_array=None):
        self.name = name
        self.container = list()
        self.section_bin_array = section_bin_array

    def add(self, student):
        self.container.append(student)

    def can_add(self, student):
        if self.section_bin_array is None:
            return True
        student_bin_week_arr = student.week_arr_to_bin(week_arr=student.get_week_arr())
        product = np.sum(self.section_bin_array*student_bin_week_arr)
        if product == 0:  # no section collusion.
            return True
        return False

    def export_students(self):
        pd.DataFrame({'No': [student.no for student in self.container],
                      'Name': [student.name for student in self.container]}).to_csv(f"../output/{COURSE_NAME}_{self.name}.csv", index=False)


    def __len__(self):
        return self.container.__len__()

    def __str__(self):
        return f"{self.name} - Student count: {self.__len__()}"

    def __repr__(self):
        return self.__str__()


class StudentBucketManager:
    def __init__(self, section_bin_arrays):
        self.bucket_count = section_bin_arrays.__len__()
        self.buckets = [StudentBucket(f"section_{i}" ,section_bin_arrays[i]) for i in range(self.bucket_count)]
        self.garbage_bucket = StudentBucket(name='garbage')


    def get_best_available_bucket(self, student):
        """
        return  min size bucket which is available too, or garbage bucket
        """
        min_bucket = None

        available_buckets = [bucket for bucket in self.buckets if bucket.can_add(student)]

        if available_buckets.__len__() == 0:
            return self.garbage_bucket

        for bucket in available_buckets:
            if min_bucket is None or bucket.__len__() < min_bucket.__len__():
                min_bucket = bucket

        return min_bucket

    def export_students(self):
        for bucket in self.buckets:
            bucket.export_students()
        self.garbage_bucket.export_students()




req_bin_week_arrays = to_week_arrays(requested_slots=REQUESTED_SLOTS)
bucketmanager = StudentBucketManager(req_bin_week_arrays)

requested_course_student_nos = student_list[0]['Öğrenci No'].values # replace 0 index with loop for generic
for r_student_no in requested_course_student_nos:

    r_student_no = int(r_student_no)
    u_student = university.students.get(r_student_no, None)
    if u_student is None:
        print(f"Where is {r_student_no}?")
    else:
        bucket = bucketmanager.get_best_available_bucket(u_student)
        bucket.add(u_student)


bucketmanager.export_students()




        # Schedule().output(student=u_student, week_arr=u_student.get_week_arr())


# muho = university.students[171117002]
# week_arr = muho.get_week_arr()
#
# Schedule().output(week_arr=week_arr)
# 181111033