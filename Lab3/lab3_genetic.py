from itertools import combinations
import random
import time

max_runs = 30

def read_cnf_file(filename):
    """
    Used to read the CNF file and extract the necessary data.
    """
    clauses = []
    num_variables = 0
    num_clauses = 0

    try:
        with open(filename, 'r') as file:
            for line in file:
                line = line.strip()

                # Ignores comments, the % at the end and also the 0 at the end of the file.
                if line.startswith('c') or line.startswith('%') or line == '0':
                    continue

                # Reads the problem line to get the number of variables stated at the beginning of the CNF file.
                if line.startswith('p cnf'):
                    parts = line.split()
                    num_variables = int(parts[2])
                    num_clauses = int(parts[3])
                    continue

                # Process the clause lines by removing the 0 at the end of each line.
                clause = list(map(int, line.split()))
                if clause and clause[-1] == 0:
                    clause.pop()
                clauses.append(clause)
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    
    return clauses, num_variables, num_clauses

def initialize_population(pop_size, num_variables):
    return [[random.choice([True, False]) for _ in range(num_variables)] for _ in range(pop_size)]

def fitness(solution, clauses):
    score = 0
    for clause in clauses:
        if any((literal > 0 and solution[abs(literal) - 1]) or (literal < 0 and not solution[abs(literal) - 1]) for literal in clause):
            score += 1
    return score

def select_parents(population, fitnesses, num_parents):
    parents = random.choices(population, weights=fitnesses, k=num_parents)
    return parents

def crossover(parent1, parent2):
    point = random.randint(1, len(parent1) - 1)
    child1 = parent1[:point] + parent2[point:]
    child2 = parent2[:point] + parent1[point:]
    return child1, child2

def mutate(solution, mutation_rate):
    for i in range(len(solution)):
        if random.random() < mutation_rate:
            solution[i] = not solution[i]

def genetic_algorithm(clauses, num_variables, pop_size=100, num_generations=1000, mutation_rate=0.01):
    population = initialize_population(pop_size, num_variables)
    for generation in range(num_generations):
        fitnesses = [fitness(solution, clauses) for solution in population]
        if max(fitnesses) == len(clauses):
            break
        parents = select_parents(population, fitnesses, pop_size // 2)
        next_population = []
        for i in range(0, len(parents), 2):
            parent1, parent2 = parents[i], parents[i + 1]
            child1, child2 = crossover(parent1, parent2)
            mutate(child1, mutation_rate)
            mutate(child2, mutation_rate)
            next_population.extend([child1, child2])
        population = next_population
    best_solution = max(population, key=lambda sol: fitness(sol, clauses))
    return best_solution, fitness(best_solution, clauses)

def main(): 
    filename = input('Enter file name: \n')
    clauses, num_variables, num_clauses = read_cnf_file(filename)

    if num_variables is None or clauses is None:
        return
    
    for _ in range(max_runs):
        start_time = time.time()
        best_solution, best_fitness = genetic_algorithm(clauses, num_variables)
        # best_time = time.time() - start_time
        # boolean_result = convert_to_boolean(best_solution)
        print(f"Best solution: {best_solution}")
        print(f"Best fitness: {best_fitness}")
        # print(f"Taking {best_time} seconds.")

if __name__ == "__main__":
    main()