#!/bin/bash

# 1. Define the base name for your reports (easily changeable for your next AI cohort)
REPORT_PREFIX="bandit_report_GithubCopilot_GPT54_v1"

# 2. Define the output formats you need for your appendices and repository
FORMATS=("xml" "csv" "html" "txt" "json")

echo "Starting Bandit multi-format generation..."
echo "Target directories: Current (.) excluding .venv and tests"
echo "--------------------------------------------------------"

# 3. Loop through each format and execute the Bandit command
for FORMAT in "${FORMATS[@]}"; do
    OUTPUT_FILE="${REPORT_PREFIX}.${FORMAT}"
    echo "Generating ${FORMAT^^} report -> ${OUTPUT_FILE}..."
    
    # Run the Bandit command using your exact template
    bandit -r . -x "*/.venv/*,*/tests/*" -f "$FORMAT" -o "$OUTPUT_FILE"
    
    # Capture the exit code. 
    # 0 = No issues found, 1 = Issues found (Success for your paper!), 2 = Real Error
    EXIT_CODE=$?
    
    if [ $EXIT_CODE -eq 0 ]; then
         echo "  [✓] Done (0 issues found)."
    elif [ $EXIT_CODE -eq 1 ]; then
         echo "  [✓] Done (Vulnerabilities found and logged)."
    else
         echo "  [x] Error generating ${FORMAT^^} report."
    fi
done

echo "--------------------------------------------------------"
echo "All reports successfully generated in the current directory!"