from itertools import combinations
import random
import re
import time

max_runs = 30
max_evaluations = 200000

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
    start_time = time.time()

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

    return current_possibility, satisfied_clauses, function_evaluations, time.time()-start_time

def neighbourhood_checker(num_variables, clauses, variable_neighbourhood):
    """
    Runs the hillclimb algorithm multiple times and tracks the best result across the runs.
    """
    best_clauses = 0
    best_function_evaluations = 0
    best_time = 0
    best_solution = []

    for _ in range(max_runs):
        current_solution, satisfied_clauses, function_evaluations, cpu_time= hillclimb(num_variables, clauses, variable_neighbourhood)
        if satisfied_clauses > best_clauses:
            best_clauses = satisfied_clauses
            best_function_evaluations = function_evaluations
            best_solution = current_solution
            best_time = cpu_time

    return best_solution, best_clauses, best_function_evaluations, best_time

def multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood):
    """
    Runs the multistart hillclimb algorithm multiple times and tracks the best result across the runs.
    """
    function_counter = 0
    best_multistart_clauses = 0
    best_function_evaluations = 0
    best_time = 0
    best_solution = []

    while best_multistart_clauses != num_clauses and function_counter <= max_evaluations:
        current_best_solution, current_best_satisfied_clauses, current_best_function_evaluations, current_best_cpu_time = neighbourhood_checker(num_variables, clauses, variable_neighbourhood)
        if current_best_satisfied_clauses > best_multistart_clauses:
            best_multistart_clauses = current_best_satisfied_clauses
            best_function_evaluations = current_best_function_evaluations
            best_solution = current_best_solution
            best_time = current_best_cpu_time
        function_counter += current_best_function_evaluations
        print(function_counter)
    
    return best_solution, best_multistart_clauses, best_function_evaluations, best_time

def convert_to_boolean(assignment):
    """
    Will convert the result's 0s to False and 1s to True.
    """
    return [bool(val) for val in assignment]

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
            best_solution, best_clauses, best_function_evaluations, best_time = neighbourhood_checker(num_variables, clauses, variable_neighbourhood)
        
        elif option == 'B':
            variable_neighbourhood = False
            best_solution, best_clauses, best_function_evaluations, best_time = multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood)

        elif option == 'C':
            variable_neighbourhood = True
            best_solution, best_clauses, best_function_evaluations, best_time = neighbourhood_checker(num_variables, clauses, variable_neighbourhood)

        elif option == 'D':
            variable_neighbourhood = True
            best_solution, best_clauses, best_function_evaluations, best_time = multistart_neighbourhood_checker(num_variables, num_clauses, clauses, variable_neighbourhood)
        
        boolean_result = convert_to_boolean(best_solution)
        print(f"The best solution found was: {boolean_result}")
        print(f"Satisfying {best_clauses} clauses")
        print(f"Taking {best_function_evaluations} function evaluations")
        print(f"And taking {best_time} seconds.")

if __name__ == "__main__":
    main()