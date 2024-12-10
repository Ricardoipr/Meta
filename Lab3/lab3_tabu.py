from collections import deque
import csv
from itertools import combinations
import random
import time

max_runs = 30
max_evaluations = 10000000
tabu_tenure = 15

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
        return None, None, None

    return num_variables, num_clauses, clauses

def num_clauses_satisfied(clause, possibility):
    """
    Checks how many clauses are satisfied.
    """
    for literal in clause:
        var = abs(literal) - 1
        if (literal > 0 and possibility[var] == 1):
            return True
        if (literal < 0 and possibility[var] == 0):
            return True
    return False

def clause_counter(possibility, clauses):
    """
    Counts how many clauses are satisfied by the current variable assignment.
    """
    clauses_satisfied = 0

    for clause in clauses:
        if num_clauses_satisfied(clause, possibility):
            clauses_satisfied +=1

    return clauses_satisfied    

def tabu(num_variables, clauses):
    """
    Implements the Tabu algorithm.
    Starts with a random assignment of variables, evaluates neighbors, and 
    continues improving until no better neighbor is found or the maximum number of evaluations is reached.
    """
    current_possibility = [random.choice([0,1]) for _ in range(num_variables)]
    tabu_list = deque(maxlen=tabu_tenure)
    function_evaluations = 0
    satisfied_clauses = clause_counter(current_possibility, clauses)
    best_possibility = current_possibility[:]
    best_satisfied_clauses = satisfied_clauses

    while function_evaluations < max_evaluations:
        improved = False
        best_neighbor = None
        best_neighbor_satisfied_clauses = -1

        # Generate neighbors by flipping each bit
        for i in range(num_variables):
            neighbor = current_possibility[:]
            neighbor[i] = 1 - neighbor[i]  # Flip the bit

            if neighbor in tabu_list:
                continue

            neighbor_satisfied_clauses = clause_counter(neighbor, clauses)
            function_evaluations += 1

            if neighbor_satisfied_clauses > best_neighbor_satisfied_clauses:
                best_neighbor = neighbor
                best_neighbor_satisfied_clauses = neighbor_satisfied_clauses

            if function_evaluations >= max_evaluations:
                break

        if best_neighbor_satisfied_clauses > satisfied_clauses:
            current_possibility = best_neighbor
            satisfied_clauses = best_neighbor_satisfied_clauses
            tabu_list.append(current_possibility)
            improved = True

        if satisfied_clauses > best_satisfied_clauses:
            best_possibility = current_possibility[:]
            best_satisfied_clauses = satisfied_clauses

        if not improved:
            break

    return best_possibility, best_satisfied_clauses, function_evaluations

def neighbourhood_checker(num_variables, clauses, output_csv='results.csv'):
    """
    Runs the tabu algorithm multiple times and tracks the best result across the runs.
    Saves the results of each run to a CSV file.
    """
    best_clauses = 0
    best_function_evaluations = 0
    best_solution = []

    # Prepare the CSV file
    with open(output_csv, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Run', 'Satisfied Clauses', 'Function Evaluations', 'Solution'])

        for run in range(max_runs):
            current_solution, satisfied_clauses, function_evaluations = tabu(num_variables, clauses)
            
            # Save the result of the current run to the CSV file
            writer.writerow([run + 1, satisfied_clauses, function_evaluations, current_solution])
            
            if satisfied_clauses > best_clauses:
                best_clauses = satisfied_clauses
                best_function_evaluations = function_evaluations
                best_solution = current_solution

    return best_solution, best_clauses, best_function_evaluations

def convert_to_boolean(assignment):
    """
    Will convert the result's 0s to False and 1s to True.
    """
    return [bool(val) for val in assignment]

def main():
    filename = input('Enter file name: \n')
    num_variables, num_clauses, clauses = read_cnf_file(filename)

    if num_variables is None or clauses is None:
        return
    
    for _ in range(max_runs):
        start_time = time.time()
        best_solution = neighbourhood_checker(num_variables, clauses)
        best_time = time.time() - start_time
        boolean_result = convert_to_boolean(best_solution)

if __name__ == "__main__":
    main()
    main()