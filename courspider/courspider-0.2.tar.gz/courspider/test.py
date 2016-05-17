import json


from faculty_calender import FacultyCalender
from faculty_calender_resources.faculty_of_arts_and_science_calender import FacultyOfArtsAndScienceCalender
from faculty_calender_resources.session import Session
from faculty_calender_resources.session import Season
from faculty_calender_resources.url import URL

cal = FacultyOfArtsAndScienceCalender(Session(2016, Season.FALL),
                                      URL("http://calendar.artsci.utoronto.ca"))

print('getting department calenders')
deps = cal.get_department_calenders()

course_datas = []

print('getting course datas')
for dep in deps:
    for course in dep.get_courses():cF
        course_datas.append(course.to_data())

# print(type(course_datas))
# print(type(course_datas[0]))
# print(type(course_datas[0]['Course code']))

file = open("courses.json", 'w')
file.write(json.dumps({"courses":course_datas}, indent=4))
