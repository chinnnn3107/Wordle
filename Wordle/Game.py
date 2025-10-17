keyword = "CATTY"
attempt = 5
correct = False    
        
while attempt > 0:
    word = input(f"Attempt {attempt}:\n").upper()

    while len(word) != 5 or not word.isalpha():
        print("The word must contain 5 letters, please enter again!")
        word = input(f"Attempt {attempt}:\n").upper()

    if word == keyword:
        correct = True
        print("Correct!")
        break

    for i in range(5):
        if word[i] == keyword[i]:
            print(f"Right place: {word[i]}")
        elif word[i] in keyword:
            print(f"Wrong place: {word[i]}")
        else:
            print(f"Not in keyword: {word[i]}")
    print()
    
    attempt = attempt - 1

if not correct:
    print("You ran out of attemp. The word was:", keyword)


