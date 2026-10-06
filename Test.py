

while True:
  name = input("what is your name?: ")
  if name == "John":
    print ("provide 3 expenses")
    expenses = [int(input("Expense 1: ")), int(input("Expense 2: ")), int(input("Expense 3: "))]
    total = sum(expenses)
    print(total)
    break
  else:
    print("user not found")