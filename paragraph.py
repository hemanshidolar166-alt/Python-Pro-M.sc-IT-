text = input("Enter a paragraph: ")
#remove punction
punc = ".,!?;:'\"()-[]{}<>/\\@#$%^&*_+=|`~"
new_text = ""
for ch in text:
    if ch in punc:
        new_text = new_text + " "
    else:
        new_text = new_text + ch

#Split into words and store in list
words = new_text.lower().split()

#1.Total number of words
print("Total number of words=",len(words))

#2.Number of unique words
unique = []
for w in words:
    if w not in unique:
        unique.append(w)
print("Number of unique words =",len(unique))

#3.Longest word(s)
max_len = len(words[0])
for w in words:
    if len(w) > max_len:
        max_len = len(w)

print("Longest word(s):")
for w in unique:
    if len(w) == max_len:
        print(w)

#4.Shortest word(s)
min_len = len(words[0])
for w in words:
    if len(w) < min_len:
        min_len = len(w)

print("Shortest word(s):")
for w in unique:
    if len(w) == min_len:
        print(w)

#5.Words appearing more than once
print("Words appearing more than once:")
found = False

for w in unique:
    count = 0
    for x in words:
        if w == x:
            count += 1
    if count > 1:
        print(w, "->", count, "times")
        found = True

if found == False:
    print("No repeated words")

#Display words in alphabetical order
unique.sort()

print("\nWords in alphabetical order:")
for w in unique:
    print(w)

# Search a word and display all positions
search = input("\nEnter a word to search: ").lower()

pos = []
for i in range(len(words)):
    if words[i] == search:
        pos.append(i)

if len(pos) > 0:
    print("Word found at positions:", pos)
else:
    print("Word not found")
