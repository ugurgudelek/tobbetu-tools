import os
import pandas as pd
from tqdm import tqdm
from collections import defaultdict

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


    def output(self, week_arr=None):
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

        with open('temp.html', 'w', encoding='utf-8') as f:
            f.write(TEMPLATE_STR)




class Student:
    def __init__(self, no, name, dep, grade):
        self.no = no  # öğrenci no
        self.name = name  # ad soyad
        self.dep = dep  # bölüm
        self.grade = grade  # sınıf

        self.sections = list()


    def register_section(self, section):
        self.sections.append(section)

    def get_week_arr(self):
        return self.week_dict_to_arr(self.get_week_dict())

    def week_dict_to_arr(self, week_dict):
        week_arr = []
        for hour, row in week_dict.items():
            row_arr = []
            for day, place in row.items():
                row_arr.append(place)
            week_arr.append(row_arr)
        return week_arr

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
                week_dict[slot.hour][slot.day] = slot.place

        return week_dict

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
            with open(os.path.join(course_dir, 'info.txt'), 'r') as f:
                course_name = f.readline()

            course_sample = Course(code=code, name=course_name.strip())

            sections = os.listdir(course_dir)[:-1]  # drop info.txt
            for section in sections:
                section_dir = os.path.join(course_dir, section)
                with open(os.path.join(section_dir, 'info.txt'), 'r') as f:
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



university = University()
#
university.read('../course_student_list')

muho = university.students[171117002]
week_arr = muho.get_week_arr()

Schedule().output(week_arr=week_arr)