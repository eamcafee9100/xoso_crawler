"""
JavaScript Syntax Checker for monthly_report.html
"""

import os
import re


def check_js_syntax():
    """Check for common JavaScript syntax errors"""

    print("🔍 CHECKING JAVASCRIPT SYNTAX ERRORS")
    print("=" * 50)

    file_path = "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\monthly_report.html"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    errors = []

    # Common syntax error patterns
    error_patterns = [
        (r"}\s*error\s*:", "Object syntax error after closing brace"),
        (r"function\s*\(\s*\)\s*{[^}]*function\s*\(", "Nested function without name"),
        (r"}\s*\w+\s*:\s*function", "Property definition after closing brace"),
        (r"\.catch\([^)]*\)\s*[^;]\s*\w+\s*:", "Code after catch block"),
        (r"function\s+function", "Double function keyword"),
        (r"}\s*}\s*[^;,}\s]", "Missing semicolon after closing braces"),
    ]

    # Check each line
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Skip empty lines and comments
        if (
            not line_stripped
            or line_stripped.startswith("//")
            or line_stripped.startswith("/*")
        ):
            continue

        # Check for error patterns
        for pattern, description in error_patterns:
            if re.search(pattern, line_stripped):
                errors.append(
                    {
                        "line": i,
                        "content": (
                            line_stripped[:100] + "..."
                            if len(line_stripped) > 100
                            else line_stripped
                        ),
                        "error": description,
                        "pattern": pattern,
                    }
                )

    # Check for unclosed brackets/braces
    open_brackets = {"(": 0, "{": 0, "[": 0}
    in_string = False
    string_char = None

    for i, line in enumerate(lines, 1):
        for char in line:
            if char in ['"', "'"] and not in_string:
                in_string = True
                string_char = char
            elif char == string_char and in_string:
                in_string = False
                string_char = None
            elif not in_string:
                if char == "(":
                    open_brackets["("] += 1
                elif char == ")":
                    open_brackets["("] -= 1
                elif char == "{":
                    open_brackets["{"] += 1
                elif char == "}":
                    open_brackets["{"] -= 1
                elif char == "[":
                    open_brackets["["] += 1
                elif char == "]":
                    open_brackets["["] -= 1

    # Report bracket mismatches
    for bracket, count in open_brackets.items():
        if count != 0:
            close_bracket = {"(": ")", "{": "}", "[": "]"}[bracket]
            errors.append(
                {
                    "line": "Multiple",
                    "content": f"Bracket mismatch: {bracket}...{close_bracket}",
                    "error": f"Unclosed {bracket} brackets: {count}",
                    "pattern": "Bracket counting",
                }
            )

    # Display results
    if errors:
        print(f"❌ FOUND {len(errors)} SYNTAX ERRORS:")
        print("-" * 50)

        for error in errors:
            print(f"📍 Line {error['line']}: {error['error']}")
            print(f"   Code: {error['content']}")
            print(f"   Pattern: {error['pattern']}")
            print()
    else:
        print("✅ NO OBVIOUS SYNTAX ERRORS FOUND")

    # Check for specific problematic sections
    print("\n🔍 CHECKING SPECIFIC SECTIONS:")
    print("-" * 30)

    # Check for Promise.allSettled section
    promise_sections = re.findall(
        r"Promise\.allSettled.*?\.catch.*?(?=function|\n\s*})", content, re.DOTALL
    )
    for i, section in enumerate(promise_sections):
        if "error:" in section and ".catch(" in section:
            print(f"⚠️  Promise section {i+1} has potential syntax issues")
            print(f"   Contains both .catch() and error: property")

    # Check for function definitions
    function_defs = re.findall(r"function\s+(\w+)?", content)
    unnamed_functions = [f for f in function_defs if not f]
    if unnamed_functions:
        print(
            f"⚠️  Found {len(unnamed_functions)} potentially unnamed function statements"
        )

    return len(errors) == 0


if __name__ == "__main__":
    is_clean = check_js_syntax()
    if is_clean:
        print("\n🎉 SYNTAX CHECK PASSED!")
    else:
        print("\n❌ SYNTAX ERRORS NEED FIXING")
