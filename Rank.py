n = int(input("Enter number of students: "))

roll = []
name = []
total = []
percentage = []
grade = []
rank = []

for i in range(n):
    print("\nEnter details of Student", i + 1)

    r = int(input("Enter Roll No: "))
    nm = input("Enter Name: ")

    m1 = float(input("Enter marks of Subject 1: "))
    m2 = float(input("Enter marks of Subject 2: "))
    m3 = float(input("Enter marks of Subject 3: "))
    m4 = float(input("Enter marks of Subject 4: "))
    m5 = float(input("Enter marks of Subject 5: "))

    t = m1 + m2 + m3 + m4 + m5
    p = t / 5

    if p >= 90:
        g = "A+"
    elif p >= 80:
        g = "A"
    elif p >= 70:
        g = "B"
    elif p >= 60:
        g = "C"
    elif p >= 50:
        g = "D"
    else:
        g = "F"

    roll.append(r)
    name.append(nm)
    total.append(t)
    percentage.append(p)
    grade.append(g)


# Sort in descending order of total
for i in range(n):
    for j in range(i + 1, n):
        if total[j] > total[i]:

            total[i], total[j] = total[j], total[i]
            roll[i], roll[j] = roll[j], roll[i]
            name[i], name[j] = name[j], name[i]
            percentage[i], percentage[j] = percentage[j], percentage[i]
            grade[i], grade[j] = grade[j], grade[i]


# Rank
for i in range(n):
    rnk = 1

    for j in range(n):
        if total[j] > total[i]:
            rnk = rnk + 1

    rank.append(rnk)


# Display
print("\nRollNo\tName\tTotal\tPercentage\tGrade\tRank")

for i in range(n):
    print(roll[i], "\t", name[i], "\t", total[i],
          "\t", percentage[i], "%\t\t", grade[i], "\t", rank[i])
