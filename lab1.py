def read_cnf_file(filename):
    clauses = []
    num_variables = 0
    num_clauses = 0

    with open(filename, 'r') as file:
        for line in file:
            line = line.strip()
            
            #If line starts with c, so a comment, it'll run to the next line
            if line.startswith('c'):
                continue
            
            #Reads the first line to store the number of variables and the number of clauses in an instance
            if line.startswith('p cnf'):
                parts = line.split()
                num_variables = int(parts[2])
                num_clauses = int(parts[3])
                continue
            
            
            if line and not line.startswith('%'):
                clause = list(map(int, line.split()))
                clause.pop()
                clauses.append(clause)
    
    return num_variables, num_clauses, clauses

filename = 'uf20-01.cnf'
num_variables, num_clauses, clauses = read_cnf_file(filename)

print(f"Number of variables: {num_variables}")
print(f"Number of clauses: {num_clauses}")
print("Clauses:")
for clause in clauses:
    print(clause)
