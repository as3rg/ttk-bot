from PIL import Image
import yandex_cloud as yc
from src.bot import config
import numpy as np
import cv2

folder_id = config.folder_id
iam = config.iam_token
image_path = "C:/Users/Vika/PycharmProjects/ttk-bot/pictures/ticket2-1.jpg"
image = Image.open(image_path)


def crop_frame(img, brightness_threshold=30):
    left, top, right, bottom = image.width, image.height, 0, 0
    for x in range(img.width):
        for y in range(img.height):
            pixel = img.getpixel((x, y))
            left_pixel = img.getpixel((x - 1, y))
            top_pixel = img.getpixel((x, y - 1))
            brightness = sum(pixel) / 3
            left_brightness = sum(left_pixel) / 3
            top_brightness = sum(top_pixel) / 3
            brightness_difference = abs(brightness - left_brightness)
            if brightness_difference > brightness_threshold or brightness_difference > brightness_threshold:
                left = min(left, x)
                right = max(right, x)
                top = min(top, y)
                bottom = max(bottom, y)

    cropped_image = img.crop((left + 5, top + 5, right - 10, bottom - 10))
    return cropped_image


def parse_blocks(blocks):
    data = []
    for block in blocks:
        vertices = block['boundingBox']['vertices']
        try:
            # todo: remove toggle
            cords = (int(vertices[0]['x']), int(vertices[2]['y'])), (int(vertices[0]['x']), int(vertices[2]['y']))
        except:
            data.append(('', ((-1e9, -1e9), (-1e9, -1e9))))
            continue
        words = block['text'].split()
        for word in words:
            data.append((word, cords))
    return data


cropped_1 = crop_frame(crop_frame(image))
cropped_1.save("cropped_image.jpg", "JPEG")

image = cv2.imread("cropped_image.jpg")
image = image[30:image.shape[0] - 30, :]
image_height, image_width = image.shape[:2]
gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0)
edges = cv2.Canny(blurred_image, threshold1=20, threshold2=60)
lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=60, minLineLength=10, maxLineGap=10)

# Группировка горизонтальных отрезков
if lines is not None:
    horizontal_lines = []
    for line in lines:
        x1, y1, x2, y2 = line[0]
        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        if y1 == y2 and length >= (image_width - 20):
            horizontal_lines.append((x1, x2, y1, y2))

    # Сортировка отрезков по y-координате
    horizontal_lines.sort(key=lambda line: line[2])

    # Объединение близко расположенных горизонтальных отрезков
    merged_lines = []
    if horizontal_lines:
        current_line = horizontal_lines[0]
        for line in horizontal_lines[1:]:
            if line[2] - current_line[3] <= 15:  # Проверка расстояния между отрезками
                current_line = (current_line[0], max(current_line[1], line[1]), current_line[2], line[3])
            else:
                merged_lines.append(current_line)
                current_line = line
        merged_lines.append(current_line)


# рисование линий
    for line in merged_lines:
        x1, x2, y1, y2 = line
        length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)
        #print(f"Длина объединенного горизонтального отрезка: {length:.2f} пикселей")


    if len(merged_lines) >= 2:
        #print(merged_lines[-1])
        _, _, y1, _ = merged_lines[-1]
        _, _, y2, _ = merged_lines[-2]
        image = image[y2:y1, :]

cv2.imwrite("cropped_image_mew.jpg", image)

cropped = Image.open('cropped_image_mew.jpg')
parsed_blocks = yc.parse([cropped], folder_id, iam)[0]

parsed = []
for i in parse_blocks(parsed_blocks):
    parsed.append(i[0])

info = {}
for i, word in enumerate(parsed):
    if word == "Поезд":
        info["ПОЕЗД"] = parsed[i + 2]
    elif word == "Вагон":
        info["ВАГОН"] = parsed[i + 2]
    elif word == "Место":
        info["МЕСТО"] = parsed[i + 2]
print(info)

