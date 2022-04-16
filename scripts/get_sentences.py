# -*- coding: utf-8 -*-
import random
import string
from collections import defaultdict
from subprocess import Popen, PIPE

# grabbed from stack overflow
import re
alphabets = "([A-Za-z])"
prefixes = "(Mr|St|Mrs|Ms|Dr)[.]"
suffixes = "(Inc|Ltd|Jr|Sr|Co)"
starters = "(Mr|Mrs|Ms|Dr|He\s|She\s|It\s|They\s|Their\s|Our\s|We\s|But\s|However\s|That\s|This\s|Wherever)"
acronyms = "([A-Z][.][A-Z][.](?:[A-Z][.])?)"
websites = "[.](com|net|org|io|gov)"

class Verb:
    def __init__(self, text, base_form, tense, person, number, gender):
        self.text = text
        self.base_form = base_form
        self.tense = tense
        self.person = person
        self.number = number
        self.gender = gender
	
    def __repr__(self):
        return f"Verb(text = {self.text}, base_form = {self.base_form}, tense = {self.tense}, person = {self.person}, number = {self.number}, gender = {self.gender})"
	
    @staticmethod
    def fromFormAndAnalysis(form, analysis):
        text = form
        parts = analysis.split("+")
        base_form = parts[0]
        tense = parts[4]
        person = parts[5]
        number = parts[6]
        gender = parts[7]
        print(form)
        print(analysis)
        return Verb(text, base_form, tense, person, number, gender)
	
def split_into_sentences(text):
    text = " " + text + "  "
    text = text.replace("\n"," ")
    text = re.sub(prefixes,"\\1<prd>",text)
    text = re.sub(websites,"<prd>\\1",text)
    if "Ph.D" in text: text = text.replace("Ph.D.","Ph<prd>D<prd>")
    text = re.sub("\s" + alphabets + "[.] "," \\1<prd> ",text)
    text = re.sub(acronyms+" "+starters,"\\1<stop> \\2",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>\\3<prd>",text)
    text = re.sub(alphabets + "[.]" + alphabets + "[.]","\\1<prd>\\2<prd>",text)
    text = re.sub(" "+suffixes+"[.] "+starters," \\1<stop> \\2",text)
    text = re.sub(" "+suffixes+"[.]"," \\1<prd>",text)
    text = re.sub(" " + alphabets + "[.]"," \\1<prd>",text)
    if "”" in text: text = text.replace(".”","”.")
    if "\"" in text: text = text.replace(".\"","\".")
    if "!" in text: text = text.replace("!\"","\"!")
    if "?" in text: text = text.replace("?\"","\"?")
    text = text.replace(".",".<stop>")
    text = text.replace("?","?<stop>")
    text = text.replace("!","!<stop>")
    text = text.replace("<prd>",".")
    sentences = text.split("<stop>")
    sentences = sentences[:-1]
    sentences = [s.strip() for s in sentences]
    return sentences
# end grabbed from stack overflow 

translation_table = str.maketrans('', '', string.punctuation)

def remove_punctuation(word):
	return word.translate(translation_table)

class Sentence:
    def __init__(self, text):
        self.text = text
        self.words = [remove_punctuation(word) for word in text.split(" ")]

    def __repr__(self):
        return self.text

def main():
    filename = '../data/harry_potter_1_slovene.txt'
    with open(filename) as f:
        lines = f.readlines()

    num_paragraphs = 0
    sentences = []
    for line in lines:
        if not line.strip():
            continue
        num_paragraphs += 1
        sentences.extend(split_into_sentences(line.strip()))

    print(num_paragraphs)
    print(len(sentences))
    sentences = [Sentence(sentence) for sentence in sentences]
    sentences = [s for s in sentences if 8 < len(s.words) < 15]
    random.shuffle(sentences)
    print(len(sentences))
    for sentence in sentences[:1]:
        verbs = []
        print(sentence)
        proc = Popen(('flookup', 'slovene.bin'), stdin=PIPE, stdout=PIPE)
        for word in sentence.words:
            proc.stdin.write(('%s\n' % word.lower()).encode('utf-8'))
        proc.stdin.close()
        parses = defaultdict(set)
        for line in proc.stdout:
            if line.isspace(): continue
            try:
                form, analysis = line.decode('utf-8').strip().split('\t')
            except ValueError:
                print('Bad line from stdout:', line)
                exit(-1)
            parses[form].add(analysis)
        for form, analyses in parses.items():
            verbs.append(Verb.fromFormAndAnalysis(form, analyses))
            print(form)
            for analysis in analyses:
                print('   ' + analysis)
        for verb in verbs:
            print(verb)

if __name__ == '__main__':
    main()
