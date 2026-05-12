import numpy as np


class NeuralNetwork:
    def __init__(self, input_size, hidden_layers, output_size, learning_rate=0.1, seed=42):
        self.learning_rate = learning_rate

        # Reproducible random initialization
        self.rng = np.random.default_rng(seed)

        # Example:
        # input_size = 3
        # hidden_layers = [2, 4, 2]
        # output_size = 1
        #
        # layer_sizes = [3, 2, 4, 2, 1]
        self.layer_sizes = [input_size] + hidden_layers + [output_size]

        self.weights = []
        self.biases = []

        # Xavier/Glorot initialization
        for i in range(len(self.layer_sizes) - 1):
            fan_in = self.layer_sizes[i]
            fan_out = self.layer_sizes[i + 1]

            limit = np.sqrt(6 / (fan_in + fan_out))

            W = self.rng.uniform(-limit, limit, size=(fan_in, fan_out))
            b = np.zeros((1, fan_out))

            self.weights.append(W)
            self.biases.append(b)

    def sigmoid(self, x):
        # Clip avoids overflow for very large/small values
        x = np.clip(x, -500, 500)
        return 1 / (1 + np.exp(-x))

    def sigmoid_derivative(self, activated_value):
        return activated_value * (1 - activated_value)

    def forward(self, X):
        self.activations = [X]

        current_activation = X

        for i in range(len(self.weights)):
            z = np.dot(current_activation, self.weights[i]) + self.biases[i]
            current_activation = self.sigmoid(z)

            self.activations.append(current_activation)

        return current_activation

    def backward(self, X, y, output):
        samples = X.shape[0]

        deltas = [None] * len(self.weights)

        # For sigmoid + binary cross entropy:
        # output layer delta is simply output - y
        deltas[-1] = output - y

        # Backpropagate through hidden layers
        for i in reversed(range(len(self.weights) - 1)):
            error = np.dot(deltas[i + 1], self.weights[i + 1].T)
            deltas[i] = error * self.sigmoid_derivative(self.activations[i + 1])

        # Update weights and biases
        for i in range(len(self.weights)):
            dW = np.dot(self.activations[i].T, deltas[i]) / samples
            db = np.sum(deltas[i], axis=0, keepdims=True) / samples

            self.weights[i] -= self.learning_rate * dW
            self.biases[i] -= self.learning_rate * db

    def binary_cross_entropy(self, y, output):
        epsilon = 1e-12
        output = np.clip(output, epsilon, 1 - epsilon)

        return -np.mean(
            y * np.log(output) + (1 - y) * np.log(1 - output)
        )

    def train(self, X, y, epochs=50000, print_every=5000):
        for epoch in range(epochs + 1):
            output = self.forward(X)
            self.backward(X, y, output)

            if epoch % print_every == 0:
                loss = self.binary_cross_entropy(y, output)
                print(f"Epoch {epoch}, Loss: {loss:.6f}")

    def predict_proba(self, X):
        return self.forward(X)

    def predict(self, X):
        output = self.forward(X)
        return (output >= 0.5).astype(int)

    def get_genes(self):
        """
        Convert all weights and biases into one long vector.
        This is the DNA/chromosome of the neural network.
        """
        genes = []

        for W in self.weights:
            genes.extend(W.flatten())

        for b in self.biases:
            genes.extend(b.flatten())

        return np.array(genes)

    def set_genes(self, genes):
        """
        Load one long vector back into weights and biases.
        """
        index = 0

        for i in range(len(self.weights)):
            shape = self.weights[i].shape
            size = self.weights[i].size

            self.weights[i] = genes[index:index + size].reshape(shape)
            index += size

        for i in range(len(self.biases)):
            shape = self.biases[i].shape
            size = self.biases[i].size

            self.biases[i] = genes[index:index + size].reshape(shape)
            index += size

    def copy(self):
        new_network = NeuralNetwork(
            input_size=self.layer_sizes[0],
            hidden_layers=self.layer_sizes[1:-1],
            output_size=self.layer_sizes[-1]
        )

        new_network.set_genes(self.get_genes().copy())

        return new_network
