import time
import re

# Global variables dictionary to store variable values
variables = {}

# Function to evaluate commands inside the .tec script
def run_command(command):
    command = command.strip()

    # Handle variable assignment
    match = re.match(r'(\w+)(\s*=\s*)(.*)', command)
    if match:
        var_name = match.group(1)
        value = match.group(3)

        # If it's a string, remove the quotes
        if value.startswith('str("') and value.endswith('")'):
            value = value[5:-2]

        # Assign the value to the variable
        variables[var_name] = value
        print(f"Variable {var_name} set to: {value}")
        return

    # Handle console logging
    if command.startswith('run browser.func(console.log'):
        match = re.match(r'run browser.func\(console.log\((.*)\)\)', command)
        if match:
            log_value = match.group(1).strip()
            if log_value in variables:
                log_value = variables[log_value]
            print(log_value)
        return

    # Handle wait
    if command.startswith('wait('):
        match = re.match(r'wait\((\d+s)\)', command)
        if match:
            seconds = int(match.group(1).replace('s', ''))
            print(f"Waiting for {seconds} seconds...")
            time.sleep(seconds)
        return

    # Handle function calls
    if command.startswith('run browser.func'):
        match = re.match(r'run browser.func\((.*)\)', command)
        if match:
            func_command = match.group(1).strip()
            if func_command.startswith('var_edit'):
                edit_var(func_command)
            return

    # Handle conditional statements
    if command.startswith('if'):
        match = re.match(r'if \((.*)\) \{', command)
        if match:
            condition = match.group(1)
            if evaluate_condition(condition):
                return  # Continue parsing within this conditional block

    if command.startswith('else'):
        return  # Handle the else block

    # Handle end of function or block
    if command.startswith('end'):
        return  # Ends the current function or block

# Function to evaluate conditionals (basic comparisons)
def evaluate_condition(condition):
    condition = condition.strip()

    # Check if the condition is a simple equality check
    if "==" in condition:
        var_name, value = condition.split("==")
        var_name = var_name.strip()
        value = value.strip().strip('"')

        if var_name in variables:
            return variables[var_name] == value

    return False

# Function to handle variable edits (e.g., changing a variable value)
def edit_var(command):
    match = re.match(r'var_edit\((\w+)\s*=\s*(.*)\)', command)
    if match:
        var_name = match.group(1)
        new_value = match.group(2).strip()

        # If it's a string, remove quotes
        if new_value.startswith('str("') and new_value.endswith('")'):
            new_value = new_value[5:-2]

        variables[var_name] = new_value
        print(f"Variable {var_name} updated to: {new_value}")

# Function to simulate the entire script execution
def parse_tec_script(script):
    lines = script.strip().splitlines()
    for line in lines:
        run_command(line)

# This function is where the .tec script will be parsed and run
def parse_tec(script):
    parse_tec_script(script)
