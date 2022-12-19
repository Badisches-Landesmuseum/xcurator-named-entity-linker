import re
import unicodedata

from nlp.pipelines.text_preprocessing.html_parser import HtmlToTextParser


class CleanUtil:

    @staticmethod
    def remove_stopwords(doc):
        tokens = [token.text for token in doc if not token.is_stop]

        filtered_text = ' '.join(tokens)
        return filtered_text

    @staticmethod
    def lemmatize_text(doc):
        doc = ' '.join([word.lemma_ if word.lemma_ != '-PRON-' else word.text for word in doc])
        return doc

    @staticmethod
    def strip_html_tags(text: str):
        html_parser = HtmlToTextParser(full_page_html=False)
        html_parser.feed(text)
        return html_parser.text()

    @staticmethod
    def remove_multi_whitespace(text):
        return re.sub(' +', ' ', text)

    @staticmethod
    def remove_short_sentences(text, splitter="\n"):
        sentences = []
        for sentence in text.split(splitter):
            if len(sentence.split(" ")) > 1:
                sentences.append(sentence)
        return "\n".join(sentences)

    @staticmethod
    def strip_sentences(text, splitter="\n"):
        sentences = []
        for sentence in text.split(splitter):
            sentences.append(sentence.strip())
        return "\n".join(sentences)

    @staticmethod
    def remove_accented_chars(text: str):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8', 'ignore')
        return text

    @staticmethod
    def remove_special_characters(text: str, remove_digits=False):
        pattern = r'[^a-zA-züöäÖÄÜß0-9\s\-\&\.\,]' if not remove_digits else r'[^a-zA-züöäÖÄÜß0-9\s\-\&\.\,]'
        text = re.sub(pattern, ',', text)
        return text

    @staticmethod
    def unicodeCleaner(text: str, seperator: bool = False):
        """Clean Unicode Charakters

        Parameters:
        text (str): text to clean
        seperator (boolean) Default = False: If True keep \n,\t,\r

        Returns:
        str:Returning cleaned text

       """
        d = text.replace(u'\xad', u'')
        d = d.replace(u'\xa0', u' ')
        d = d.replace(u'\xa4', u'ä')
        d = d.replace(u'\xb6', u'ö')
        d = d.replace(u'\xbc', u'ü')
        d = d.replace(u'\xc4', u'Ä')
        d = d.replace(u'\xd6', u'Ö')
        d = d.replace(u'\xdc', u'Ü')
        d = d.replace(u'\x9f', u'ß')
        if seperator:
            d = d.replace(u'\n', u'')
            d = d.replace(u'\t', u'')
            d = d.replace(u'\r', u'')
        return d

    @staticmethod
    def removeUmlauts(text: str):
        """Clean (german) Umlaute Charakters

        Parameters:
        text (str): text to clean

        Returns:
        str:Returning cleaned text

        """
        res = text.replace('ä', 'ae')
        res = res.replace('ö', 'oe')
        res = res.replace('ü', 'ue')
        res = res.replace('Ä', 'Ae')
        res = res.replace('Ö', 'Oe')
        res = res.replace('Ü', 'Ue')
        res = res.replace('ß', 'ss')
        return res

    # Handle E-Mail => E | Mail
    @staticmethod
    def expandCompoundToken(text, split_chars="-"):
        new_text = text
        for t in text.split():
            parts = []
            add = False  # signals if current part should be appended to previous part
            for p in t.split(split_chars):  # for each part p in compound token t
                if not p: continue  # skip empty part
                if add and parts:  # append current part p to previous part
                    parts[-1] += p
                else:  # add p as separate token
                    parts.append(p)
                add = len(p) <= 1  # if p only consists of a single character -> append the next p to it

            if len(parts) > 0:
                new_text = new_text.replace(t, " ".join(parts))
        return new_text

    @staticmethod
    def full_clean_html_text(html_content: str,
                             remove_special_chars=True,
                             remove_short_sentences=True,
                             expand_compound_words=True):

        text = CleanUtil.strip_html_tags(html_content)
        text = CleanUtil.remove_multi_whitespace(text)
        text = CleanUtil.strip_sentences(text)
        if remove_short_sentences:
            text = CleanUtil.remove_short_sentences(text)

        if expand_compound_words:
            text = CleanUtil.expandCompoundToken(text)

        if remove_special_chars:
            text = CleanUtil.remove_special_characters(text)

        return text

    switch = {
        1: unicodeCleaner.__get__(object),
        2: removeUmlauts.__get__(object),
        5: expandCompoundToken.__get__(object),
        6: remove_stopwords.__get__(object),
        7: lemmatize_text.__get__(object),
        8: strip_html_tags.__get__(object),
        9: remove_accented_chars.__get__(object)
    }


data = ('Neue    Kommunikation für    eine neue Zeit', 7204, 7247, 'div')
