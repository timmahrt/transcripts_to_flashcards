import re

from sudachipy import tokenizer, dictionary

from app import load_transcripts

# 助動詞 -> Aux verb ('ます', 'です')
POS_IGNORE_LIST = [
    "助詞",
    "感動詞",
    "助動詞",
    "代名詞",
    "接続詞",  # conjunction
    "接頭辞",  # prefix
]

POS_KEEP_LIST = [
    "名詞",  # noun
    "動詞",  # verb
    "形容詞",  # adjective
    "副詞",  # adverb
]


def isOnlyKana(inputStr):
    return bool(re.match(r"^[\u3040-\u309F\u30A0-\u30FFー 　]+$", inputStr))


def isOnlyAlphanumeric(inputStr):
    return bool(re.match(r"^[a-zA-Z0-9]+$", inputStr))


def getTranscriptTexts(url, outputPath, targetLang):
    transcriptData = load_transcripts.loadTranscript(url, outputPath, targetLang)

    return {
        "transcript": [row["text"] for row in transcriptData["transcript"]],
        "title": transcriptData["metadata"]["title"],
        "author": transcriptData["metadata"]["author"],
    }


def printTranscript(texts):
    for text in texts:
        print(text)


def segmentText(text):
    """
    Given a long string of Japanese speech, chunk into phrases

    Currently, this does not work at all
    """
    tokenizerObj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.B

    segments = []
    currentSegment = ""

    for token in tokenizerObj.tokenize(text, mode):
        currentSegment += token.surface()

        if token.part_of_speech()[0] == "補助記号" and token.part_of_speech()[1] == "句点":
            segments.append(currentSegment)
            currentSegment = ""
            print("Hello world")

    # Add the last segment if not empty
    if currentSegment:
        segments.append(currentSegment)

    # for segment in segments:
    #     print(segment)
    #     print("")
    exit(0)

    return segments


def tokenizeText(text):
    tokenizer_obj = dictionary.Dictionary().create()
    mode = tokenizer.Tokenizer.SplitMode.C

    tokens = []
    filteredPosWords = []
    filteredAlphanumericWords = []
    filteredShortKanaWords = []
    for token in tokenizer_obj.tokenize(text, mode):
        word = token.surface()
        pos = token.part_of_speech()[0]
        if pos not in POS_KEEP_LIST:
            filteredPosWords.append(word)
            continue

        if isOnlyAlphanumeric(word):
            filteredAlphanumericWords.append(word)
            continue
        if isOnlyKana(word) and len(word) <= 2:
            filteredShortKanaWords.append(word)
            continue

        tokens.append(token)

    tokensByPos = {}
    for token in tokens:
        word = token.surface()
        pos = token.part_of_speech()[0]
        if pos not in tokensByPos.keys():
            tokensByPos[pos] = []

        tokensByPos[pos].append(token)

    tokensByPos = _filterDuplicates(tokensByPos)

    printSummary(tokensByPos)

    # # Dump stats
    # print(
    #     "----------\n"
    #     "# Ignored by\n"
    #     f"POS: {len(filteredPosWords)}\n"
    #     f"Romaji: {len(filteredAlphanumericWords)}\n"
    #     f"Short kana words: {len(filteredShortKanaWords)}\n"
    # )

    return tokensByPos


def _filterDuplicates(tokensByPos):
    registeredWords = {}
    uniqueTokensByPos = {}
    for pos, tokens in tokensByPos.items():
        uniqueTokensByPos[pos] = []
        for token in tokens:
            key = f"{pos}:{token}"
            if key in registeredWords.keys():
                continue
            registeredWords[key] = ""
            uniqueTokensByPos[pos].append(token)

    return uniqueTokensByPos


def printSummary(tokensByPos):
    print("----------\n" "# Discovered word counts by POS")
    for pos in tokensByPos.keys():
        print(f"{pos}: {len(tokensByPos[pos])}")


def findContexts(texts, word):
    matches = []
    for text in texts:
        if word.surface() not in text:
            continue

        matches.append(text)

    return matches


def listWordsForPos(texts, tokens_by_pos, pos):
    for token in tokens_by_pos[pos]:
        if isOnlyKana(token.surface()):
            print(f"{token}")
        else:
            print(f"{token}({token.reading_form()})")
        for context in findContexts(texts, token):
            print(f"\t- {context}")


def getContextsByPairs(texts, tokens_by_pos):
    contextsByPairs = {}
    for pos, tokens in tokens_by_pos.items():
        for token in tokens:
            key = (pos, token)
            contexts = findContexts(texts, token)
            contextsByPairs[key] = contexts

    return contextsByPairs


if __name__ == "__main__":
    url = "https://www.youtube.com/watch?v=WBA5aS7pHUE"
    outputPath = "./transcripts"
    texts = getTranscriptTexts(url, outputPath, "ja")
    text = "".join(texts)
    tokens_by_pos = tokenizeText(text)
    getContextsByPairs(texts, tokens_by_pos)

    # segmented_phrases = segmentText(text)
    # listWordsForPos(texts, tokens_by_pos, "名詞")
    # printTranscript(text)
    print(text)
    # test()
