import pandas as pd
from prophet import Prophet
import mysql.connector

class Search_Ops:
    def date_to_date(self, date_tuple):
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='230399',
            database='csvdb'
        )
        curs = con.cursor()

        query = "SELECT * FROM meter_readings WHERE date_time BETWEEN %s AND %s"
        curs.execute(query, date_tuple)

        data = curs.fetchall()
        print("Database response:", data)

        # Convert the data to a list of dictionaries
        records = []
        for row in data:
            record = {
                'date_time': row[0],
                'reading': row[1],
                'value': row[2],
                'meter_condition': row[3]
            }
            records.append(record)

        con.close()
        return records  # Return the list of records
    
def fetch_historical_data():
    try:
        con = mysql.connector.connect(
            host='localhost',
            user='root',
            password='230399',
            database='csvdb'
        )
        curs = con.cursor()
        curs.execute("SELECT date_time, reading FROM meter_readings")
        data = curs.fetchall()
        con.close()
        
        print("Fetched Data:", data)  # Debugging: check if data is fetched
        return data
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return []

def prediction(data, start_date, end_date):
    # Create a DataFrame from the fetched data
    df = pd.DataFrame(data, columns=['date_time', 'reading'])
    print("Initial DataFrame:", df.head())  # Debugging

    # Rename columns to match Prophet's requirements
    df.rename(columns={'date_time': 'ds', 'reading': 'y'}, inplace=True)

    # Convert 'ds' to datetime
    df['ds'] = pd.to_datetime(df['ds'])
    print("DataFrame after renaming and converting dates:", df.head())  # Debugging

    # Optionally, filter out any rows with NaN values in 'y'
    df = df[['ds', 'y']].dropna()

    # Initialize the model
    model = Prophet()

    # Fit the model
    model.fit(df)

    # Create a DataFrame for future dates based on user input
    future_dates = pd.date_range(start=start_date, end=end_date, freq='h')
    future = pd.DataFrame(future_dates, columns=['ds'])
    print("Future dates DataFrame:", future.head())  # Debugging

    # Make predictions
    forecast = model.predict(future)
    print("Forecast DataFrame:", forecast.head())  # Debugging

    # Display the forecast data for the selected date range
    date_range_forecast = forecast[(forecast['ds'] >= str(start_date)) & (forecast['ds'] <= str(end_date))]
    result = date_range_forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    print("Filtered forecast result:", result.head())  # Debugging

    return result
