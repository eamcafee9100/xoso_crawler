# URL Configuration for Ultimate Prediction Templates
# Add these routes to your main Django URLs

from django.urls import path



# Template URLs
urlpatterns = [
    # Main prediction template
    
]

"""
📋 INTEGRATION INSTRUCTIONS:

1. Add to main urls.py:
   ```python
   from django.urls import include
   
   urlpatterns = [
       path('analytic_frequence/', include('analytic_frequence.template_urls')),
   ]
   ```

2. URLs will be available at:
   - /analytic_frequence/ultimate-prediction/ (Main prediction interface)
   - /analytic_frequence/dashboard/ (Analytics dashboard) 
   - /analytic_frequence/ajax/prediction/ (AJAX API)

3. Ensure templates directory exists:
   - analytic_frequence/templates/analytic_frequence/ultimate_prediction.html
   - analytic_frequence/templates/analytic_frequence/prediction_dashboard.html

4. For production, configure static files for CSS/JS assets
"""
