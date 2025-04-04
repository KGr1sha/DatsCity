import os
from dotenv import load_dotenv
import requests

load_dotenv()
words_url = "https://games-test.datsteam.dev/api/words"
token = os.getenv("TOKEN")
headers = {
    "X-auth-token": token
}

map_size = [30, 30, 100]
current_tower = list(list(list()))
words = list()

def get_words():
    response = requests.get(words_url, headers=headers)
    if response.status_code != 200: return None
    json = response.json()
    return json["words"]

def count_letters():
    letters = dict()
    for word in words:
        for letter in word:
            letters[letter] = letters.get(letter, 0) + 1
    return letters

def count_word_len(words: list):
    lengths = dict()
    for i in range(1000):
        w = words[i]
        lengths[len(w)] = lengths.get(len(w), list())
        lengths[len(w)].append(i)
    return lengths

def find_word_of_min_len(n, words):
    for i in range(len(words)):
        w = words[i]
        if len(w) >= n:
            return i, w
    return -1, ""


def find_horizontal(end_letter):
    for i in range(1000):
        w = words[i]
        if w[-1] == end_letter:
            return i
    return -1


def build_frame():
    built_words = dict()
    lengths = count_word_len(words)
    lengths_count = [{x: len(words[x])} for x in lengths.keys()]
    lengths_sorted = list(lengths.keys())
    print(lengths_count)
    needed_len = lengths_sorted[int(len(lengths_sorted)/2)]
    first_id = lengths[needed_len][0]
    first_w = words[first_id]
    print(f"horizontal: {first_w}")
    first_offset = -1
    first_up = -1
    for i in range(len(first_w)):
        first_letter = first_w[i]
        first_up = find_horizontal(first_letter)
        if first_up != -1:
            first_offset = i
            break
    first_up_w = words[first_up]
    print(first_offset, first_up_w)

    
    last_letter = first_w[-1]
    second_up = find_horizontal(last_letter)
    if second_up == -1:
        print("i'm gay (could not find second up)")
        return
    second_up_w = words[second_up]

    built_words[first_id] = {
        "pos": [10, 10, 0],
        "dir": [1, 0, 0]
    }
    built_words[first_up] = {
        "pos": [10, 10, len(first_up_w)],
        "dir": [0, 0, -1]
    }
    built_words[second_up] = {
        "pos": [10 + len(first_w), 10, len(second_up_w)],
        "dir": [0, 0, -1]
    }


#    highest_point = min(len(first_up_w), len(second_up_w))
#    lowest_point = 2
#    #       w_id   a   b
#    found = [-1, -1, -1]
#
#    print(f"horizontal: {first_w}")
#    print(f"first up: {first_up_w}")
#    print(f"second up: {second_up_w}")
#    for height in range(highest_point, lowest_point, -1):
#        print(f"height: {height}")
#        letter_a = first_up_w[-height]
#        letter_b = second_up_w[-height]
#        print(f"a: {letter_a}\nb: {letter_b}")
#        for i in range(len(words)):
#            w = words[i]
#            first_pos = w.find(letter_a)
#            if first_pos == -1: continue
#            second_pos = first_pos + len(first_w)
#            if second_pos < len(w) and w[second_pos] == letter_b:
#                print(w)
#                print(f"first_pos: {first_pos} second_pos: {second_pos}")
#                found = [i, first_pos, second_pos]
#                break
#
#

if __name__ == "__main__":
    words = get_words()
    if words != None:
        with open('words.txt', 'w') as file:
            for w in words:
                file.write(w + "\n")
    else:
        words = list()
        with open("words.txt", "r") as file:
            for line in file:
                words.append(line)
    letters = count_letters()
    build_frame()
