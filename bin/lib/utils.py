import re
import unicodedata


def words_match(word1, word2):
    word1 = unicodedata.normalize('NFD', word1).encode('ascii', 'ignore').decode("utf-8").lower().strip()
    word2 = unicodedata.normalize('NFD', word2).encode('ascii', 'ignore').decode("utf-8").lower().strip()

    return word1 == word2


def make_preview(word):
    res = ""
    for i, part in enumerate(re.split("(\W|\s)", word)):
        if i%2:
            res += part
        else:
            res += "_" * len(part)

    return " ".join(res)
