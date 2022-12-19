import os


class MatcherDirectory:
    persons = []
    PERSON_FILE = os.path.join(os.path.dirname(__file__), 'person.txt')

    locations = []
    LOCATION_FILE = os.path.join(os.path.dirname(__file__), 'location.txt')

    organisations = []
    ORGANISATION_FILE = os.path.join(os.path.dirname(__file__), 'organisation.txt')

    mists = []
    MISC_FILE = os.path.join(os.path.dirname(__file__), 'misc.txt')

    all = []

    def __init__(self):
        self.persons = []
        person_file = open(self.PERSON_FILE, 'r', encoding="utf8")
        for line in person_file:
            self.add_person(line.strip())

        self.locations = []
        location_file = open(self.LOCATION_FILE, 'r', encoding="utf8")
        for line in location_file:
            self.add_location(line.strip())

        self.orgaSnisations = []
        organisation_file = open(self.ORGANISATION_FILE, 'r', encoding="utf8")
        for line in organisation_file:
            self.add_organisation(line.strip())

        self.mists = []
        misc_file = open(self.MISC_FILE, 'r', encoding="utf8")
        for line in misc_file:
            self.add_misc(line.strip())

        self.all.extend(self.persons)
        self.all.extend(self.organisations)
        self.all.extend(self.locations)
        self.all.extend(self.mists)

    def add_person(self, name: str):
        for temp_name in name.split():
            if temp_name[0].isupper():
                self.persons.append({"label": "PER", "pattern": temp_name})
        self.persons.append({"label": "PER", "pattern": name})

    def add_location(self, name: str):
        self.locations.append({"label": "LOC", "pattern": name})

    def add_organisation(self, name: str):
        self.organisations.append({"label": "ORG", "pattern": name})

    def add_misc(self, name: str):
        self.mists.append({"label": "MISC", "pattern": name})
