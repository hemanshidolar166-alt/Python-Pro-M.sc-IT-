def report(stud_data):
    print("\nSTUDENT REPORT")
    print("-" * 75)
    print("Rank\tRoll No\tName\t\tTotal\tPercentage\tGrade")
    print("-" * 75)
    for student in stud_data:
        print(
            student["rank"],
            "\t",
            student["roll_no"],
            "\t",
            student["name"],
            "\t\t",
            student["total"],
            "\t",
            student["percentage"],
            "\t\t",
            student["grade"]
        )
    print("-" * 75)