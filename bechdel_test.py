from bs4 import BeautifulSoup
from pathlib import Path
import csv
import time


def get_names_from_files():
    """
            get_names_from_files: reads the name files and sends them back as list
            NOTE: Data source~ http://www.cs.cmu.edu/afs/cs/project/ai-repository/ai/areas/nlp/corpora/names/

            :return list of female and male names

    """

    female_names_list = []
    male_names_list = []
    with open('female.txt', 'r') as f1, open('male.txt', 'r') as f2:
        female_name = f1.read().splitlines()  # remove '\n'
        male_name = f2.read().splitlines()  # remove '\n'

    for fname in female_name:
        female_names_list.append(fname)
    for mname in male_name:
        male_names_list.append(mname)

    # append titles for female names
    female_names_list.append('Ms.')
    female_names_list.append('Mrs.')
    female_names_list.append('Miss')

    # append titles for male names
    male_names_list.append('Mr.')
    male_names_list.append('Sir.')

    return sorted(female_names_list), sorted(male_names_list)


def get_semi_clean_bold_data(parsed_html):
    """
        get_semi_clean_bold_data = returns list containing only speaker names
        NOTE: Speaker is in BOLD or UPPERCASE in script

        :param parsed_html: describe about parameter p1

        :return no_ext_str_row: list that only contains uppercase words other than space, INT., EXT. and END

    """
    # Get the data in <b> tags
    b_list = parsed_html.select("b")

    # Get the rows excluding the spaces
    no_space_row = [item.text.strip() for item in b_list if item is not item.text.strip() != ""]

    # Get the rows excluding the "INT.", "EXT." and "END"
    no_ext_str_row = [item for item in no_space_row if not ("INT." in item or "EXT." in item or "END" in item)]

    return no_ext_str_row


def first_bechdel_score(semi_clean_data, female_names, male_names):
    """
        first_bechdel_score = 'Are there at least two named female characters? '

        :param male_names: contains all male names
        :param semi_clean_data: contains all the speaker names in the given script
        :param female_names: contains all the female names

        :return score: 1 or 0 ~ 1 for two female characters presences
        :return female_characters: list of all female characters present. NOTE: for the second Bechdel criteria
        :return male_characters: list of all male characters present. NOTE: for the third Bechdel criteria

    """
    female_characters = []
    male_characters = []

    for data in semi_clean_data:
        for name in female_names:

            if data.lower() == name.lower() or data.lower().startswith('mrs.') or data.lower().startswith(
                    'ms') or data.lower().startswith('miss'):

                if not female_characters:

                    female_characters.append(data.lower())
                else:
                    # no same name occurrence check
                    if data.lower() not in female_characters:
                        female_characters.append(data.lower())

        for name in male_names:

            if data.lower() == name.lower() or data.lower().startswith('mr.') or data.lower().startswith(
                    'sir.'):

                if not male_characters:

                    male_characters.append(data.lower())
                else:
                    if data.lower() not in male_characters:
                        male_characters.append(data.lower())

    # more than two female characters present?
    if len(female_characters) > 1:
        return 1, female_characters, male_characters
    else:
        return 0, female_characters, male_characters


def second_bechdel_score(semi_clean_data, female_names):
    """
            second_bechdel_score = 'Do these female characters have a conversation with one another? '.

            :param semi_clean_data: contains all the speaker names in the given script
            :param female_names: contains all the female names present in a given script

            :return female_talking: 1 or 0 ~ 1 for two female characters talking to each other
          
    """
    female_talking = 0
    for i in range(0, len(semi_clean_data) - 1):
        if semi_clean_data[i].lower() in female_names and semi_clean_data[i + 1].lower() in female_names and \
                semi_clean_data[i].lower() != semi_clean_data[i + 1].lower():
            female_talking = 1
            break

    return female_talking


def third_bechdel_score(soup, female_names, male_names):
    """
    third_bechdel_score = 'Is there at least one conversation between female characters about something other than a
    man? '.

    :param soup: contains the parsed script
    :param female_names: contains all the female names present in a given script
    :param male_names: contains all the male names present in a given script

    :return score: 1 if two females talk about other than man else 0

    """

    # append references of gender that may appear to be talking about a specific gender

    female_names.append('girl')
    male_names.append('his')
    male_names.append('him')
    male_names.append('he')

    text = soup.get_text()

    # break into lines and remove leading and trailing space on each
    lines = (line.strip() for line in text.splitlines())
    # break multi-headlines into a line each
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    # drop blank lines

    script_lines = []
    for line in chunks:
        if line != "":
            script_lines.append(line.split())  # Split a string into a list where each word is a list item

    # reformat the script to the followingz; [ [speaker,[conversation]], [speaker, [conversation]..]
    conv_holder = []
    speaker = None
    speaker_speaking = None
    speaker_conversation = []
    for i in range(0, len(script_lines)):
        for j in range(0, len(script_lines[i])):
            word = script_lines[i][j]
            if word.isupper() and (word.lower() in female_names or word.lower() in male_names):
                speaker = word
                if speaker is not None and speaker != speaker_speaking:
                    speaker_conversation.append([speaker_speaking, conv_holder])
                    conv_holder = []
            elif not word.isupper():
                speaker_speaking = speaker
                conv_holder.append(word)

    # read conversation between two female characters and check if any male reference comes up
    third_score = 0
    for i in range(0, len(speaker_conversation) - 1):
        first_speaker = speaker_conversation[i][0]
        second_speaker = speaker_conversation[i + 1][0]
        conversation = speaker_conversation[i][1]
        if first_speaker is not None and second_speaker is not None and first_speaker.lower() in female_names and second_speaker.lower() in female_names and first_speaker != second_speaker:
            # analyse of script
            male_presence = False
            for word in conversation:
                if word.lower() in male_names:
                    male_presence = True
            if male_presence == False:
                third_score = 1

    return third_score


def main():
    female_names, male_names = get_names_from_files()

    # iterate over all html files
    start_global = time.time()
    for p in Path('scripts_html/').glob('*.html'):
        start_local = time.time()
        print('analyzing script:', p)

        html = str(p)
        html = "".join(line.strip() for line in html.split("\n"))

        with open(html, encoding="utf-8") as fp:
            soup = BeautifulSoup(fp, 'html.parser')
            semi_clean_data = get_semi_clean_bold_data(soup)

        # FIRST BECHDEL TEST
        first_score, present_female_names, present_male_names = first_bechdel_score(semi_clean_data, female_names,
                                                                                    male_names)

        # SECOND BECHDEL TEST
        second_score = second_bechdel_score(semi_clean_data, present_female_names)

        # Third BECHDEL TEST
        third_score = third_bechdel_score(soup, present_female_names, present_male_names)

        end_local = time.time()
        print('time taken to analyze:' + str(html) +' is:', end_local-start_local )
        print()

        data = [str(html), str(first_score), str(second_score), str(third_score)]

        with open('score_info.csv', 'a') as result_file:
            wr = csv.writer(result_file)
            wr.writerow(data)
    end_global = time.time()
    print('time taken to analyze all scripts: ', (end_global - start_global))


if __name__ == '__main__':
    main()
