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
    if response.status_code != 200: 
        ans = []
        with open("words.txt", "r") as file:
            for line in file:
                ans.append(line)
        return ans
    json = response.json()
    return json["words"]



def len_to_words():
    len_to_words = dict()
    for i in range(1000):
        w = words[i]
        len_to_words[len(w)] = len_to_words.get(len(w), list()) + [i]
    return len_to_words


def build_frame():
    h_len = 12 # why not
    ltw = len_to_words()
    h_id = ltw[12][0]
    print(f"horizontal: {words[h_id]}")


if __name__ == "__main__":
    words = get_words()
    build_frame()
