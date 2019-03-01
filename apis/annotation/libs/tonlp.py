"""Organize the data to be passed on to the NLP module"""

class NLPData:
    """The class for data organization"""
    def __init__(self, data=None, auxiliary=None):
        self.data = data
        self.nlp_data = {
            "labels": self.get_labels()
        }

    def get_labels(self):
        """The function for getting all the visible labels"""
        labels = []
        if self.data is not None:
            for entity in self.data:
                if entity.get("label") is not None:
                    labels.extend(entity["label"])
        return labels

    def get_result(self):
        """Return the organized data for the NLP module"""
        return self.nlp_data
