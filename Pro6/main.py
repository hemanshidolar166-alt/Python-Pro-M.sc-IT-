from student import get_stud_data, get_stud_total, assign_grade
from rank import rank_stud
from Report import report

std_data = get_stud_data()
stud_total = get_stud_total(std_data)
report_data = assign_grade(stud_total)
ranked_data = rank_stud(report_data)
report(ranked_data)

for student in ranked_data:
    print("Roll No:", student["roll_no"])
    print("Name:", student["name"])
    print("Mark 1:", student["mark1"])
    print("Mark 2:", student["mark2"])
    print("Mark 3:", student["mark3"])
    print("Mark 4:", student["mark4"])
    print("Mark 5:", student["mark5"])
    print("Total:", student["total"])
    print("Percentage:", student["percentage"])
    print("Grade:", student["grade"])
    print("Rank:", student["rank"])
   