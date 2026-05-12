import numpy as np

from NeuralNetwork import NeuralNetwork


class GeneticAlgorithmTrainer:
    def __init__(
        self,
        input_size,
        hidden_layers,
        output_size,
        population_size=50,
        mutation_rate=0.08,
        mutation_strength=0.4,
        elite_size=8,
        seed=42
    ):
        self.input_size = input_size
        self.hidden_layers = hidden_layers
        self.output_size = output_size

        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.mutation_strength = mutation_strength
        self.elite_size = elite_size

        self.rng = np.random.default_rng(seed)
        self._next_id = 0  # contador global de ids

        self.population = []
        for _ in range(population_size):
            net = NeuralNetwork(input_size, hidden_layers, output_size, seed=int(self.rng.integers(1_000_000)))
            net.individual_id = self._next_id
            self._next_id += 1
            self.population.append(net)

    def evolve(self, fitness_scores):
        """
        Recebe os fitness coletados do jogo (um por individuo, mesma ordem
        de self.population) e produz a proxima geracao.
        Elites mantem seu id original; filhos recebem um id novo.
        """
        scored = sorted(
            zip(fitness_scores, self.population),
            key=lambda item: item[0],
            reverse=True
        )

        new_population = []

        # Elitismo: mantem os melhores com o mesmo id
        for _, elite in scored[:self.elite_size]:
            clone = elite.copy()
            clone.individual_id = elite.individual_id  # preserva o id
            new_population.append(clone)

        # Filhos recebem ids novos
        while len(new_population) < self.population_size:
            parent1 = self._select_parent(scored)
            parent2 = self._select_parent(scored)

            child = self._crossover(parent1, parent2)
            self._mutate(child)
            child.individual_id = self._next_id
            self._next_id += 1

            new_population.append(child)

        self.population = new_population

    # ------------------------------------------------------------------
    # Operadores genéticos
    # ------------------------------------------------------------------

    def _crossover(self, parent1, parent2):
        genes1 = parent1.get_genes()
        genes2 = parent2.get_genes()

        mask = self.rng.random(size=genes1.shape) < 0.5
        child_genes = np.where(mask, genes1, genes2)

        child = NeuralNetwork(self.input_size, self.hidden_layers, self.output_size)
        child.set_genes(child_genes)
        return child

    def _mutate(self, network):
        genes = network.get_genes()

        mutation_mask = self.rng.random(size=genes.shape) < self.mutation_rate
        mutations = self.rng.normal(0.0, self.mutation_strength, size=genes.shape)
        genes[mutation_mask] += mutations[mutation_mask]

        network.set_genes(genes)

    def _select_parent(self, scored_population):
        """Seleção por torneio."""
        tournament_size = min(5, len(scored_population))

        candidates = self.rng.choice(len(scored_population), size=tournament_size, replace=False)

        best_idx = candidates[0]
        best_score = scored_population[best_idx][0]

        for idx in candidates[1:]:
            if scored_population[idx][0] > best_score:
                best_score = scored_population[idx][0]
                best_idx = idx

        return scored_population[best_idx][1]