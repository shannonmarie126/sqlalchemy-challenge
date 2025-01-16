# Import the dependencies.
import numpy as np 

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
stations=Base.classes.station
measurements=Base.classes.measurement

#################################################
# Flask Setup
#################################################

app=Flask(__name__)

#################################################
# Flask Routes
#################################################

# home page route with all routes listed and explanation of datetime formatting
@app.route("/")
def home_page():
    """List all available api routes."""
    return (
        "Welcome to the Hawaii Weather API!<br/>"
        "Available routes:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br/>"
        "/api/v1.0/<start>start_date: insert date in YYYY-mm-dd<br/>"
        "/api/v1.0/<start>start_date: insert date in YYYY-mm-dd/<end>end_date: insert date in YYYY-mm-dd"
    )

#
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return precipitation data for the last year of data"""
    session=Session(engine)
    #query the latest date and calculate date for one year prior to that
    latest_date=session.query(measurements.date).order_by(measurements.date.desc()).first()[0]
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_prior = latest_date_obj - dt.timedelta(days=365)
    #query the year of data including the date for a key
    results=session.query(measurements.date,measurements.prcp).\
    filter(func.strftime(measurements.date>=one_year_prior)).\
    order_by(measurements.date).all()
    session.close()
   #create the date key 
    precip_data = {}
    for date, prcp in results:
        if date not in precip_data:
            precip_data[date] = []
        precip_data[date].append(prcp)

# Add the precipitations for each date and convert to JSON for the return
    precip_data_list=[]
    for date, prcp in precip_data.items():
        precip_data_list.append({'date': date, 'prcp': prcp})
    return jsonify(precip_data_list)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of all the stations"""
    session=Session(engine)
    #query all station IDs
    results=session.query(stations.station).all()
    session.close()
    #change results to a list then jsonify
    stations_list=list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperatures():
    """Return temperature observations for the last year from the most active station"""
    session=Session(engine)
    latest_date=session.query(measurements.date).order_by(measurements.date.desc()).first()[0]
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_prior = latest_date_obj - dt.timedelta(days=365)
    #query temp for most active station for date range 
    results=session.query(measurements.date,measurements.tobs).\
    filter((measurements.station=='USC00519281')).\
    filter(func.strftime(measurements.date>=one_year_prior)).all()
    session.close()
    #create a list of dictionaries to hold date and temp and return jsonified result
    temp_last_year=[]
    for date,temp in results:
        temp_dict={}
        temp_dict['date']=date
        temp_dict['temp']=temp
        temp_last_year.append(temp_dict)
    return jsonify(temp_last_year)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def date_range(start,end=None):
    """Return min, avg, max for a specified date range"""
    session=Session(engine)
    start_date=dt.datetime.strptime(start,'%Y-%m-%d')
    #define selection criteria
    sel=[func.min(measurements.tobs),
        func.avg(measurements.tobs),
        func.max(measurements.tobs)]
    #check for end date being provided and if so then use for the query
    if end:
        start_range_date=start_date
        end_range_date=dt.datetime.strptime(end,'%Y-%m-%d')
        results=session.query(*sel).filter(measurements.date>=start_range_date).\
        filter(measurements.date<=end_range_date).all()
    #query for start date to last day in data set 
    else:
        results=session.query(*sel).filter(measurements.date>=start_date).all()
    session.close()
    
    #return temp stats as a dictionary and jsonify it in the return
    if results:
        temp_stats_list=[]
        for tmin,tavg,tmax in results:
            temp_stats={}
            temp_stats['tmin']=tmin
            temp_stats['tavg']=tavg
            temp_stats['tmax']=tmax
            temp_stats_list.append(temp_stats)
    
        return jsonify(temp_stats_list)
    #error message for dates not in the data set 
    else:
        return (f"Error, no data for date range selected")


if __name__ == '__main__':
    app.run(debug=True)