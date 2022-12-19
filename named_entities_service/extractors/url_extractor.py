class UrlExtractor:
    label = "URL"

    def extract(self, doc):
        resultlis = []
        for token in doc:
            if token.like_url:
                resultlis.append((token.text, token.idx, token.idx + len(token)))
        return resultlis

    def __call__(self, doc):
        new_ents = []
        old_ents = list(doc.ents)

        for value, start, end in self.extract(doc):
            span = doc.char_span(start, end, label=self.label)
            if span is None:
                # TODO why can some spans not be created?
                print('Span was none for value {}'.format(value))
                continue
            span._.set('regexp_match', value)
            new_ents += [span]

        doc.ents = old_ents + new_ents
        return doc
