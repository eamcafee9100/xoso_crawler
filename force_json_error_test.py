#!/usr/bin/env python3
"""
Force JSON Serialization Error Test
Reproduce exact error to understand the root cause
"""

import json
from datetime import datetime

# Test 1: Standard JSON with booleans (should work in modern Python)
print("🧪 Test 1: Standard JSON encoder with booleans")
try:
    result = json.dumps({"test": True, "test2": False})
    print(f"   ✅ Standard JSON works: {result}")
except Exception as e:
    print(f"   ❌ Standard JSON failed: {e}")

# Test 2: Try to reproduce the exact error
print("\n🧪 Test 2: Trying to reproduce 'Object of type bool is not JSON serializable'")


# Custom JSONEncoder that might cause issues
class ProblematicEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        # Note: No boolean handling here
        return super().default(obj)


try:
    data = {
        "status": "success",
        "boolean_value": True,
    }
    result = json.dumps(data, cls=ProblematicEncoder)
    print(f"   ✅ ProblematicEncoder works: {result}")
except Exception as e:
    print(f"   ❌ ProblematicEncoder failed: {e}")

# Test 3: Django-like scenario
print("\n🧪 Test 3: Django JsonResponse simulation")


class MockJsonResponse:
    def __init__(self, data, encoder=None, safe=True):
        self.data = data
        self.encoder = encoder
        self.safe = safe

        # Django JsonResponse behavior
        if encoder:
            self.content = json.dumps(data, cls=encoder, ensure_ascii=False)
        else:
            # This might cause issues if Django has custom serialization
            self.content = json.dumps(data, ensure_ascii=False)


try:
    data = {"boolean_field": True}
    response = MockJsonResponse(data)
    print(f"   ✅ MockJsonResponse works: {response.content}")
except Exception as e:
    print(f"   ❌ MockJsonResponse failed: {e}")

# Test 4: Check if there are any special object types
print("\n🧪 Test 4: Special object types that might cause issues")


class CustomObject:
    def __init__(self, value):
        self.value = value
        self.is_active = True  # Boolean in custom object


special_data = {"custom_obj": CustomObject("test"), "boolean": True}


# Test with CustomJSONEncoder (fixed version)
class FixedCustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, bool):
            return "enabled" if o else "disabled"
        elif isinstance(o, datetime):
            return o.isoformat()
        elif hasattr(o, "__dict__"):
            return o.__dict__
        return super().default(o)

    def encode(self, o):
        return super().encode(self._convert_booleans(o))

    def _convert_booleans(self, obj):
        if isinstance(obj, bool):
            return "enabled" if obj else "disabled"
        elif isinstance(obj, dict):
            return {key: self._convert_booleans(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_booleans(item) for item in obj]
        elif isinstance(obj, tuple):
            return tuple(self._convert_booleans(item) for item in obj)
        else:
            return obj


try:
    result = json.dumps(special_data, cls=FixedCustomJSONEncoder)
    print(f"   ✅ FixedCustomJSONEncoder with special objects works!")

    # Parse back to check
    parsed = json.loads(result)
    print(f"   📊 custom_obj.is_active: '{parsed['custom_obj']['is_active']}'")
    print(f"   📊 boolean: '{parsed['boolean']}'")

except Exception as e:
    print(f"   ❌ FixedCustomJSONEncoder failed: {e}")

# Test 5: Django model-like objects (simulate database results)
print("\n🧪 Test 5: Django model-like objects (database simulation)")


class MockModel:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# Simulate database query results
db_results = [
    MockModel(id=1, number=15, is_active=True, is_hot=False),
    MockModel(id=2, number=87, is_active=False, is_hot=True),
]

db_data = {"database_results": db_results, "query_successful": True}

try:
    result = json.dumps(db_data, cls=FixedCustomJSONEncoder)
    print(f"   ✅ Database-like objects serialized successfully!")

    # Check for boolean conversion
    parsed = json.loads(result)
    first_result = parsed["database_results"][0]
    print(f"   📊 First result is_active: '{first_result['is_active']}'")
    print(f"   📊 Query successful: '{parsed['query_successful']}'")

except Exception as e:
    print(f"   ❌ Database-like serialization failed: {e}")

print("\n" + "=" * 60)
print("🎯 CONCLUSION:")
print("If all tests pass, then the 'Object of type bool is not JSON serializable'")
print("error is likely caused by:")
print("1. Old code being cached by Django")
print("2. A different code path not using safe_json_response")
print("3. Third-party library or Django internal serialization")
print("4. Database model serialization bypassing CustomJSONEncoder")
print("=" * 60)
