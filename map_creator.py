from PIL import Image
import os

def convert_image_to_map(image_path):
    img = Image.open(image_path)
    img = img.convert("RGBA")  # Конвертируем изображение в RGBA, чтобы работать с альфа-каналом
    width, height = img.size
    pixel_map = []

    for y in range(height):
        row = []
        for x in range(width):
            r, g, b, a = img.getpixel((x, y))  # Получаем RGBA значения пикселя
            if a == 0:  # Если альфа-канал равен 0, пиксель прозрачный
                row.append(' ')  # Добавляем пробел для прозрачного пикселя
            elif (r, g, b) == (0, 0, 0):
                row.append('#')
            elif (r, g, b) == (255, 255, 255):
                row.append('.')
            elif (r, g, b) == (0, 0, 255):
                row.append('c')
            elif (r, g, b) == (255, 0, 0):
                row.append('C')
            elif (r, g, b) == (255, 255, 0):
                row.append('@')
            else:
                row.append('.')
        pixel_map.append(row)  # Добавляем список символов в pixel_map

    return pixel_map

def main():
    image_path = os.path.expanduser(input())  # Используем os для получения пути
    if not os.path.exists(image_path):
        print("Файл не найден. Проверьте путь.")
        return

    result_map = convert_image_to_map(image_path)

    # Выводим результат в нужном формате
    for line in result_map:
        # Переставляем первый символ в конец, добавляем кавычки и запятую
        formatted_line = ''.join(line)
        if formatted_line:  # Проверяем, что строка не пустая
            formatted_line = formatted_line[1:] + formatted_line[0]  # Перемещаем первый символ в конец
            print(f'"{formatted_line}",')  # Добавляем кавычки и запятую

if __name__ == "__main__":
    main()
