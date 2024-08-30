# one example of qoa4ml policies for a contract for bts scenario
package qoa4ml.bts.alarm

#import bts.contract

default contract_violation = false

#qoa4ml_contract =bts

# Count number of violations to define a contract problem

contract_violation = true {
    count(violation) == 0
}
# The policy checker will receive two inputs: the contract and the runtime information
# input variable: the input of runtime metrics
violation[service.id] {
	some service
    get_service[service]
    service.processingtype[_]=="GPU"
    service.serviceapi[_]=="rest"
}
get_service[service] {
    service := input.resources.services[_]
    service.processingtype[_] == "GPU"
}
