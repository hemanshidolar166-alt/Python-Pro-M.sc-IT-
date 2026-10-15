from datetime import datetime
class Course:
    def __init__(self, code, day, start, end):
        self.code = code
        self.day = day
        self.start = start
        self.end = end

        s = datetime.strptime(start, "%H:%M")
        e = datetime.strptime(end, "%H:%M")

        if s >= e:
            raise ValueError("End time must be after start time")

    def __str__(self):
        return (self.code + " - " + self.day + " - "
                + self.start + " to " + self.end)

class Student:
    def __init__(self, sid, name):
        self.sid = sid
        self.name = name
        self.courses = []

    def add_course(self, course):
        self.courses.append(course)

    def __str__(self):
        return "\nStudent ID: " + self.sid + "\nName: " + self.name

    def check_conflict(self):
        conflict = False

        for i in range(len(self.courses)):
            for j in range(i + 1, len(self.courses)):
                c1 = self.courses[i]
                c2 = self.courses[j]

                if (c1.day.lower() == c2.day.lower()
                    and c1.start < c2.end
                    and c2.start < c1.end):

                    print("Conflict:", c1.code, "and", c2.code)
                    conflict = True

        if not conflict:
            print("No conflict. Student timetable:")
            for c in self.courses:
                print(c)

    def total_courses(self):
        return len(self.courses)

try:
    n = int(input("Enter number of students: "))

    for i in range(n):
        print("\nEnter Student Details")
        sid = input("Student ID: ")
        name = input("Student Name: ")
        s = Student(sid, name)
        m = int(input("Enter number of courses: "))

        for j in range(m):
            print("\nEnter Course Details")
            code = input("Course Code: ")
            day = input("Day: ")
            start = input("Start Time (HH:MM): ")
            end = input("End Time (HH:MM): ")

            c = Course(code, day, start, end)
            s.add_course(c)

        print("\nStudent Information")
        print(s)

        print("\nChecking Timetable")
        s.check_conflict()

        print("Total Registered Courses:", s.total_courses())

except ValueError as e:
    print("Invalid input:", e)

except Exception as e:
    print("Error:", e)