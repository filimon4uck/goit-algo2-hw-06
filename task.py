from collections import Counter
from concurrent.futures import ThreadPoolExecutor
import matplotlib.pyplot as plt
import requests


def get_text(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Перевірка на помилки HTTP
        print("-----------------------------------------")
        print(response.text)
        return response.text
    except requests.RequestException as e:
        print(f"Error getting text from {url}: {e}")
        return None


def tokenize_text(text_chunk):
    words = []
    word = ""
    for char in text_chunk.lower():
        if char.isalnum():
            word += char
        elif word:
            words.append(word)
            word = ""
    if word:
        words.append(word)

    return Counter(words)


def merge_word_counts(first_counter, second_counter):
    first_counter.update(second_counter)
    return first_counter


def reduce_function(key_values):
    key, values = key_values
    return key, sum(values)


def visualize_top_words(word_counts, top_n=10):
    top_words = word_counts.most_common(top_n)
    words, counts = zip(*top_words)
    plt.figure(figsize=(10, 6))
    plt.barh(words, counts, color="skyblue")
    plt.title(f"Топ {top_n} слів за частотою використання")
    plt.ylabel("Слова")
    plt.xlabel("Частота")
    plt.gca().invert_yaxis()
    plt.show()


def process_text_analysis(url, num_threads=4, top_n=10):
    text = get_text(url)
    if not text:
        print("Помилка: Не вдалося отримати текст")
        return
    chunk_size = max(len(text) // num_threads, 1)
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        counters = list(executor.map(tokenize_text, chunks))
    total_word_count = Counter()
    for counter in counters:
        total_word_count = merge_word_counts(total_word_count, counter)
    visualize_top_words(total_word_count, top_n)


if __name__ == "__main__":
    # Вхідний текст для обробки
    url = "https://gutenberg.net.au/ebooks06/0606201.txt"

    process_text_analysis(url, num_threads=4, top_n=10)
