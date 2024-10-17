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
            order = random.sample(range(num_variables), num_variables)

            for indexes in random.sample(list(combinations(order, hamming_distance)), len(order)):
                neighbour_possibility = current_possibility.copy()

                for index in indexes:
                    neighbour_possibility[index] = 1 - current_possibility[index]
                
                neighbour_clauses = clause_counter(neighbour_possibility, clauses)
                function_evaluations +=1

                if(neighbour_clauses > satisfied_clauses):
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

def multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart):
    """
    Runs the multistart hillclimb algorithm multiple times (30 times, max_runs) and tracks the best result across the runs.
    """

    subdirectory = "uf100-01"
    filepath = os.path.join(subdirectory, "results_Multistart_Next_Ascent_Hillclimbing_uf100-01.csv")
    filepath_best = os.path.join(subdirectory, "best_results_Multistart_Next_Ascent_Hillclimbing_uf100-01.csv")

    best_multistart_clauses = 0
    best_function_evaluations = 0
    best_solution = []
    big_time = time.time()  # Track total runtime

    # Run the algorithm for each of the max_runs (30 runs in total)
    for run_num in range(max_runs):  # Assuming max_runs = 30
        function_counter = 0
        current_best_solution = []
        current_best_satisfied_clauses = 0
        run_start_time = time.time()  # Start time for this run

        # Continue until max_evaluations is reached or global optimum is found
        while function_counter <= max_evaluations:
            current_solution, current_satisfied_clauses, current_function_evaluations = neighbourhood_checker(
                num_variables, clauses, variable_neighbourhood, multistart)

            # Update best solution found in this run
            if current_satisfied_clauses > current_best_satisfied_clauses:
                current_best_satisfied_clauses = current_satisfied_clauses
                current_best_solution = current_solution

            function_counter += current_function_evaluations

            # Stop if the global optimum is found or if we exceed max_evaluations
            if current_satisfied_clauses == num_clauses or function_counter >= max_evaluations:
                break

        # Save the best solution for this run (global optimum or best found)
        with open(filepath, mode='a', newline='') as file:
            writer = csv.writer(file)
            boolean_result = convert_to_boolean(current_best_solution)
            writer.writerow(' ')
            writer.writerow([f'Solution number {run_num + 1}'])
            writer.writerow([str(boolean_result)])
            writer.writerow(['Clauses Satisfied', 'Function Evaluations', 'Time (seconds)'])
            writer.writerow([current_best_satisfied_clauses, function_counter, time.time() - run_start_time])

        # Update the overall best solution across all runs
        if current_best_satisfied_clauses > best_multistart_clauses:
            best_multistart_clauses = current_best_satisfied_clauses
            best_function_evaluations = function_counter
            best_solution = current_best_solution

    # Save the overall best solution across all runs
    with open(filepath_best, mode='a', newline='') as file:
        writer = csv.writer(file)
        boolean_result = convert_to_boolean(best_solution)
        writer.writerow(' ')
        writer.writerow(['Best Solution Across All Runs'])
        writer.writerow([str(boolean_result)])
        writer.writerow(['Most Clauses Satisfied', 'Most Function Evaluations', 'Total Time (seconds)'])
        writer.writerow([best_multistart_clauses, best_function_evaluations, time.time() - big_time])

    return best_solution, best_multistart_clauses, best_function_evaluations, time.time() - big_time

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
            best_solution, best_clauses, best_function_evaluations, best_time = neighbourhood_checker(num_variables, clauses, variable_neighbourhood, multistart)
            csv_filename = 'results_A_Next_Ascent_Hillclimbing.csv'
        
        elif option == 'B':
            print("Running...")
            variable_neighbourhood = False
            multistart = True
            best_solution, best_clauses, best_function_evaluations, best_time = multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart)
            csv_filename = 'results_B_Multistart_Next_Ascent_Hillclimbing.csv'
            print("Finished.")

        elif option == 'C':
            variable_neighbourhood = True
            multistart = False
            best_solution, best_clauses, best_function_evaluations, best_time = neighbourhood_checker(num_variables, clauses, variable_neighbourhood, multistart)
            csv_filename = 'results_C_Variable_Neighbourhood_Ascent.csv'

        elif option == 'D':
            print("Running...")
            variable_neighbourhood = True
            multistart = True
            best_solution, best_clauses, best_function_evaluations, best_time= multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood, multistart)
            csv_filename = 'results_D_Multistart_Variable_Neighbourhood_Ascent.csv'
            print("Finished.")

        
        # boolean_result = convert_to_boolean(best_solution)

        # with open(csv_filename, mode='a', newline='') as file:
        #     writer = csv.writer(file)
        #     # Write the header
        #     if option == 'B' or option == 'D':
        #         writer.writerow(['Best Solution', 'Clauses Satisfied', 'Function Evaluations', 'Time (seconds)', 'Avg Time per Restart'])
        #         writer.writerow([boolean_result, best_clauses, best_function_evaluations, best_time, avg_time_per_restart])
        #     else:
        #         writer.writerow(['Best Solution', 'Clauses Satisfied', 'Function Evaluations', 'Time (seconds)'])
        #         writer.writerow([boolean_result, best_clauses, best_function_evaluations, best_time])

if __name__ == "__main__":
    main()