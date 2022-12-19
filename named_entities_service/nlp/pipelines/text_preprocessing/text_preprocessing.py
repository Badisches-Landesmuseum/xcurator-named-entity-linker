import re
import unicodedata

from nlp.pipelines.text_preprocessing.html_parser import HtmlToTextParser


class TextPreprocessing:

    # https://spacy.io/usage/training
    @staticmethod
    def get_start_end_char_positions(text, word):
        start = text.lower().find(word.lower())
        return start, start + len(word)

    @staticmethod
    def replace_with_whitespace(text: str, regex_pattern: re):
        return re.sub(regex_pattern, TextPreprocessing.replace_pattern_match_with_whitespace, text)

    @staticmethod
    def remove_multi_whitespace(text: str):
        return re.sub(' {2,}', " ", text)

    @staticmethod
    def replace_pattern_match_with_whitespace(m):
        return ' ' * len(m.group())

    @staticmethod
    def handle_html_entities(text: str):
        text = text.replace("&nbsp;", "      ") \
            .replace("&lt;", " <  ") \
            .replace("&gt;", "  > ") \
            .replace("&amp;", "&") \
            .replace("&quot;", " \"    ") \
            .replace("&apos;", " '    ") \
            .replace("&cent;", " ¢    ") \
            .replace("&pound;", " £     ") \
            .replace("&yen;", " ¥   ") \
            .replace("&euro;", " €    ") \
            .replace("&copy;", " ©    ") \
            .replace("&reg;", " ®   ")

        return TextPreprocessing.replace_with_whitespace(text, r'^(?:&[a-z]{2,};)|^(?:&#[0-9]{2,};)')

    @staticmethod
    def accented_chars_to_chars(text: str):
        return str(unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore'))

    @staticmethod
    def remove_quotation_mark(text: str):
        return TextPreprocessing.replace_with_whitespace(text, r'[\'\"]+')

    @staticmethod
    def remove_brackets(text: str):
        return TextPreprocessing.replace_with_whitespace(text, r'[\(\)\[\]\{\}]+')

    @staticmethod
    def default_html_cleaning(html_content: str):
        return TextPreprocessing.handle_html_entities(html_content)

    @staticmethod
    def default_text_cleaning(text: str):
        # text = accented_chars_to_chars(text) bug ß -> n etc..
        text = TextPreprocessing.remove_quotation_mark(text)

        text = text.replace(" .", ". ") \
            .replace(" ,", ", ") \
            .replace(" :", ": ")
        return text

    multiple_whitespaces_in_text_regex = re.compile(' {2,}')
    multiple_whitespaces_in_text_regex = re.compile('ß')

    # POSITIONING BETWEEN ORIGINAL TEXT AND CLEANED TEXT
    @staticmethod
    def whitespace_to_position_map_handling(text: str):
        position_map = []

        # remove leading whitespace
        leading_striped_text = text.lstrip()
        leading_striped_length_diff = len(text) - len(leading_striped_text)
        position_map.insert(0, [0, leading_striped_length_diff])

        # remove tailing whitespace
        tailing_striped_text = leading_striped_text.rstrip()
        tailing_striped_length_diff = len(leading_striped_text) - len(tailing_striped_text)

        # remove whitespace in between with positions
        previous_removed_whitespace_count = 0
        for multi_whitespace_match in TextPreprocessing.multiple_whitespaces_in_text_regex.finditer(
                tailing_striped_text):
            match_start_position = multi_whitespace_match.start() - previous_removed_whitespace_count + 1

            # replace multi whitespaces with a single whitespace | 4 whitespaces will be 3 whitespaces -> -1
            current_char_remove_count = multi_whitespace_match.end() - multi_whitespace_match.start() - 1
            orig_clean_text_dela_count = current_char_remove_count + previous_removed_whitespace_count + leading_striped_length_diff

            position_map.append([match_start_position, orig_clean_text_dela_count])
            tailing_striped_text = tailing_striped_text[
                                   :multi_whitespace_match.start() - previous_removed_whitespace_count] + " " + tailing_striped_text[
                                                                                                                multi_whitespace_match.end() - previous_removed_whitespace_count:]

            previous_removed_whitespace_count = previous_removed_whitespace_count + current_char_remove_count

        # if tailing_striped_length_diff > 0:
        position_map.append([len(tailing_striped_text), tailing_striped_length_diff + position_map[-1][1]])

        return tailing_striped_text, position_map

    @staticmethod
    def orig_text_to_cleaned_text_position_delta(position_map, pos):
        for i in range(len(position_map) - 1):
            if position_map[i][0] <= pos < position_map[i + 1][0]:
                return position_map[i][1]
        return 0

    @staticmethod
    def orig_text_to_cleaned_text_position(position_map, clean_text_position, context_start_position=0):
        for i in range(len(position_map) - 1):
            if position_map[i][0] <= clean_text_position < position_map[i + 1][0]:
                return context_start_position + clean_text_position + position_map[i][1]
            # elif
        return context_start_position + clean_text_position

    @staticmethod
    def text_preprocessing(html_content: str):
        parser = HtmlToTextParser()  # a list of text with the deleted position
        parser.feed(html_content)
        content = parser.data  # including the orginal position of the text.

        named_entity_content = []
        sentiment_content = []
        for text, start, end, tag in content:  # tag relates to HTML Tags
            text = TextPreprocessing.default_text_cleaning(text)
            text = TextPreprocessing.replace_with_whitespace(
                text, r'[^a-zA-züöäÖÄÜßèé0-9\s\-\&\/\(\)\.:@€%*\{\}\[\]]')
            sentiment = TextPreprocessing.replace_with_whitespace(
                text, r'[^a-zA-züöäÖÄÜß]').lower().strip()
            sentiment = TextPreprocessing.remove_multi_whitespace(
                sentiment)  # Normal cleaning without the text positions

            text, position_map = TextPreprocessing.whitespace_to_position_map_handling(
                text)
            sentiment_content.append(sentiment)
            named_entity_content.append(
                (text, start, end, tag, position_map))  # named_entity_content usage for entity linker

        sentiment_text = '\n'.join(sentiment_content)
        return named_entity_content, sentiment_text

    @staticmethod
    def preprocess_text(html_text: str):
        html_text = TextPreprocessing.default_html_cleaning(html_text)
        return TextPreprocessing.text_preprocessing(html_text)
