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
Stations=Base.classes.station
Measurements=Base.classes.measurement

#################################################
# Flask Setup
#################################################

app=Flask(__name__)

#################################################
# Flask Routes
#################################################

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
@app.route("/api/v1.0/precipitation")
def precipitation():
    session=Session(engine)
    latest_date=session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_prior = latest_date_obj - dt.timedelta(days=365)
    results=session.query(Measurements.date,Measurements.prcp).\
    filter(func.strftime(Measurements.date>=one_year_prior)).\
    order_by(Measurements.date).all()
    session.close()
   
    precip_data = {}
    for date, prcp in results:
        if date not in precip_data:
            precip_data[date] = []
        precip_data[date].append(prcp)

# Convert the dictionary to a list of dictionaries for JSON response
    precip_data_list=[]
    for date, prcp in precip_data.items():
        precip_data_list.append({'date': date, 'prcp': prcp})
    return jsonify(precip_data_list)


@app.route("/api/v1.0/stations")
def stations():
    session=Session(engine)
    results=session.query(Stations.station).all()
    session.close()
    stations_list=list(np.ravel(results))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def temperatures():
    session=Session(engine)
    latest_date=session.query(Measurements.date).order_by(Measurements.date.desc()).first()[0]
    latest_date_obj = dt.datetime.strptime(latest_date, '%Y-%m-%d').date()
    one_year_prior = latest_date_obj - dt.timedelta(days=365)
    results=session.query(Measurements.date,Measurements.tobs).\
    filter((Measurements.station=='USC00519281')).\
    filter(func.strftime(Measurements.date>=one_year_prior)).all()
    session.close()
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
    session=Session(engine)
    start_date=dt.datetime.strptime(start,'%Y-%m-%d')
    sel=[func.min(Measurements.tobs),
        func.avg(Measurements.tobs),
        func.max(Measurements.tobs)]
    if end:
        start_range_date=start_date
        end_range_date=dt.datetime.strptime(end,'%Y-%m-%d')
        results=session.query(*sel).filter(Measurements.date>=start_range_date).\
        filter(Measurements.date<=end_range_date).all()
    else:
        results=session.query(*sel).filter(Measurements.date>=start_date).all()
    session.close()
    
    if results:
        temp_stats_list=[]
        for tmin,tavg,tmax in results:
            temp_stats={}
            temp_stats['tmin']=tmin
            temp_stats['tavg']=tavg
            temp_stats['tmax']=tmax
            temp_stats_list.append(temp_stats)
    
        return jsonify(temp_stats_list)
    else:
        return (f"Error, no data for date range selected")


if __name__ == '__main__':
    app.run(debug=True)