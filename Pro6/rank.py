def rank_stud(stud_data):
    rank_stud = sorted(
        stud_data,
        key=lambda student: student["total"],
        reverse=True
    )
    rank = 0
    previous_total = None
    index = 0
    for student in rank_stud:
        current_total = student["total"]
        if current_total != previous_total:
            rank = index + 1
        student["rank"] = rank
        previous_total = current_total
        index += 1
    return rank_stud