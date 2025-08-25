#!/usr/bin/env python
"""
Test template number generation
"""
# Test Django template logic
def test_number_generation():
    """Test how Django template generates numbers"""
    print("=== Testing Number Generation Logic ===")
    
    # Simulate Django template logic
    digits = "0123456789"
    
    print("Method 1: Simple concatenation")
    for i in digits:
        for j in digits:
            number = i + j
            print(number, end=" ")
        print()
    
    print("\nMethod 2: With zero padding")
    for i in range(10):
        for j in range(10):
            number = f"{i:01d}{j:01d}"
            print(number, end=" ")
        print()
    
    print("\nMethod 3: Using Django-like add filter simulation")
    for i in digits:
        for j in digits:
            # Simulate Django's add filter behavior
            try:
                # Try to convert to int first, then back to string
                i_int = int(i)
                j_int = int(j) 
                number = str(i_int) + str(j_int)  # This is what add filter might do
                print(number, end=" ")
            except:
                number = i + j
                print(number, end=" ")
        print()

if __name__ == "__main__":
    test_number_generation()
