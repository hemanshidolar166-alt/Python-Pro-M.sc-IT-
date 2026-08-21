def get_stud_data():
    stud_data = []

    for i in range(5):
        roll_no = input("Enter Roll No: ")
        name = input("Enter Name:")

        mark1 = int(input("Enter Mark 1: "))
        mark2 = int(input("Enter Mark 2: "))
        mark3 = int(input("Enter Mark 3: "))
        mark4 = int(input("Enter Mark 4: "))
        mark5 = int(input("Enter Mark 5: "))

        std_dict = {
            "name": name,
            "roll_no": roll_no,
            "mark1": mark1,
            "mark2": mark2,
            "mark3": mark3,
            "mark4": mark4,
            "mark5": mark5
        }
        stud_data.append(std_dict)
    return stud_data
def get_stud_total(stud_data):
    for stud in stud_data:
        total = (
            stud["mark1"]
            + stud["mark2"]
            + stud["mark3"]
            + stud["mark4"]
            + stud["mark5"]
        )
        percentage = (total / 500) * 100
        stud["total"] = total
        stud["percentage"] = percentage
    return stud_data

def assign_grade(stud_data):
    for student in stud_data:
        percentage = student["percentage"]
        if percentage >= 90:
            student["grade"] = "A+"
        elif percentage >= 80:
            student["grade"] = "A"
        elif percentage >= 70:
            student["grade"] = "B"
        elif percentage >= 60:
            student["grade"] = "C"
        elif percentage >= 50:
            student["grade"] = "D"
        elif percentage >= 40:
            student["grade"] = "E"
        else:
            student["grade"] = "F"
    return stud_data