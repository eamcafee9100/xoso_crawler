# security/sandbox.py
import ast
import re

class FormulaValidator:
    SAFE_CHARS = re.compile(r'^[\w\s\"\':,\[\]\{\}-]+$')
    
    @classmethod
    def sanitize_lambda(cls, code):
        """Làm sạch mã lambda trước khi eval"""
        if not cls.SAFE_CHARS.match(code):
            raise ValueError("Invalid characters in formula")
        
        parsed = ast.parse(code)
        for node in ast.walk(parsed):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.Call)):
                raise ValueError("Unsafe operations detected")
        
        return code