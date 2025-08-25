"""
Find exact bracket mismatch locations
"""


def find_bracket_issues():
    file_path = "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\monthly_report.html"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # Track brackets in JavaScript sections only
    in_script = False
    bracket_stack = []
    issues = []

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Detect script sections
        if "<script>" in line_stripped or "document.addEventListener" in line_stripped:
            in_script = True
        elif "</script>" in line_stripped:
            in_script = False

        if not in_script:
            continue

        # Skip Django template syntax and comments
        if (
            "{{" in line_stripped
            or "{%" in line_stripped
            or line_stripped.startswith("//")
        ):
            continue

        # Process each character
        for j, char in enumerate(line):
            if char == "(":
                bracket_stack.append(("(", i, j))
            elif char == ")":
                if bracket_stack and bracket_stack[-1][0] == "(":
                    bracket_stack.pop()
                else:
                    issues.append(
                        f"Line {i}, Col {j}: Unmatched closing parenthesis ')'"
                    )
            elif char == "{":
                bracket_stack.append(("{", i, j))
            elif char == "}":
                if bracket_stack and bracket_stack[-1][0] == "{":
                    bracket_stack.pop()
                else:
                    issues.append(f"Line {i}, Col {j}: Unmatched closing brace '}}'")

    # Report unclosed brackets
    for bracket, line_num, col_num in bracket_stack:
        issues.append(f"Line {line_num}, Col {col_num}: Unclosed '{bracket}'")

    print("🔍 BRACKET ANALYSIS RESULTS:")
    print("=" * 40)

    if issues:
        print(f"❌ Found {len(issues)} bracket issues:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("✅ No bracket issues found in JavaScript sections")

    return len(issues) == 0


if __name__ == "__main__":
    find_bracket_issues()
