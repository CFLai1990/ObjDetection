"""Organize the data to be passed on to the NLP module"""

class NLPData:
    """The class for data organization"""
    def __init__(self, data=None, auxiliary=None):
        self.data = data
        self.auxiliary = auxiliary
        self.nlp_data = {
            "labels": self.get_labels(),
            "axes": self.get_axes(),
            "legends": self.get_legends()
        }

    def get_labels(self):
        """The function for getting all the visible labels"""
        labels = []
        if self.data:
            for entity in self.data:
                if entity.get("label") is not None:
                    entity_labels = entity["label"]
                    for label in entity_labels:
                        if label not in labels:
                            labels.append(label)
        return labels

    def get_axes(self):
        """The function for getting all the axes"""
        axes = []
        if self.auxiliary is not None:
            for entity in self.auxiliary:
                if entity.get("class") == "axis":
                    # Get the label of the axis, including the title and the unit
                    axis_label = entity.get("label")
                    # Get the tick values of the axis
                    axis_ticks = []
                    axis_data = entity.get("axis_data")
                    if axis_data is not None:
                        ticks = axis_data.get("ticks")
                        if ticks is not None:
                            for tick in ticks:
                                axis_ticks.append(tick["text"])
                    # Pack the axis data
                    axis = {
                        "label": axis_label,
                        "ticks": axis_ticks
                    }
                    axes.append(axis)
        return axes

    def get_legends(self):
        """The function for getting all the legends"""
        legends = []
        if self.auxiliary is not None:
            for entity in self.auxiliary:
                if entity.get("class") == "legend":
                    # Get the label of the legend, including the title and the unit
                    legend_label = entity.get("label")
                    # Get the feature of the legend
                    legend_feature = {}
                    legend_data = entity.get("legend_data")
                    if legend_data is not None:
                        legend_feature["color"] = legend_data.get("color")
                    # Pack the legend data
                    legend = {
                        "label": legend_label,
                        "feature": legend_feature
                    }
                    legends.append(legend)
        return legends

    def get_result(self):
        """Return the organized data for the NLP module"""
        return self.nlp_data
