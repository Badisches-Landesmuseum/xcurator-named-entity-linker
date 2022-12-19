from spacy.lang.char_classes import ALPHA, ALPHA_LOWER, ALPHA_UPPER, LIST_ELLIPSES, LIST_ICONS
from spacy.lang.de.punctuation import _quotes
from spacy.tokenizer import Tokenizer
from spacy.util import compile_infix_regex


def german_tokenizer(nlp):
    """
    return Tokenizer (spacy.tokenizer)

    Specialized tokenizer for the german language

    usage: nlp.tokenizer = german_tokenizer(nlp)
    """
    infixes = (
            LIST_ELLIPSES
            + LIST_ICONS
            + [
                r"(?<=[{al}])\.(?=[{au}])".format(al=ALPHA_LOWER, au=ALPHA_UPPER),
                r"(?<=[{a}])[,!?](?=[{a}])".format(a=ALPHA),
                r'(?<=[{a}])[:<>=](?=[{a}])'.format(a=ALPHA),
                r"(?<=[{a}]),(?=[{a}])".format(a=ALPHA),
                r"(?<=[{a}])([{q}\]\[])(?=[{a}])".format(a=ALPHA, q=_quotes),
                r"(?<=[{a}])--(?=[{a}])".format(a=ALPHA),
                r"(?<=[0-9])-(?=[0-9])",
                r"(?<=[0-9])\)(?=[0-9])",
                r"(?<=[+])(?=[0-9])",
                r"(?<=[a-zA-ZöäüÜÖÄß])\-|\/(?=[a-zA-ZöäüÜÖÄß]+)",
            ]
    )

    infix_re = compile_infix_regex(infixes)

    return Tokenizer(nlp.vocab,
                     prefix_search=nlp.tokenizer.prefix_search,
                     suffix_search=nlp.tokenizer.suffix_search,
                     infix_finditer=infix_re.finditer,
                     token_match=nlp.tokenizer.token_match,
                     rules=nlp.Defaults.tokenizer_exceptions)
