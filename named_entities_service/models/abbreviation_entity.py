class AbbreviationEntity:
    short_form = ""
    long_forms = []

    def __init__(self, short_form: str, long_forms: set):
        self.short_form = short_form
        self.long_forms = list(long_forms)

    def short_form(self):
        return self.short_form

    def long_forms(self):
        return self.long_forms
