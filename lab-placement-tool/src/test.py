import os
import pandas as pd
from tqdm import tqdm


class Student:
    def __init__(self, no, name, dep, grade):
        self.no = no  # öğrenci no
        self.name = name  # ad soyad
        self.dep = dep  # bölüm
        self.grade = grade  # sınıf

        self.sections = list()

    def register_section(self, section):
        self.sections.append(section)



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

university.read('../course_student_list')

print()
