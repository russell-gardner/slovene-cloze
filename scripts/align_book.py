from copy import deepcopy
from typing import List, Tuple
import math
import re


names = [
    ("Harry", "Harry"),
    ("Hermione", "Hermion"),
    ("Ron", "Ron"),
    ("Vernon", "Vernon"),
    ("Petunia", "Petunij"),
    ("Dudley", "Dudley"),
    ("Marge", "Marge"),
    ("Dursley", "Dursley"),
    ("Dumbledore", "Dumbledore"),
    ("Draco", "Drec"),
    ("Weasley", "Weasley"),
    ("Quirrell", "Smott"),
    ("Flitwick", "Colibr"),
    ("Neville", "Neville"),
    ("McGonagall", "McHudurra"),
    ("Snape", "Raws"),
    ("Binns", "Speed"),
    ("Voldemort", "Mrlakenst"),
]


english_begin_quote = "“"
english_end_quote = "”"
slovene_begin_quote = '"'
slovene_end_quote = '"'


def align_books(english_filename: str, slovene_filename: str, out_filename: str):
    with open(english_filename) as english_file:
        english_lines = english_file.readlines()
    with open(slovene_filename) as slovene_file:
        slovene_lines = slovene_file.readlines()

    print(f"English lines: {len(english_lines)}")
    print(f"Slovene lines: {len(slovene_lines)}")

    english_regex = (
        "(" + english_begin_quote + "[^" + english_end_quote + "]*" + english_end_quote + ")"
    )
    slovene_regex = (
        "(" + slovene_begin_quote + "[^" + slovene_end_quote + "]*" + slovene_end_quote + ")"
    )

    english_chapters = []
    for line in english_lines:
        if line.startswith("CHAPTER"):
            english_chapters.append([])
        english_chapters[-1].append(line)

    slovene_chapters = []
    for line in slovene_lines:
        if line.strip().endswith("poglavje"):
            slovene_chapters.append([])
        slovene_chapters[-1].append(line)

    print(f"English chapters: {len(english_chapters)}")
    print(f"Slovene chapters: {len(slovene_chapters)}")

    for i, (english_lines, slovene_lines) in enumerate(zip(english_chapters, slovene_chapters)):
        print(f"\n\n\nCHAPTER {i+1}\n\n\n")
        english_text = "\n".join(line.strip() for line in english_lines if line.strip())
        slovene_text = "\n".join(line.strip() for line in slovene_lines if line.strip())

        english_segments = re.split(english_regex, english_text)
        slovene_segments = re.split(slovene_regex, slovene_text)

        english_segments = [segment for segment in english_segments if segment.strip()]
        slovene_segments = [segment for segment in slovene_segments if segment.strip()]

        print(f"English segments: {len(english_segments)}")
        print(f"Slovene segments: {len(slovene_segments)}")
        print(f"English characters: {len(english_text)}")
        print(f"Slovene characters: {len(slovene_text)}")

        segmentation = align_segments(english_segments, slovene_segments, 50)
        for i in range(max(len(segmentation.slovene_segments), len(segmentation.english_segments))):
            if i < len(english_segments):
                english_segment = segmentation.english_segments[i]
            else:
                english_segment = "-"
            if i < len(slovene_segments):
                slovene_segment = segmentation.slovene_segments[i]
            else:
                slovene_segment = "-"

            print("\n\n")
            print(i)
            print("ENGLISH:")
            print(english_segment)
            print("SLOVENE:")
            print(slovene_segment)


def match_score(english_text: str, slovene_text: str) -> float:
    name_differences = []
    for english_name, slovene_name in names:
        english_count = english_text.count(english_name)
        slovene_count = slovene_text.count(slovene_name)
        name_differences.append(abs(english_count - slovene_count))
    average_name_difference = sum(name_differences) / len(name_differences)
    english_length_difference = abs(len(english_text) - len(slovene_text)) / len(english_text)
    slovene_length_difference = abs(len(english_text) - len(slovene_text)) / len(slovene_text)
    length_difference = (english_length_difference + slovene_length_difference) / 2

    english_quotes = english_text.count(english_begin_quote)
    slovene_quotes = slovene_text.count(slovene_begin_quote) / 2
    quote_difference = abs(english_quotes - slovene_quotes)

    return 5 * average_name_difference + length_difference + quote_difference


class Segmentation:
    def __init__(self, english_segments: List[str], slovene_segments: List[str]):
        self.english_segments = english_segments
        self.slovene_segments = slovene_segments

    def copy(self) -> "Segmentation":
        return Segmentation(deepcopy(self.english_segments), deepcopy(self.slovene_segments))

    def add_english(self, english_text: str) -> "Segmentation":
        new_segmentation = self.copy()
        new_segmentation.english_segments[-1] += "\n" + english_text
        return new_segmentation

    def add_slovene(self, slovene_text: str) -> "Segmentation":
        new_segmentation = self.copy()
        new_segmentation.slovene_segments[-1] += "\n" + slovene_text
        return new_segmentation

    def add_both(self, english_text: str, slovene_text: str) -> "Segmentation":
        new_segmentation = self.copy()
        new_segmentation.english_segments.append(english_text)
        new_segmentation.slovene_segments.append(slovene_text)
        return new_segmentation

    def last_segment_match_score(self) -> float:
        return match_score(self.english_segments[-1], self.slovene_segments[-1])


def align_segments(
    english_segments: List[str], slovene_segments: List[str], search_width: int
) -> Segmentation:
    chart: List[Tuple[float, float, Segmentation]] = []
    for _ in english_segments:
        chart.append([(1000.0, 1000.0, None)] * len(slovene_segments))

    for english_index in range(len(english_segments)):
        if english_index % 100 == 0:
            print(english_index)
        min_slovene_index = max(0, english_index - search_width)
        max_slovene_index = min(len(slovene_segments), english_index + search_width)
        for slovene_index in range(min_slovene_index, max_slovene_index):
            english_text = english_segments[english_index]
            slovene_text = slovene_segments[slovene_index]
            if english_index == 0 and slovene_index == 0:
                segmentation = Segmentation([english_text], [slovene_text])
                previous_score = 0.0
                current_score = match_score(english_text, slovene_text)
                chart[english_index][slovene_index] = (previous_score, current_score, segmentation)
                continue

            options: List[Tuple[float, Tuple[float, float, Segmentation]]] = []

            if slovene_index > 0 and chart[english_index][slovene_index - 1][-1] is not None:
                # Add to slovene segment
                previous_score, _, segmentation = chart[english_index][slovene_index - 1]
                new_segmentation = segmentation.add_slovene(slovene_text)
                current_score = new_segmentation.last_segment_match_score()
                chart_entry = (previous_score, current_score, new_segmentation)
                options.append((previous_score + current_score, chart_entry))
            if english_index > 0 and chart[english_index - 1][slovene_index][-1] is not None:
                # Add to english segment
                previous_score, _, segmentation = chart[english_index - 1][slovene_index]
                new_segmentation = segmentation.add_english(english_text)
                current_score = new_segmentation.last_segment_match_score()
                chart_entry = (previous_score, current_score, new_segmentation)
                options.append((previous_score + current_score, chart_entry))
            if english_index > 0 and slovene_index:
                # Start new segment
                previous_score, _, segmentation = chart[english_index - 1][slovene_index - 1]
                new_segmentation = segmentation.add_both(english_text, slovene_text)
                current_score = new_segmentation.last_segment_match_score()
                chart_entry = (previous_score, current_score, new_segmentation)
                options.append((previous_score + current_score, chart_entry))

            options.sort(key=lambda x: x[0])
            chart[english_index][slovene_index] = options[0][1]

    return chart[-1][-1][-1]


if __name__ == "__main__":
    align_books(
        "data/harry_potter_1_english.txt",
        "data/harry_potter_1_slovene.txt",
        "data/harry_potter_1_aligned.tsv",
    )
