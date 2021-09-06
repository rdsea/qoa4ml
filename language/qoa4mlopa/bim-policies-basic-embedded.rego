# one example of qoa4ml policies for a contract for bts scenario
package qoa4ml.bim.basic.embedded

# the contract data is embedded into this policies

default mlfair_violation = true
default mlaccuracy_violation=false
#load the contract data
qoa4ml_contract :={
    "stakeholders":
    {
        "id": "solibri",
        "roles": ["mlprovider"]
    },

    "resources":{
        "services": [
            {"id": "bimclassification", "serviceapi": ["rest"],"machinetypes":["small"], "processortypes": ["GPU"]}
        ],
        "data": [
            {"id": "bimdata", "datatypes": ["files"], "formats": ["smc"]}
        ],
        "mlmodels": [
            {"id": "model1", "formats": ["kerash5"], "mlinfrastructures": ["tensorflow"]}
        ]
    },
    "quality": {
        "services":{
            "ResponseTime":{"operators":["min"],"value":"300"}
        },
        "data":{
            "Accuracy": {"operators":["min"],"value":"0.99"}
        },
        "mlmodels": {
            "Accuracy":{"operators":["min"],"value":"0.99"}
        }
    },
    "interpretability": {
        "explanability":{"modes": ["full"]}
    }
}
# The policy checker will receive two inputs: the contract and the runtime information
# input variable: the input of runtime metrics

mlaccuracy_violation = {
	  qoa4ml_contract.quality.mlmodels.Accuracy.value > input.quality.mlmodels.Accuracy.value
}
mlfair_violation = {
	  qoa4ml_contract.interpretability.explainability.modes[_]!=input.interpretability.explainability.modes[0]
}
