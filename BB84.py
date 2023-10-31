from qiskit import QuantumCircuit, transpile, execute
from numpy.random import randint
from numpy import array2string
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error


# Quantum Circuit that performs key generation in BB84
def bb84_circuit(state, basis, measurement_basis, num_qubits):
    circuit = QuantumCircuit(num_qubits)

    # Loop in which Alice puts her bit
    for i in range(len(basis)):
        #If the randomly generated a value is 1 use the Pauli X gate
        if state[i] == 1:
            circuit.x(i)

        #If the randomly generated b value is 1 use the Hadamard gate
        if basis[i] == 1:
            circuit.h(i)
   
    #Loop in which Bob measures qubits
    for i in range(len(measurement_basis)):

        #If the randomly generated b' is 1 then we use the Hadamard gate
        if measurement_basis[i] == 1:
            circuit.h(i)

    #Quantum gates are reversible so they can save previous state therefore we measure all at once
    circuit.measure_all()
    
    return circuit


#Main Loop for creating simulator, circuit, and random values
def main():
    #Ask if we want to introduce noise
    noise_option = input("Would you like to add noise? (y/n): ")

    #Initialize our simulator either with noise or without
    if noise_option == 'y':
        noise = NoiseModel()
        error = depolarizing_error(.9, 1)
        noise.add_all_qubit_quantum_error(error, ['x', 'h'])
        simulator = AerSimulator(noise_model=noise)
    else:
        simulator = AerSimulator()

    # For each qubit generate a, b, and b'
    num_qubits = 27
    alice_a = randint(2, size=num_qubits)
    alice_b = randint(2, size=num_qubits)
    bob_b_prime = randint(2, size=num_qubits)

    #Create circuit and feed our bits into the circuit
    circuit = bb84_circuit(alice_a, alice_b, bob_b_prime, num_qubits)

    #Execute the circuit using Qasm simulator then reverse the bits given that we performed a measure all function at the end of circuit circuit
    #If we want noise the simulator we must transpile our BB84 circuit and simulator
    if noise_option == 'y':
        noisy_circuit = transpile(circuit, simulator)
        key = next(iter(simulator.run(noisy_circuit.reverse_bits()).result().get_counts().items()))[0]
    else:
        key = execute(circuit.reverse_bits(), backend=simulator, shots=1).result().get_counts().most_frequent()

    #Bob and Alice publicly discuss the choice of basis and discard those basis that were not correct
    key_alice = []
    key_bob = []
    for i in range(num_qubits):
        #If basis match retain the bit
        if alice_b[i] == bob_b_prime[i]:
            key_alice.append(alice_a[i])
            key_bob.append(int(key[i]))

    #Print all our values
    print(f"Alice's random states:\t {array2string(alice_a)}") #random a
    print(f"Alice's random bases:\t {array2string(alice_b)}") # random b
    print(f"Bob's random bases:\t {array2string(bob_b_prime)}") # random b'
    print(f"Alice's Key:\t\t {key_alice}") # alice's key
    print(f"Bob's Key:\t\t {key_bob}") # bob's key


if __name__ == "__main__":
    main()