# Генерируем случайные, не более, чем 6-значные, числа
import random

N = 550               # Количество номеров
numbers = set()
while len(numbers) < N:
    numbers.add(random.randrange(1000000))

# Преобразуем в строку и добавляем ведущие нули
numbers = [str(num).zfill(6) for num in numbers]

# Сохраняем в текстовый файл
with open('numbers.txt', 'w') as f:
    f.writelines(n + '\n' for n in numbers)
