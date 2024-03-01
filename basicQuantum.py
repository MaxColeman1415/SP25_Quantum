# Required dependencies for the interpreter
# Reference https://docs.quantum.ibm.com/start/install#local
#   import matplotlib
#   import pylatexenc
#   import qiskit-ibm-runtime
#   import qiskit[visualization]


# Import libraries
from qiskit import QuantumCircuit
from qiskit.quantum_info import Pauli
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_ibm_runtime import QiskitRuntimeService, Estimator, Options
import matplotlib.pyplot as plt
import numpy as np

################
# Import account
################
API_TOKEN = "your IMBQ token goes here"
QiskitRuntimeService.save_account(channel="ibm_quantum", token=API_TOKEN, overwrite=True)
service = QiskitRuntimeService(channel="ibm_quantum")

# Run on the least-busy backend you have access to
# backend = service.least_busy(simulator=False, operational=True) <- ACTUAL QUANTUM, MAY TAKE A WHILE
backend = service.get_backend('simulator_statevector')

############################################
# Map the problem to a quantum native format
############################################
# Build a basic circuit with two qubits and a hadamard gate on 0, and a 0 controlled cx gate on 1
qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)

# The following code cell uses the quantum_info package to create the two-qubit Pauli operator Z
# on qubit 1 and Z on qubit 2.
# If the state is entangled, then the correlation between qubit 1 and qubit 2 is one.
ZZ = Pauli('ZZ')
ZI = Pauli('ZI')
IZ = Pauli('IZ')
XX = Pauli('XX')
XI = Pauli('XI')
IX = Pauli('IX')

# build a pass manager to manage the transformations to the quantum circuit
pm = generate_preset_pass_manager(optimization_level=1)
isa_circuit = pm.run(qc)

##############
# Execute code
##############
options = Options()
options.resilience_level = 1
options.optimization_level = 3

# Create an Estimator object
estimator = Estimator(backend, options=options)

# Submit the circuit to Estimator
job = estimator.run([isa_circuit] * 6, observables=[IZ, IX, ZI, XI, ZZ, XX], shots=5000)

# Once the job is complete, get the result
data = ['IZ', 'IX', 'ZI', 'XI', 'ZZ', 'XX']
values = job.result().values

# creating error bars
error = []
for case in job.result().metadata:
    error.append(2 * np.sqrt(case['variance'] / case['shots']))

# plotting graph
plt.plot(data, values)
plt.errorbar(data, values, yerr=error, fmt='o')
plt.xlabel('Observables')
plt.ylabel('Values')
plt.savefig('q_plot.png')
