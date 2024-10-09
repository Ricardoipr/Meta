def read_cnf_file(filename):
    """
    Used to read the CNF file and extract the necessary data.
    """
    clauses = []
    num_variables = 0

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
                    continue

                # Process the clause lines by removing the 0 at the end of each line.
                clause = list(map(int, line.split()))
                if clause and clause[-1] == 0:
                    clause.pop()
                clauses.append(clause)
    
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
        return None, None, None

    return num_variables, clauses


def is_clause_satisfied(clause, possibility):
    """
    Checks if a single clause is satisfied by the given possibility.
    """
    for literal in clause:
        var = abs(literal) - 1
        if (literal > 0 and possibility[var] == 1):
            return True
        if (literal < 0 and possibility[var] == 0):
            return True
    return False


def is_formula_satisfied(clauses, possibility):
    """
    Checks if the entire formula is satisfied by the given possibility.
    """
    for clause in clauses:
        if not is_clause_satisfied(clause, possibility):
            return False
    return True


def solution_satisfier(num_variables, clauses):
    """
    Generates all possible options of boolean values and finds satisfying ones.
    """
    possibilities = []

    for i in range(2 ** num_variables):
        row = [(i >> j) & 1 for j in range(num_variables-1, -1, -1)]
        possibilities.append(row)

    satisfying_possibilities = [possibility for possibility in possibilities if is_formula_satisfied(clauses, possibility)]
    return satisfying_possibilities


def convert_to_boolean(assignment):
    """
    Will convert the result's 0s to False and 1s to True.
    """
    return [False if val == 0 else True for val in assignment]


def main():
    filename = input('Enter file name: ')
    num_variables, clauses = read_cnf_file(filename)
    
    # Will exit if the file is not found.
    if num_variables is None or clauses is None:
        return

    results = solution_satisfier(num_variables, clauses)

    print(f"Number of satisfying solutions: {len(results)}")
    for result in results:
        boolean_result = convert_to_boolean(result)
        print(boolean_result)


if __name__ == "__main__":
    main()
