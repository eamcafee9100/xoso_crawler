"""
Extract JavaScript from template and validate syntax
"""

import re


def extract_and_validate_js():
    """Extract JavaScript sections and create a test file"""

    print("🔍 EXTRACTING JAVASCRIPT FOR VALIDATION")
    print("=" * 50)

    file_path = "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\monthly_report.html"

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Find JavaScript sections
    js_sections = []

    # Extract content between <script> tags
    script_pattern = r"<script[^>]*>(.*?)</script>"
    matches = re.findall(script_pattern, content, re.DOTALL)

    for match in matches:
        js_sections.append(match)

    # Also extract inline JS (document.addEventListener blocks)
    inline_js_pattern = (
        r"(document\.addEventListener.*?(?=</script>|document\.addEventListener|$))"
    )
    inline_matches = re.findall(inline_js_pattern, content, re.DOTALL)

    for match in inline_matches:
        if match not in str(js_sections):  # Avoid duplicates
            js_sections.append(match)

    print(f"📊 Found {len(js_sections)} JavaScript sections")

    # Combine all JS
    combined_js = ""
    for i, section in enumerate(js_sections):
        # Clean Django template syntax
        cleaned = re.sub(r"{%.*?%}", "", section)
        cleaned = re.sub(r"{{.*?}}", '""', cleaned)

        combined_js += f"\n\n// ===== SECTION {i+1} =====\n"
        combined_js += cleaned

    # Write to test file
    test_file = "c:\\Users\\n2t\\Documents\\xoso_crawler\\js_test.js"

    with open(test_file, "w", encoding="utf-8") as f:
        f.write("// JavaScript extracted from monthly_report.html\n")
        f.write("// This file is for syntax validation only\n\n")

        # Add some mock functions/variables for validation
        f.write("// Mock functions and variables\n")
        f.write(
            "const $ = function() { return { on: function() {}, ajax: function() {} }; };\n"
        )
        f.write("const console = { log: function() {}, error: function() {} };\n")
        f.write(
            "const document = { addEventListener: function() {}, getElementById: function() { return { value: '', innerHTML: '' }; } };\n"
        )
        f.write("const window = {};\n")
        f.write("const jQuery = $;\n\n")

        f.write(combined_js)

    print(f"✅ JavaScript extracted to: {test_file}")
    print(f"📝 Total characters: {len(combined_js)}")

    # Basic syntax check
    basic_issues = []
    lines = combined_js.split("\n")

    open_braces = 0
    open_parens = 0

    for i, line in enumerate(lines, 1):
        if "//" in line:
            line = line[: line.index("//")]  # Remove comments

        for char in line:
            if char == "{":
                open_braces += 1
            elif char == "}":
                open_braces -= 1
            elif char == "(":
                open_parens += 1
            elif char == ")":
                open_parens -= 1

        # Check for common issues
        if "function (" in line and not line.strip().startswith("function "):
            basic_issues.append(f"Line {i}: Possible unnamed function")

        if open_braces < 0:
            basic_issues.append(f"Line {i}: Extra closing brace")

        if open_parens < 0:
            basic_issues.append(f"Line {i}: Extra closing parenthesis")

    print(f"\n🔍 BASIC SYNTAX CHECK:")
    print(f"   Unclosed braces: {open_braces}")
    print(f"   Unclosed parentheses: {open_parens}")

    if basic_issues:
        print(f"   Issues found: {len(basic_issues)}")
        for issue in basic_issues[:5]:
            print(f"   - {issue}")
    else:
        print("   ✅ No obvious issues in extracted JS")

    return test_file


if __name__ == "__main__":
    test_file = extract_and_validate_js()
    print(f"\n💡 Next step: Try to run 'node {test_file}' to validate syntax")
