# todo: delete this file
from PIL import Image
from src.bot import config
import yandex_cloud as yc

folder_id = config.folder_id
iam = config.iam_token
image_path = "D:/hackathons/ttk-bot/pictures/five.jpg"
image = Image.open(image_path)


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


parsed_blocks = yc.parse([image], folder_id, iam)[0]

for i in parse_blocks(parsed_blocks):
    print(i[0])
