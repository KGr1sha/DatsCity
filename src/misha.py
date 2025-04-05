import numpy as np
import json
import requests
import copy
import os
from dotenv import load_dotenv
import matplotlib.pyplot as plt

vectors = []
first_letter_coords = []
ids = []

load_dotenv()
words_url = "https://games-test.datsteam.dev/api/words"
build_url = "https://games-test.datsteam.dev/api/build"
towers_url = "https://games-test.datsteam.dev/api/towers"
token = os.getenv("TOKEN")
headers = {
    "X-auth-token": token
}

def get_words():
    response = requests.get(words_url, headers=headers)
    if response.status_code != 200: 
        ans = []
        with open("src/words.txt", "r") as file:
            for line in file:
                ans.append(line)
        return ans
    json = response.json()
    return json["words"]

words = get_words()
placed_words = []

def reset_words_map():
    return np.zeros((30, 30, 100)).astype(str)

def reset_viz_map():
    return np.zeros((30, 30, 100)).astype(int)

def reset_boolean_map():
    return np.zeros((30, 30, 100)).astype(bool)

def get_words_by_len():
    """
    Создает словарь len_word_dict у которого ключ - длина, а значение - массив из id слов
    """
    len_word_dict = {}
    for i in range(1000):
        word = words[i]
        if len(word) not in len_word_dict.keys():
            len_word_dict[len(word)] = [i]
        else:
            len_word_dict[len(word)].append(i)

    return len_word_dict

# Создаю словарь где ключ длина а значение массив с словами этой длины
len_word_dict = get_words_by_len()
sorted_lens = sorted(list(len_word_dict.keys()), reverse=True)

# Словарь векторов направления от первой буквы
vecs = {
    'x': np.array([1, 0, 0]),
    'y': np.array([0, 1, 0]),
    'z': np.array([0, 0, -1])
}

dir_to_n = {
    "z": 1,
    "x": 2,
    "y": 3
}

"""
У нас будет следующий подход:
Ставится первое слово, на него с заданным GAP'ом ставятся длинные слова по вертикали
Далее ставится возможное слово которое будет пересекать данные длинные слова по горизонтали
у этого возможного слова задается начальная (минимальная) длина

после построения такого слова мы будем ставить на нем новые вертикальные слова
и стараться поставить горизонтальное слово так, чтобы оно пересекало только 2 вертикальных слова

алгоритм повторяется - получается высокая башня
"""

def find_max_length_z(letter, coords):
    """
    Находит слово максимальной длины подходящее под текущую букву с учетом уровня

    ALERT ЭТА ФУНКЦИЯ НЕ УЧИТЫВАЕТ ПОВТОР СЛОВ!

    есть еще небольшой баг если слово опускается вплотную до слова по горизонтали, по правилам так нельзя
    но такое происходит редко
    """
    x, y, z = coords # координаты текущей буквы
    if boolean_map_z[x, y, z] or x >= 30 or y >= 30 or z >= 30: # проверяем что по оси z что на этой координате можно разместить букву по оси z
        return (None, [0, 0, 0])
    layer = coords[2] # достаем уровень текущей буквы
    for length in sorted_lens: # идем в порядке убывания длины по нашему dict'у
        for word_id in len_word_dict[length]: # перебираем слова
            word = words[word_id]
            for i in range(1, min(len(word), layer + 2)): # данным циклом я проверяю, насколько ниже можно опустить потенциальное слово относительно этой буквы
                possible_letter = word[-i]
                flag = True
                if letter == possible_letter:
                    for ind, possible_letters in enumerate(word[-i:]): # цикл для провреки что все буквы ушедшие вниз - стоят на валидных местах
                        if not(boolean_map_z[x, y, z - ind]) and (words_map[x, y, z - ind] == '0.0' or words_map[x, y, z - ind] == possible_letters):
                            pass
                        else:
                            print(f'ALERT {boolean_map_z[x, y, z - ind], words_map[x, y, z - ind], possible_letters, letter}')
                            flag = False
                            break
                    if flag:
                        # print(f'ALERT SOMETHING HERE {word}, {coords}, {len(word) - i}, i {i}, LETTER {letter}')
                        return word_id, coords + np.array([0, 0, len(word) - i]) # возвращаем потенциальное слово и координаты его первой буквы
    return (None, [0, 0, 0])


def word_to_id():
    wti = dict()
    for i in range(1000):
        w = words[i]
        wti[w] = i
    return wti

word_to_id = word_to_id()

def first_word(FIRST_LEN=11):
    """
    выбирает первое слово для башни случайным образом заданной длины
    """
    ind = np.random.randint(0, len(len_word_dict[FIRST_LEN]))
    
    return len_word_dict[FIRST_LEN][ind]
    
def create_vertical_word(word_id, first_letter_coord, GAP=5):
    """
    Ставит вертикально слова которые получает из функции find_max_length_z
    с гиперпараметром GAP (минимальное расстояние)
    """
    word = words[word_id]
    gap = 0
    letter_coord = first_letter_coord.copy()
    layers = [] # массив для записи наших высоты чтобы потом найти минимум из двух
    letters_coords = [] # хранит координаты букв для следующего горизонтального слова
    for letter in word:
        word_id, new_coords = find_max_length_z(letter, letter_coord)
        if word_id == None: return (None, None)

        word = words[word_id]
        letter_coord += vecs['x']
        if word != 'None' and not(gap):
            print(f'ALERT {word}, {new_coords}')
            put_word(word_id, new_coords, 'z')
            layers.append(new_coords[2])
            gap += GAP
            letters_coords.append(new_coords)
        elif gap:
            gap -= 1
    min_layer = letter_coord[2] # ВЫСОТА ГОРИЗОНТАЛЬНОГО СЛОВА
    for i in range(len(letters_coords)):
        letters_coords[i][2] = min(layers)
    return (letters_coords, min_layer)
    

def create_horizontal_word(letters_coords, min_layer, LEN_WORD=12):
    """
    Функция которая ставит горизонтально слова в зависимости от
    координат двух вертикальных слов
    LEN_WORD - длина горизонтального слова
    """
    
    gap = letters_coords[1][0] - letters_coords[0][0] # считаем получившийся гап между словами
    max_layer = letters_coords[0][2].copy() # берем топ леер
    while LEN_WORD <= max(len_word_dict.keys()):
        if LEN_WORD not in len_word_dict.keys():
            break
        temp_letters_coords = copy.deepcopy(np.array(letters_coords))
        current_layer = max_layer.copy()
        # print(f'updating current_layer {current_layer} {temp_letters_coords[1][2]}')
        while current_layer != min_layer + 1:
            letters = ''
            for letter_coords in temp_letters_coords:
                letters += words_map[*letter_coords]
            for word_id in len_word_dict[LEN_WORD]:
                word = words[word_id]
                flag = True
                x, y, z = letters_coords[0]
                for ind, letter in enumerate(word):
                    if x + ind >= 30 or words_map[x + ind, y, current_layer] == '0.0' or words_map[x + ind, y, current_layer] == letter:
                       pass
                    else:
                        flag = False
                        break
                if flag:
                    # print(f'ALERT HORIZONTAL WORD {word}, coords {temp_letters_coords[0]}')
                    put_word(word_id, temp_letters_coords[0], 'x')
                    return word_id, temp_letters_coords[0]
            for i in range(len(letters_coords)):
                temp_letters_coords[i] += [0, 0, -1]
            current_layer -= 1
        LEN_WORD += 1
        print(f'WARNING {current_layer, min_layer}')
    return None, [0, 0, 0]

def mega_print():
    print(real_words)
    for line in words_map[10:23, 10, 0:21][::-1]:
        new_line = line.copy()
        for ind, letter in enumerate(new_line):
            if letter == '0.0':
                new_line[ind] = 'n'
        print(*new_line[::-1])



def put_word(word_id, start_coord, direction):
    """
    Размещает слово на words_map и viz_map для визуализации
    """
    word = words[word_id]
    vec = vecs[direction]
    print(f'СТАВИТСЯ СЛОВО {word} vec {vec}')
    real_words.append(word)
    coord = start_coord.copy()
    placed_words.append({
        "dir": dir_to_n[direction],
        "id": word_id,
        "pos": start_coord.tolist()
    })
    for letter in word:
        x, y, z = coord
        if direction == 'x':
            boolean_map_x[max(0, x - 1):min(100, x + 2), max(0, y - 1):min(100, y + 2), max(0, z - 1):min(100, z + 2)] = 1
        elif direction == 'y':
            boolean_map_y[max(0, x - 1):min(100, x + 2), max(0, y - 1):min(100, y + 2), max(0, z - 1):min(100, z + 2)] = 1
        elif direction == 'z':
            boolean_map_z[max(0, x - 1):min(100, x + 2), max(0, y - 1):min(100, y + 2), max(0, z - 1):min(100, z + 2)] = 1
        words_map[*coord] = letter
        viz_map[*coord] = 1
        coord += vec
    mega_print()

real_words = []
words_map = reset_words_map()
viz_map = reset_viz_map()
boolean_map_x = reset_boolean_map()
boolean_map_y = reset_boolean_map()
boolean_map_z = reset_boolean_map()


first_coords = np.array([10, 10, 0])
word_id = first_word()
put_word(word_id, first_coords, 'x')
coords = first_coords.copy()

flag = True
while flag:
    print("creating vertical with id: ", word_id)
    letters_coords, min_layer = create_vertical_word(word_id, coords)
    if letters_coords == None or len(letters_coords) <= 1:
        print(f'не удалось поставить 2 слова, но получилось ')
        flag = False
        break
    word_id, coords = create_horizontal_word(letters_coords, min_layer)
    print("got word id: ", word_id)
    word = words[word_id]
    if word == None:
        print('не удалось поставить горизонтальное слово')
        flag = False


"""
ВАЖНО!
Мой код не учитывает границы карты, поэтому
на графике видно что по x доходит до 30 и все
"""


# Генерация большого 3D массива
np.random.seed(42)
array = viz_map.copy()

# Создание булевых масок для кубов
filled = array != 0
colors = np.empty(array.shape, dtype=object)
colors[array == 1] = "green"
colors[array == -1] = "red"

# Визуализация
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

ax.voxels(filled, facecolors=colors, edgecolor="k", linewidth=0.1)

# Установка начального угла
ax.view_init(elev=30, azim=45)
plt.show()
send = input("send? (y/n)")
if send == "y":
    data = {
        "done": True,
        "words": placed_words
    }
    print(data)
    response = requests.post(build_url, headers=headers, json=data)
    if response.status_code != 200:
        print(response)
        print(response.text)
    else:
        res = requests.get(towers_url, headers=headers)
        if res.status_code != 200:
            printf("failed to get towers\n", res.text)
        else:
            json_towers = res.json()
            with open ("towers.json", "w") as f:
                json.dump(json_towers, f, indent=2)
elif send == "n":
    response = requests.get(words_url, headers=headers)
    if response.status_code != 200: print("failed to get next turn time")
    nextturn = response.json()["nextTurnSec"]
    print(f"next turn in {nextturn} seconds")
