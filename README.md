# QoA4ML - Quality of Analytics for ML
>Note: **We are currently revising the prototype and the code will be released soon**

## Language

The design of QoA4ML specification is in [language](language/)

## Probes
* [QoA4ML Probes](probes/): libraries and lightweight modules capturing metrics. They are integrated into suitable ML serving frameworks and ML code
* Probe properties:
  - Can be written in different languages (Python, GoLang)
  - Can have different communications to monitoring systems (depending on probes and its ML support)
  - Capture metrics with a clear definition/scope
    - e.g., Response time for an ML stage (training) or a service call (of ML APIs)
    - Thus output of probes must be correlated to objects to be monitored and the tenant
  - Support high or low-level metrics/attributes
    - depending on probes implementation
  - Can be instrumented into source code or standlone

## QoA4ML Handler

## QoA4ML Reports

## Examples

Examples are in [examples](examples/).


## QoA4ML Observability

The code is in [observability](observability./)

![The overal architecture of the Observability Service](img/qoa4mlos-overview.png)
QoA4ML Monitor is a component monitoring QoA for a ML model which is deployed in a serving platform.


* Monitoring Service: third party monitoring service used for managing monitoring data.
  - We use Prometheus and other services: provide information on how to configure them.
* QoA4MLObservabilityService: a service reads QoA4ML specifications and real time monitoring data and detect if any violation occurs


## References
* Hong-Linh Truong, Minh-Tri Nguyen, ["QoA4ML -A Framework for Supporting Contracts in Machine Learning Services"](https://research.aalto.fi/files/65786264/main.pdf), [The 2021 IEEE International Conference on Web Services (ICWS 2021)](https://conferences.computer.org/icws/2021/), to appear.
*  Minh-Tri Nguyen, Hong-Linh Truong [Demonstration Paper: Monitoring Machine Learning Contracts with QoA4ML](https://research.aalto.fi/files/56621517/main.pdf), Companion of the 2021 ACM/SPEC International Conference on Performance Engineering (ICPE'21), Apr. 19-23, 2021
*   https://www.researchgate.net/publication/341762862_R3E_-An_Approach_to_Robustness_Reliability_Resilience_and_Elasticity_Engineering_for_End-to-End_Machine_Learning_Systems
