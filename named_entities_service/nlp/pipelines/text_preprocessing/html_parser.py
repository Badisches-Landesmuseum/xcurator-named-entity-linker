from abc import ABC
from html.parser import HTMLParser


# Source: https://stackoverflow.com/questions/31953451/remove-html-tags-and-get-start-end-indices-of-marked-down-text
class HtmlToTextParser(HTMLParser, ABC):
    html_tags = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'br', 'strong', 'span', 'a', 'ul', 'li', 'b',
                 'table', 'thead', 'tbody', 'tr', 'th', 'td', 'b', 'em', 'ins', ]
    embedded_tags = ['br', 'strong', 'span', 'a', 'ul', 'li', 'b', 'em', 'ins']

    def __init__(self, full_page_html: bool = False, *args, **kwargs):
        super(HtmlToTextParser, self).__init__(*args, **kwargs)
        self.is_body = not full_page_html
        self.data = []
        self.test = []
        self.line_len = []
        self.is_temp_tag = False
        self.temp_tag = ""

    def text(self):
        return '\n'.join([x[0] for x in self.data])

    def handle_starttag(self, tag, attrs):
        self.getpos()
        if tag == 'body':
            self.is_body = True
        elif tag == 'footer':
            self.is_body = False

    def handle_endtag(self, tag):

        if tag == 'footer':
            self.is_body = False
        elif self.is_temp_tag and self.temp_tag == tag:
            self.is_temp_tag = False
            self.temp_tag = ""

    def handle_data(self, data):
        if data.strip() and self.lasttag in self.html_tags and self.is_body:
            start_pos = self.getpos()[0]
            end_pos = self.getpos()[1]
            relative_to_root_start = self.start_pos_of_line(start_pos)
            real_start = relative_to_root_start + end_pos
            real_end = real_start + len(data)

            if self.is_embedded_tag():
                self.handle_embedded_tag(real_start, data)
            else:
                self.data.append((data, real_start, real_end, self.lasttag))
                self.is_temp_tag = True
                self.temp_tag = self.lasttag

    def is_embedded_tag(self):
        return self.lasttag in self.embedded_tags and self.is_temp_tag

    def handle_embedded_tag(self, real_start, data):
        previous_data = self.data[-1]
        diff_tags = real_start - previous_data[2]

        new_data = previous_data[0] + " " * diff_tags + data

        previous_tag = previous_data[3]
        previous_start = previous_data[1]

        self.data.remove(previous_data)
        self.data.append((new_data, previous_start, previous_start + len(new_data), previous_tag))

    def start_pos_of_line(self, line):
        pos = 0
        for n in range(line - 1):
            pos += self.line_len[n]
        return pos

    def feed(self, data: str):
        for line in data.splitlines():
            length = len(line) + 1
            self.line_len.append(length)
        self.is_body = not "<head>" in data
        return super().feed(data)
