async def sumOfDigits(num):
    sum = 0
    while num > 0:
        sum += num % 10
        num //= 10
    return sum