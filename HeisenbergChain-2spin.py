import numpy as np
import sys
# import matplotlib.pyplot as plt
# from matplotlib import rc
# rc('font',**{'family':'sans-serif','sans-serif':['Helvetica']})
# rc('text', usetex=True)
# fig = plt.figure()
# plt1 = fig.add_subplot(111)
#plt2 = fig.add_subplot(212)
#sys.path.append('/Users/mmetcalf/Dropbox/Quantum Embedding/Codes/QITE/code_v4/')

<<<<<<< HEAD
from hamiltonian      import Heisenberg_LR,Heisenberg_SR,print_Hamiltonian, Hmat, TransverseIsing, Ising, single_qubit_field
from mf               import hom_mf_solution,hom_mf_state,hom_mf_energy,mf_solution,mf_state,mf_energy
from ite              import ITE_FCI
from qite             import QITE
from binary_functions import Bas2Int
from math import ceil, floor, pi
from scipy.linalg import eigh
nspin =  3

R     =  0.5
db    =  0.5
bmax  =  2.00

#H = Heisenberg_LR(nspin,R)
J = 1/np.sqrt(2)
#H = TransverseIsing(nspin, R, J, J)
#H = Ising(nspin, R, pi/2)
H = single_qubit_field(pi/4)
#print('Hamiltonian\n',H)
print_Hamiltonian(H)

Hm = Hmat(H)
evl, evc = eigh(Hm)
print(evl)
# print()
# print(np.real(Hm))


# AFM initial guess

psi_0       = np.zeros(2**nspin,dtype=complex)
#psi_0       = np.array([ 0, 0,0,1],dtype=complex)
#print(psi_0)
xvec        = [0,1]*ceil((nspin/2))
xind        = Bas2Int(xvec,2)
#psi_0[xind] = 1.0
psi_0[0] = 1.0

#print(psi_0)


#ite_data = ITE_FCI(H,db,bmax,psi0=psi_0)
#print(ite_data)
#ite_data, Xop = QITE(H,db,bmax,lanczos=False,psi0=psi_0,ncheck=10)

#print(Xop)
# plt1.scatter(ite_data[:,0],ite_data[:,1], color='xkcd:purple', label='ITE' )
# plt1.set_ylabel('E', fontsize=14)
# plt1.set_xlabel(r'$\beta$',fontsize=16)
# plt1.scatter(qite_data[:,0],qite_data[:,1], color='xkcd:green', label='QITE' )
# plt.legend(loc='upper right', fontsize=16)
# plt.show()