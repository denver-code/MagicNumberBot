import datetime

now = datetime.datetime.now()

def sum_of_digits(num):
    sum = 0
    while num > 0:
        sum += num % 10
        num //= 10
    return sum

print(sum_of_digits(now.year))