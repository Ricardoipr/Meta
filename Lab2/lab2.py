from itertools import combinations
import random
import re
import time
import csv
import os

max_runs = 30
max_evaluations = 10000000

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

                if line.startswith('c') or line.startswith('%') or line == '0':
                    continue

                if line.startswith('p cnf'):
                    parts = line.split()
                    num_variables = int(parts[2])
                    num_clauses = int(parts[3])
                    continue

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

def hillclimb(num_variables, clauses, variable_neighbourhood):
    """
    Implements the Hillclimbing algorithm.
    Starts with a random assignment of variables, evaluates neighbors, and 
    continues improving until no better neighbor is found.
    """
    current_possibility = [random.choice([0,1]) for _ in range(num_variables)]
    function_evaluations = 0
    satisfied_clauses = clause_counter(current_possibility, clauses)
    max_hamming_distance = 3 if variable_neighbourhood else 1
    hamming_distance = 1

    while True:
        improved = False

        for hamming_distance in range(1, max_hamming_distance + 1):
            order = list(range(num_variables))
            random.shuffle(order)
            all_combinations = list(combinations(order, hamming_distance))
            random.shuffle(all_combinations)

            for indexes in random.sample(list(combinations(order, hamming_distance)), len(order)):
                neighbour_possibility = current_possibility.copy()

                for index in indexes:
                    neighbour_possibility[index] = 1 - current_possibility[index]
                
                neighbour_clauses = clause_counter(neighbour_possibility, clauses)
                function_evaluations +=1

                if neighbour_clauses > satisfied_clauses:
                    current_possibility = neighbour_possibility
                    satisfied_clauses = neighbour_clauses
                    improved = True
                    break

            if improved:
                break

        if not improved:
            break

    return current_possibility, satisfied_clauses, function_evaluations

def convert_to_boolean(assignment):
    """
    Will convert the result's 0s to False and 1s to True.
    """
    return [bool(val) for val in assignment]

def neighbourhood_checker(num_variables, clauses, variable_neighbourhood, multistart):
    """
    Runs the hillclimb algorithm multiple times and tracks the best result across the runs.
    """
    best_clauses = 0
    best_function_evaluations = 0
    best_solution = []
    max_runs = 1 if multistart else 30

    for _ in range(max_runs):
        current_solution, satisfied_clauses, function_evaluations= hillclimb(num_variables, clauses, variable_neighbourhood)
        
        if satisfied_clauses > best_clauses:
            best_clauses = satisfied_clauses
            best_function_evaluations = function_evaluations
            best_solution = current_solution

    return best_solution, best_clauses, best_function_evaluations

def multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart, csv_filename):
    """
    Runs the multistart hillclimb algorithm multiple times (30 times, max_runs) and tracks the best result across the runs.
    """
    subdirectory = "revised"
    filepath = os.path.join(subdirectory, csv_filename)

    for run_num in range(max_runs):
        function_counter = 0
        current_best_solution = []
        current_best_satisfied_clauses = 0
        run_start_time = time.time()

        while function_counter <= max_evaluations:
            current_solution, current_satisfied_clauses, current_function_evaluations = neighbourhood_checker(
                num_variables, clauses, variable_neighbourhood, multistart)

            if current_satisfied_clauses > current_best_satisfied_clauses:
                current_best_satisfied_clauses = current_satisfied_clauses
                current_best_solution = current_solution

            function_counter += current_function_evaluations

            if current_satisfied_clauses == num_clauses or function_counter >= max_evaluations:
                break

        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            boolean_result = convert_to_boolean(current_best_solution)
            writer.writerow(' ')
            writer.writerow([f'Solution number {run_num + 1}'])
            writer.writerow([str(boolean_result)])
            writer.writerow(['Clauses Satisfied', 'Function Evaluations', 'Time (seconds)'])
            writer.writerow([current_best_satisfied_clauses, function_counter, time.time() - run_start_time])
            print(f"Run {run_num + 1} completed.")

def main():
    print("Chose one of the algorithms below to execute:")
    option = input("A - Next Ascent Hillclimbing\nB - Multistart Next Ascent Hillclimbing\nC - Variable Neighbourhood Ascent\nD - Multistart Variable Neighbourhood Ascent\n")

    if re.match("^[ABCD]$", option):
        filename = input('Enter file name: \n')
        num_variables, num_clauses, clauses = read_cnf_file(filename)
        if num_variables is None or clauses is None:
            return
        
        if option == 'A':
            variable_neighbourhood = False
            multistart = False
            csv_filename = 'results_A_Next_Ascent_Hillclimbing.csv'
            neighbourhood_checker(num_variables, clauses, variable_neighbourhood, multistart)
            
        elif option == 'B':
            print("Running...")
            variable_neighbourhood = False
            multistart = True
            csv_filename = 'results_B_Multistart_Next_Ascent_Hillclimbing.csv'
            multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart, csv_filename)
            print("Finished.")

        elif option == 'C':
            variable_neighbourhood = True
            multistart = False
            csv_filename = 'results_C_Variable_Neighbourhood_Ascent.csv'
            neighbourhood_checker(num_variables, clauses, variable_neighbourhood, multistart)
            
        elif option == 'D':
            print("Running...")
            variable_neighbourhood = True
            multistart = True
            csv_filename = 'results_D_Multistart_Variable_Neighbourhood_Ascent.csv'
            multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart, csv_filename)
            print("Finished.")


if __name__ == "__main__":
    main()