# Metrics are implemented based on these classes to be compatible with Prometheus
import numpy as np

class Metric(object):
    """
    This class defines the common attribute and provide basic function for handling a metric
    - Attribute: 
        - name: name of the metric
        - description: describe the metric
        - value: value of the metric
        - category: group metric into specific category supporting building QoA_Report
        - others: (Developing)

    - Function: 
        - set: set specific value
        - get_val: return current value
        - get_name: return metric name
        - get_des: return metric description
        - other: (Developing)
    """
    def __init__(self, metric_name, description, default_value=-1, category=None):
        self.metric_name = metric_name
        self.description = description
        self.default_value = default_value
        self.value = default_value
        self.category = category
    
    def set(self, value):
        self.value = value
    def get_val(self):
        return self.value
    def get_name(self):
        return self.metric_name
    def get_des(self):
        return self.description
    def get_category(self):
        return self.category

    def reset(self):
        self.value = self.default_value
    def __str__(self) -> str:
        return "metric_name: " + self.metric_name + ", " + "value: " + str(self.value)
    def to_dict(self):
        mectric_dict = {}
        mectric_dict[self.metric_name] = self.value
        return mectric_dict

class Counter(Metric):
    """
    This class inherit all attributes of Metric
    - Attribute: (Developing)

    - Function: 
        - inc: increase its value by num
        - reset: set the value back to zero
        - others: (Developing)
    """
    def __init__(self, metric_name, description, default_value=0, category=None):
        super().__init__(metric_name, description, default_value, category)

    def inc(self,num=1):
        self.value += num

class Gauge(Metric):
    """
    This class inherit all attributes of Metric
    - Attribute: (Developing)

    - Function: 
        - inc: increase its value by num
        - others: (Developing)
    """
    def __init__(self, metric_name, description, default_value=-1, category=None):
        super().__init__(metric_name, description, default_value, category)

    def inc(self,num=1):
        self.value += num
    # TO DO:
    # implement other functions
    def dec(self,num=1):
        self.value -= num
    def set(self,val):
        self.value = val

class Summary(Metric):
    """
    This class inherit all attributes of Metric
    - Attribute: (Developing)

    - Function: 
        - inc: increase its value by num
        - others: (Developing)
    """
    def __init__(self, metric_name, description, default_value=-1, category=None):
        super().__init__(metric_name, description, default_value, category)

    def inc(self,num):
        self.value += num
    # TO DO:
    # implement other functions
    def dec(self,num):
        self.value -= num
    def set(self,val):
        self.value = val

class Histogram(Metric):
    """
    This class inherit all attributes of Metric
    - Attribute: (Developing)

    - Function: 
        - inc: increase its value by num
        - others: (Developing)
    """
    def __init__(self, metric_name, description, default_value=-1, category=None):
        super().__init__(metric_name, description, default_value, category)

    def inc(self,num):
        self.value += num
    # TO DO:
    # implement other functions
    def dec(self,num):
        self.value -= num
    def set(self,val):
        self.value = val



def data_validate_max(data, normalize):
    """Return percentage data lower than threshold before normalization (%)
    data is a numpy array
    normalize example:
    {
        "max": <@value>,
        "mean": <@value>,
        "threshold": <@value>
    }
    """
    mean_val = normalize["mean"]
    max_val = normalize["max"]
    threshold = normalize["threshold"]
    data_accuracy = 100*np.sum(data<((threshold-mean_val)/max_val))/data.size
    return data_accuracy