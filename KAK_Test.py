import numpy as np
import scipy.linalg as la

from qiskit.quantum_info.synthesis import TwoQubitBasisDecomposer
from qiskit.aqua.operators import WeightedPauliOperator, evolution_circuit
from qiskit.quantum_info.operators import Pauli
from qiskit import Aer, execute
from qiskit.compiler import transpile

backend = Aer.get_backend('unitary_simulator')

I = np.array([[1,0],[0,1]])
X = np.array([[0,1],[1,0]])
Y = np.array([[0,-1j],[1j,0]])
Z = np.array([[1,0],[0,-1]])

h_img = 0.15*np.kron(I,Y)+0.15*np.kron(Y,I)-0.08*np.kron(X,Y)-0.08*np.kron(Y,X)+0.12*np.kron(Y,Z)+0.12*np.kron(Z,Y)
print(h_img, '\n')
h_list = [[-0.15,Pauli(label='YI')],[-0.15,Pauli(label='IY')],[0.08,Pauli(label='YX')],[0.08,Pauli(label='XY')],
          [-0.12,Pauli(label='YZ')],[-0.12,Pauli(label='ZY')]]
U_img = la.expm(1j*h_img)
print(U_img)
# cirq = TwoQubitBasisDecomposer(U_img)
# print(cirq)
h_p = WeightedPauliOperator(paulis=h_list)
# h_test = 0
# for key, val in enumerate(h_p.paulis):
#     h_test+= val[0]*val[1].to_matrix()
# print(h_test)
evo_cirq = evolution_circuit(h_list, evo_time=1, num_time_slices=1,
                          controlled=False, power=1,
                          use_basis_gates=False, shallow_slicing=False,
                          barrier=True, reg_name = 'a')
print(evo_cirq)
compile_cirq = transpile(evo_cirq, optimization_level=3)
job = execute(evo_cirq, backend)
result = job.result()
unitary = result.get_unitary(evo_cirq)
print(unitary)
# print(compile_cirq)
# print(compile_cirq.depth())


# print(evo_cirq)