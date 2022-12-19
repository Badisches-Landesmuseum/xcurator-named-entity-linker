# Named Entity Service

**Authors: Sören Räuchle, Nadav Babai, Jan Fillies | [3pc GmbH](https://www.3pc.de)**

This service is analyzing text for extracting Named Entities, Linked Entities, Abbreviations and Sentiment Scores for
the German language.

### Named Entities

The Named Entities are a hybrid of AI and Gazetter Dictionary matching. The AI is looking for the Grammar and is using a
Spacy Model. The Gazetter Matching is based on Entities extracted from the 3pc.de Website.

### Abbreviation Detection

The Abbreviation Detection is based an Algorithm described in a Paper of A.S. Schwartz and M.A. Hearst. Additionally, the Detection is extracting Abbreviations from HTML Content.

### Sentiment Analysis

Sentiment Analysis is done with a Sentiment Dictionary for the german language in combination with a lemmatizer.


### Install, Run, Test

- Install dependencies: ```conda env create -f environment.yml```
- Install Testing dependencies: ```conda env update -f environment.yml```
- Run: ```python __main__.py``` (inside the **source code** directory)
- Run Tests: ```pytest``` (inside the **tests** directory)
- Generate protos with: ```bash python  generate-proto.py ```


### Technology Stack
- [Python 3.8](https://www.python.org/)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Conda](https://www.anaconda.com/)
- [Spacy](https://spacy.io/)
- More dependencies ```envionment.yml```
- More runtime dependencies ```docker-compose.yml```



To activate profile, add to env variables:

```dotenv
PROFILE=local
```

### More Info | Documentation | Papers
- [A Simple Algorithm for Identifying Abbreviation Definitions in Biomedical Text](https://psb.stanford.edu/psb-online/proceedings/psb03/schwartz.pdf)
