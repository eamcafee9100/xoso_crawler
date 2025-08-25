"""
Create a minimal test template to isolate the issue
"""


def create_test_template():
    content = """{% extends "predictions_tracker/base.html" %}
{% load static %}

{% block title %}Test Template{% endblock %}

{% block extra_css %}
<style>
body { background: white; }
</style>
{% endblock %}

{% block content %}
<div class="container">
    <h1>Test Template</h1>
    <button id="testBtn">Test Button</button>
    <div id="testResult"></div>
</div>
{% endblock %}

{% block extra_js %}
<script>
document.addEventListener('DOMContentLoaded', function() {
    console.log('✅ Test template loaded successfully');
    
    const testBtn = document.getElementById('testBtn');
    const testResult = document.getElementById('testResult');
    
    if (testBtn) {
        testBtn.addEventListener('click', function() {
            testResult.innerHTML = '<p>✅ JavaScript working!</p>';
            console.log('✅ Button clicked successfully');
        });
    }
    
    // Test accuracy functions
    function testAccuracyCalculation() {
        const predictions = ['12', '34', '56'];
        const actual = ['12', '78', '56'];
        
        const matches = predictions.filter(num => actual.includes(num));
        const accuracy = (matches.length / predictions.length) * 100;
        
        console.log('🧪 Test accuracy:', accuracy + '%');
        console.log('🧪 Matches:', matches);
        
        return accuracy;
    }
    
    // Run test
    const testAccuracy = testAccuracyCalculation();
    console.log('🎯 Test completed with accuracy:', testAccuracy + '%');
});
</script>
{% endblock %}"""

    with open(
        "c:\\Users\\n2t\\Documents\\xoso_crawler\\predictions_tracker\\templates\\predictions_tracker\\test_template.html",
        "w",
        encoding="utf-8",
    ) as f:
        f.write(content)

    print("✅ Test template created: test_template.html")
    print("🔗 Access via: /pre-lokhung/test/")


if __name__ == "__main__":
    create_test_template()
