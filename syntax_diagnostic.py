"""
Create a simple diagnostic script to identify the exact syntax error
"""


def find_syntax_errors():
    """Find the most likely syntax errors causing the issue"""

    print("🔍 DIAGNOSTIC - FINDING SYNTAX ERRORS")
    print("=" * 50)

    file_path = "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\monthly_report.html"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")

    # Look for common JavaScript syntax issues
    issues = []

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Skip Django template lines
        if "{{" in line_stripped or "{%" in line_stripped:
            continue

        # Look for specific patterns that cause "function statement requires a name"
        patterns_to_check = [
            (r"}\s*function\s*\(", "Function without name after closing brace"),
            (r"}\s*error\s*:", "Object property after closing brace"),
            (
                r"\.catch\([^)]*\)[^;]*function",
                "Function after catch without proper separation",
            ),
            (r"function\s*function", "Double function keyword"),
        ]

        import re

        for pattern, description in patterns_to_check:
            if re.search(pattern, line_stripped):
                issues.append(
                    {
                        "line": i,
                        "content": line_stripped,
                        "issue": description,
                        "type": "HIGH_PRIORITY",
                    }
                )

    # Look for specific lines that are problematic
    problem_indicators = [
        "error: function",
        "} function",
        "function (",  # Missing name
        "} error:",
        "catch(error) {",
        ".catch(error =>",
    ]

    for i, line in enumerate(lines, 1):
        for indicator in problem_indicators:
            if indicator in line and "{{" not in line and "{%" not in line:
                issues.append(
                    {
                        "line": i,
                        "content": line.strip()[:100],
                        "issue": f"Contains problematic pattern: {indicator}",
                        "type": "MEDIUM_PRIORITY",
                    }
                )

    # Display results
    if issues:
        print(f"❌ FOUND {len(issues)} POTENTIAL ISSUES:")
        print("-" * 50)

        # Group by priority
        high_priority = [i for i in issues if i["type"] == "HIGH_PRIORITY"]
        medium_priority = [i for i in issues if i["type"] == "MEDIUM_PRIORITY"]

        if high_priority:
            print("🚨 HIGH PRIORITY ISSUES:")
            for issue in high_priority:
                print(f"   Line {issue['line']}: {issue['issue']}")
                print(f"   Code: {issue['content']}")
                print()

        if medium_priority:
            print("⚠️ MEDIUM PRIORITY ISSUES:")
            for issue in medium_priority[:5]:  # Limit to first 5
                print(f"   Line {issue['line']}: {issue['issue']}")
                print(f"   Code: {issue['content']}")
                print()
    else:
        print("✅ NO OBVIOUS SYNTAX PATTERNS FOUND")

    # Suggest fixes
    print("💡 SUGGESTED FIXES:")
    print("-" * 30)
    print("1. Check for missing semicolons after .catch() blocks")
    print("2. Look for 'error: function' patterns that should be '.catch(error =>'")
    print("3. Ensure all functions have names or are properly assigned")
    print("4. Check for missing closing brackets/braces")

    return len(issues) == 0


if __name__ == "__main__":
    is_clean = find_syntax_errors()
