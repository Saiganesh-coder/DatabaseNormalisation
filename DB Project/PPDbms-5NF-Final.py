import pandas as pd
import os  

# Prompt the user to enter the file name or path
file_path = input("Enter the file name (if in the same folder) or full path (if in a different folder): ").strip()

# Check if the file exists in the current directory or specified path
if not os.path.isfile(file_path):
    print(f"Error: The file '{file_path}' does not exist. Please check the path or filename.")
    exit(1)  # Exit the program if the file is not found

# Read tables and functional dependencies
tables_df = pd.read_excel(file_path, sheet_name='Tables')
fds_df = pd.read_excel(file_path, sheet_name='FunctionalDependencies')

# Parse input tables and FDs
def parse_tables_and_fds(tables_df, fds_df):
    tables = {}
    fds = {}

    for _, row in tables_df.iterrows():
        table_name = row['Table Name']
        attributes = [attr.strip() for attr in row['Attributes'].split(',')]
        primary_key = [key.strip() for key in row['Primary Key'].split(',')]
        multivalued_attributes = [attr.strip() for attr in row['Multi-Valued Attributes'].split(',')] if pd.notna(row['Multi-Valued Attributes']) else []

        tables[table_name] = {
            'attributes': attributes,
            'primary_key': primary_key,
            'multivalued_attributes': multivalued_attributes
        }

    for _, row in fds_df.iterrows():
        table_name = row['Table Name']
        lhs = [attr.strip() for attr in row['LHS (Determinants)'].split(',')]
        rhs = [attr.strip() for attr in row['RHS (Dependents)'].split(',')]
        fd_type = row['FD Type'].strip() if pd.notna(row['FD Type']) else ''

        if table_name not in fds:
            fds[table_name] = []

        fds[table_name].append({'lhs': lhs, 'rhs': rhs, 'type': fd_type})

    return tables, fds

# Normalize to 1NF (removes multi-valued attributes)
def normalize_to_1nf(tables):
    decomposed_tables = {}

    for table_name, details in tables.items():
        attributes = details['attributes']
        primary_key = details['primary_key']
        multivalued_attributes = details['multivalued_attributes']

        # Step 1: Create a new table for each multi-valued attribute
        for mv_attr in multivalued_attributes:
            new_primary_key = primary_key + [mv_attr]  # Composite primary key
            new_table_name = f"{table_name}_{mv_attr}"

            decomposed_tables[new_table_name] = {
                'attributes': new_primary_key,
                'primary_key': new_primary_key
            }

        # Step 2: Create the refined original table without multi-valued attributes
        refined_attributes = list(set(attributes) - set(multivalued_attributes))

        decomposed_tables[table_name] = {
            'attributes': refined_attributes,
            'primary_key': primary_key
        }

    return decomposed_tables

# Normalize to 2NF (removing partial dependencies)
def normalize_to_2nf(tables, fds):
    """Normalize tables to 2NF and return the transformed tables."""
    normalized_tables = {}

    for table_name, details in tables.items():
        attributes = details['attributes']
        primary_key = details['primary_key']
        table_fds = fds.get(table_name, [])

        non_prime_attributes = set(attributes) - set(primary_key)
        partial_dependencies = []

        # Identify partial dependencies (LHS is a proper subset of primary key)
        for fd in table_fds:
            lhs = set(fd['lhs'])
            rhs = set(fd['rhs'])

            if lhs < set(primary_key) and rhs.intersection(non_prime_attributes):
                partial_dependencies.append(fd)

        # If there are partial dependencies, decompose the table
        for pd in partial_dependencies:
            lhs = pd['lhs']
            rhs = pd['rhs']
            new_table_name = f"{table_name}_{'_'.join(rhs)}"

            normalized_tables[new_table_name] = {
                'attributes': lhs + rhs,
                'primary_key': lhs
            }

        # Create the original table without partial dependencies
        remaining_attributes = list(
            set(attributes) - set(attr for fd in partial_dependencies for attr in fd['rhs'])
        ) + primary_key  # Add primary key attributes

        # Remove duplicates
        remaining_attributes = list(set(remaining_attributes))

        normalized_tables[table_name] = {
            'attributes': remaining_attributes,
            'primary_key': primary_key
        }

    return normalized_tables

# Normalize to 3NF (removing transitive dependencies)
def normalize_to_3nf(tables, fds):
    """Normalize tables to 3NF and return the transformed tables."""
    normalized_tables = {}

    for table_name, details in tables.items():
        attributes = details['attributes']
        primary_key = details['primary_key']
        table_fds = fds.get(table_name, [])

        # Identify transitive dependencies
        transitive_dependencies = []
        non_prime_attributes = set(attributes) - set(primary_key)

        # Build a mapping of non-prime attributes to their functional dependencies
        for fd in table_fds:
            lhs = set(fd['lhs'])
            rhs = set(fd['rhs'])

            if lhs != set(primary_key) and lhs.issubset(non_prime_attributes):
                for attr in rhs:
                    if attr in non_prime_attributes:
                        transitive_dependencies.append({'lhs': lhs, 'rhs': [attr]})

        # If there are transitive dependencies, decompose the table
        for td in transitive_dependencies:
            lhs = td['lhs']
            rhs = td['rhs']
            new_table_name = f"{table_name}_{'_'.join(rhs)}"

            normalized_tables[new_table_name] = {
                'attributes': list(lhs) + list(rhs),
                'primary_key': list(lhs)
            }

        # Create the original table without transitive dependencies
        remaining_attributes = list(
            set(attributes) - set(attr for td in transitive_dependencies for attr in td['rhs'])
        ) + primary_key  # Add primary key attributes

        # Remove duplicates
        remaining_attributes = list(set(remaining_attributes))

        normalized_tables[table_name] = {
            'attributes': remaining_attributes,
            'primary_key': primary_key
        }

    return normalized_tables

# Normalize to BCNF
def normalize_to_bcnf(tables, fds):
    """Normalize tables to BCNF and return the transformed tables."""
    normalized_tables = {}

    for table_name, details in tables.items():
        attributes = details['attributes']
        primary_key = details['primary_key']
        table_fds = fds.get(table_name, [])

        # Create a working copy of attributes and keys
        remaining_attributes = set(attributes)
        remaining_primary_key = set(primary_key)

        # Check for BCNF violations
        while True:
            bcnf_violations = []
            for fd in table_fds:
                lhs = set(fd['lhs'])
                rhs = set(fd['rhs'])

                # Check if the LHS is a superkey
                if not (lhs == remaining_primary_key or lhs.issubset(remaining_attributes)):
                    bcnf_violations.append(fd)

            if not bcnf_violations:
                break  # No BCNF violations found, exit loop

            # Decompose the table based on the first violation found
            fd = bcnf_violations[0]
            lhs = fd['lhs']
            rhs = fd['rhs']
            new_table_name = f"{table_name}_{'_'.join(rhs)}"

            # Create a new table for the violation
            normalized_tables[new_table_name] = {
                'attributes': list(lhs) + list(rhs),
                'primary_key': list(lhs)
            }

            # Update the remaining attributes
            remaining_attributes -= set(rhs)

        # Add the remaining attributes to the current table
        normalized_tables[table_name] = {
            'attributes': list(remaining_attributes),
            'primary_key': list(remaining_primary_key)
        }

    return normalized_tables

# Normalize to 4NF using multivalued dependencies
def normalize_to_4nf(tables, fds):
    """Normalize tables to 4NF and return the transformed tables."""
    normalized_tables = {}

    for table_name, details in tables.items():
        normalized_tables[table_name] = details  # Start by copying existing tables

    for table_fds in fds.values():
        for fd in table_fds:
            if fd['type'] == 'Multivalued dependencies':  # Check for the correct key
                lhs = set(fd['lhs'])
                rhs = set(fd['rhs'])

                # Check which table has these 3 attributes (LHS + RHS)
                combined_attributes = lhs.union(rhs)
                for table_name, details in normalized_tables.items():
                    table_attributes = set(details['attributes'])

                    # If the table contains all the combined attributes, decompose it
                    if combined_attributes.issubset(table_attributes):
                        # Create new tables for each RHS attribute
                        for rhs_attr in rhs:
                            new_table_name = f"{table_name}_{'_'.join(lhs)}_{rhs_attr}"
                            normalized_tables[new_table_name] = {
                                'attributes': list(lhs) + [rhs_attr],  # LHS + one RHS
                                'primary_key': list(lhs)  # LHS becomes the primary key
                            }

                        # Remove the original table that was decomposed
                        del normalized_tables[table_name]
                        break  # Exit the loop after decomposing the table

    return normalized_tables

# Normalize to 5NF
def normalize_to_5nf(tables, fds):
    """Normalize tables to 5NF and return the transformed tables."""
    normalized_tables = {}

    for table_name, details in tables.items():
        normalized_tables[table_name] = details  # Start by copying existing tables

    # Check for join dependencies
    for table_fds in fds.values():
        for fd in table_fds:
            lhs = set(fd['lhs'])
            rhs = set(fd['rhs'])
            combined_attributes = lhs.union(rhs)

            # Check if the table has these attributes (LHS + RHS)
            for table_name, details in normalized_tables.items():
                table_attributes = set(details['attributes'])

                # If the table contains all the combined attributes
                if combined_attributes.issubset(table_attributes):
                    # Create a new table for each RHS attribute
                    for rhs_attr in rhs:
                        new_table_name = f"{table_name}_{'_'.join(lhs)}_{rhs_attr}"
                        normalized_tables[new_table_name] = {
                            'attributes': list(lhs) + [rhs_attr],  # LHS + one RHS
                            'primary_key': list(lhs)  # LHS becomes the primary key
                        }

                    # Remove the original table that was decomposed
                    del normalized_tables[table_name]
                    break  # Exit the loop after decomposing the table

    return normalized_tables

# Generate SQL CREATE TABLE statements
def generate_create_table_queries(tables):
    create_queries = []
    for table_name, details in tables.items():
        attributes = details['attributes']
        primary_key = details['primary_key']

        column_definitions = [f"`{attr}` VARCHAR(255)" for attr in attributes]  # Modify type as needed
        primary_key_definition = f"PRIMARY KEY ({', '.join(f'`{key}`' for key in primary_key)})"
        full_definition = ",\n    ".join(column_definitions) + f",\n    {primary_key_definition}"
        create_query = f"CREATE TABLE `{table_name}` (\n    {full_definition}\n);"
        create_queries.append(create_query)
    return create_queries

def save_queries_to_file(queries, filename="normalized_tables.sql"):
    """Save the generated SQL queries to a text file."""
    with open(filename, 'w') as file:
        for query in queries:
            file.write(query + "\n")
    print(f"\nSQL queries saved to '{filename}'.")

def normalize_tables_to_user_level(tables, fds, level):
    # Normalize based on the input string level
    if level == "1NF":
        tables = normalize_to_1nf(tables)
    elif level == "2NF":
        tables = normalize_to_1nf(tables)
        tables = normalize_to_2nf(tables, fds)
    elif level == "3NF":
        tables = normalize_to_1nf(tables)
        tables = normalize_to_2nf(tables, fds)
        tables = normalize_to_3nf(tables, fds)
    elif level == "BCNF":
        tables = normalize_to_1nf(tables)
        tables = normalize_to_2nf(tables, fds)
        tables = normalize_to_3nf(tables, fds)
        tables = normalize_to_bcnf(tables, fds)
    elif level == "4NF":
        tables = normalize_to_1nf(tables)
        tables = normalize_to_2nf(tables, fds)
        tables = normalize_to_3nf(tables, fds)
        tables = normalize_to_bcnf(tables, fds)
        tables = normalize_to_4nf(tables, fds)
    elif level == "5NF":
        tables = normalize_to_1nf(tables)
        tables = normalize_to_2nf(tables, fds)
        tables = normalize_to_3nf(tables, fds)
        tables = normalize_to_bcnf(tables, fds)
        tables = normalize_to_4nf(tables, fds)
        tables = normalize_to_5nf(tables, fds)
    else:
        print("Invalid normalization form! Please enter a valid normalization form: 1NF, 2NF, 3NF, BCNF, or 5NF.")
        return None
    return tables

# Main function
def main():
    # Load the input data
    tables, fds = parse_tables_and_fds(tables_df, fds_df)

    # Get user input for the normalization form
    print("Choose the highest normalization form (1NF, 2NF, 3NF, BCNF, 4NF or 5NF): ")
    level = input("Enter the normalization form: ").strip().upper()

    # Normalize tables based on the user-selected normalization form
    normalized_tables = normalize_tables_to_user_level(tables, fds, level)

    if normalized_tables:
        # Generate SQL queries for the normalized tables
        create_table_queries = generate_create_table_queries(normalized_tables)

        # Print the SQL queries
        print("\nGenerated SQL CREATE TABLE Statements:")
        for query in create_table_queries:
            print(query)

        # Save the SQL queries to a text file
        save_queries_to_file(create_table_queries)

# Run the main function
if __name__ == "__main__":
    main()
