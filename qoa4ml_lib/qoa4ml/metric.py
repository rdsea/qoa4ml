# Metrics are implemented based on these classes to be compatible with Prometheus
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

    - Category: metrics are categorized into following groups
        0 - Quality: Performance (metrics for evaluating service performance e.g., response time, throughput)
        1 - Quality: Data (metrics for evaluating data quality e.g., missing, duplicate, erroneous)
        2 - Quality: Inference (metrics for evaluating quality of ML inference, measured from inferences e.g., accuracy, confidence)
        3 - Resource: metrics for evaluating resource utilization e.g. CPU, Memory
        Other: To do (extend more categories)
    """
    def __init__(self, metric_name, description, default_value=-1, category=0):
        self.name = metric_name
        self.description = description
        self.default_value = default_value
        self.value = default_value
        self.category = category
    
    def set(self, value):
        self.value = value
    def get_val(self):
        return self.value
    def get_name(self):
        return self.name
    def get_des(self):
        return self.description
    def get_category(self):
        return self.category

    def reset(self):
        self.value = self.default_value
    def __str__(self) -> str:
        return "metric_name: " + self.name + ", " + "value: " + str(self.value)
    def to_dict(self):
        mectric_dict = {}
        mectric_dict[self.name] = self.value
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
    def __init__(self, metric_name, description, default_value=0, category=0):
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
    def __init__(self, metric_name, description, default_value=-1, category=0):
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
    def __init__(self, metric_name, description, default_value=-1, category=0):
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
    def __init__(self, metric_name, description, default_value=-1, category=0):
        super().__init__(metric_name, description, default_value, category)

    def inc(self,num):
        self.value += num
    # TO DO:
    # implement other functions
    def dec(self,num):
        self.value -= num
    def set(self,val):
        self.value = val

