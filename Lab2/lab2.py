import random

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
                    num_clauses = int(parts[3])
                    num_variables = int(parts[2])
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

def hillclimb(num_variables, num_clauses, clauses):

    initial_possibility = [random.choice([0,1]) for _ in range(num_variables)]

    for value in initial_possibility:
        print(initial_possibility[value])   
        # var = abs(literal) - 1
        # if (literal > 0 and clauses[var] == 1):
        #     return 1
        # if (literal < 0 and clauses[var] == 0):
        #     return 0

    return 1, 2, 3

def convert_to_boolean(assignment):
    """
    Will convert the result's 0s to False and 1s to True.
    """
    return [False if val == 0 else True for val in assignment]

def main():
    filename = input('Enter file name: ')

    # Data read from the cnf file
    num_variables, num_clauses, clauses = read_cnf_file(filename)

    # Data from running the algorithm
    best_solution, evaluation_number, time_taken = hillclimb(num_variables, num_clauses, clauses)
    
    # Will exit if the file is not found.
    if num_variables is None or clauses is None:
        return

    # results = solution_satisfier(num_variables, clauses)

    # print(f"Input: {len(clauses)}")
    # for clause in clauses:
    #     # boolean_result = convert_to_boolean(clause)
    #     print(clause)


if __name__ == "__main__":
    main()