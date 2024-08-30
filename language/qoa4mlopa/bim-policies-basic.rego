# one example of qoa4ml policies for a contract for bts scenario
package qoa4ml.bim.basic

# the contract data is from this location
#/v1/data/qoa4ml/bim/basic/contract (through PUT document)
import data.qoa4ml.bim.basic.contract

default mlfair_violation = true
default mlaccuracy_violation=false

#load the contract data
qoa4ml_contract :=contract

# The policy checker will receive two inputs: the contract and the runtime information
# input variable: the input of runtime metrics

mlaccuracy_violation = {
	qoa4ml_contract.quality.mlmodels.Accuracy.value > input.quality.mlmodels.Accuracy.value
}
mlfair_violation = {
	qoa4ml_contract.interpretability.explanability.modes[_]==input.interpretability.explanability.modes[0]
}
