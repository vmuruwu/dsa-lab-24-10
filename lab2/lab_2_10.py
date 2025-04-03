# Считываем строку с клавиатуры
input_string = input("Введите строку: ")

# Функция для преобразования символа в заглавный через таблицу ASCII
def to_upper_char(char):
    # Английские буквы a-z
    if ord('a') <= ord(char) <= ord('z'):
        return chr(ord(char) - 32)
    # Русские буквы а-я (кроме ё)
    elif ord('а') <= ord(char) <= ord('я'):
        return chr(ord(char) - 32)
    # Отдельная обработка для буквы ё
    elif char == 'ё':
        return 'Ё'
    return char

# Разбиваем строку на слова вручную (без split())
words = []
current_word = []
in_word = False

for char in input_string:
    if char != ' ':
        current_word.append(char)
        in_word = True
    else:
        if in_word:
            words.append(''.join(current_word))
            current_word = []
            in_word = False
# Добавляем последнее слово, если оно есть
if current_word:
    words.append(''.join(current_word))

# Обрабатываем каждое слово: первая буква - заглавная
processed_words = []
for word in words:
    if word:  # Если слово не пустое
        first_char = to_upper_char(word[0])
        processed_word = first_char + word[1:] if len(word) > 1 else first_char
        processed_words.append(processed_word)

# Собираем строку обратно, сохраняя оригинальные пробелы
result = []
word_index = 0
i = 0
n = len(input_string)

while i < n:
    if input_string[i] != ' ':
        # Вставляем обработанное слово
        if word_index < len(processed_words):
            result.append(processed_words[word_index])
            word_index += 1
            # Пропускаем остальные символы слова
            while i < n and input_string[i] != ' ':
                i += 1
    else:
        result.append(' ')
        i += 1

# Преобразуем список в строку
result = ''.join(result)

# Выводим результат
print("Результат:", result)

