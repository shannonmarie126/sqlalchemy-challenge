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

# Create our session (link) from Python to the DB
# session=Session(engine)

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
        "/api/v1.0/<start>"
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
    precip_data_list = [{'date': date, 'prcp': prcp}
                         for date, prcp in precip_data.items()]
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

# @app.route("/api/v1.0/<start>")
# def date():
#     session=Session(engine)
#     results=
#     session.close()
#     return 



if __name__ == '__main__':
    app.run(debug=True)