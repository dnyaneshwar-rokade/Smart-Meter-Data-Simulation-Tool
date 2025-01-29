import csv
import pandas as pd
from .models import Search_Ops
from prophet import Prophet
from django.shortcuts import render
from .models import fetch_historical_data, prediction
from django.core.paginator import Paginator
from django.http import HttpResponse
from datetime import datetime


def home(request):
    dic = {}
    if request.method == 'POST':
        try:
            start_date = request.POST.get("Start Date")
            end_date = request.POST.get("end date")
            date_tuple = (start_date, end_date)
            obj = Search_Ops()
            dic['records'] = obj.date_to_date(date_tuple)  
        except Exception as e:
            dic['error'] = f"Error: {str(e)}"
            
    return render(request, "index.html", dic)  


def show_prediction(request):
    # Fetch historical data
    historical_data = fetch_historical_data()
    
    # Get start_date and end_date from user input
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    
    # Initialize context
    context = {}

    # Validate and parse dates
    try:
        # Parse dates to ensure they are in the correct format with time
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        context['error'] = 'Invalid date format. Please enter dates in YYYY-MM-DD HH:MM:SS format.'
        return render(request, 'prediction_table.html', context)
    
    # Run prediction and pass results if data and dates are valid
    if historical_data and start_date and end_date:
        res_data = prediction(historical_data, start_date, end_date)
        
        # Verify data is being set in context
        context['prediction_data'] = res_data.to_dict(orient='records')
        context['start_date'] = start_date
        context['end_date'] = end_date
    else:
        context['error'] = 'No data available or invalid date range.'

    return render(request, 'prediction_table.html', context)



def download_csv(request):
    # Fetch historical data
    historical_data = fetch_historical_data()
    
    # Get start_date and end_date from user input in the request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Validate and parse dates
    try:
        # Parse dates to ensure they are in the correct format
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d %H:%M:%S')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        # If date parsing fails, return an error response
        response = HttpResponse("Invalid date format. Please enter dates in YYYY-MM-DD HH:MM:SS format.")
        response.status_code = 400  # Bad request
        return response

    # Generate prediction data for the specified date range
    prediction_data = prediction(historical_data, start_date, end_date)

    # Create the HttpResponse object with the appropriate CSV header
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="prediction_data.csv"'

    # Write data to CSV
    writer = csv.writer(response)
    writer.writerow(['Date', 'Predicted Reading (yhat)', 'Lower Bound (yhat_lower)', 'Upper Bound (yhat_upper)'])
    for row in prediction_data.to_dict(orient='records'):
        writer.writerow([row['ds'], row['yhat'], row['yhat_lower'], row['yhat_upper']])

    return response


