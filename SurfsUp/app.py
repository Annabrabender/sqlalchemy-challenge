# Import the dependencies.
import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify



#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station 

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)



#################################################
# Flask Routes
#################################################
@app.route("/")
def welcome():
    return(
      f"Available Routes:<br/>" 
      f"/api/v1.0/precipitation <br/>"
      f"/api/v1.0/stations <br/>"
      f"/api/v1.0/tobs <br/> "
      f"/api/v1.0/start <br/> "
      f"/api/v1.0/start/end <br/> "
    )

@app.route("/api/v1.0/precipitation")
#Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data) to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
def precipitation():
     m_prcp = session.query(Measurement.date, Measurement.prcp).\
            filter(Measurement.date is not None, Measurement.date > '2016-08-23').\
            order_by(Measurement.date).all()
     pr_dict = {date: prcp for date, prcp in m_prcp if prcp is not None}
     return jsonify(pr_dict)


@app.route("/api/v1.0/stations")
#Return a JSON list of stations from the dataset.
def stations():
    results = session.query(Station.station).all()
    # Extract the station names from the result
    station_list = [result[0] for result in results]  
    station_dict = {"stations": station_list}
    return jsonify(station_dict)


@app.route("/api/v1.0/tobs")
#Query the dates and temperature observations of the most-active station for the previous year of data.
#Return a JSON list of temperature observations for the previous year.
def tobs():
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
            filter(Measurement.station == 'USC00519281' ).\
            filter(Measurement.date >= '2017,8,23').all()
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in tobs_data]

    return jsonify(tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def temps(start, end=None):
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    if end:
        results = session.query(*sel).filter(Measurement.date >= start, Measurement.date <= end).all()
    else:
        results = session.query(*sel).filter(Measurement.date >= start).all()

    # Check if results is empty
    if not results:
        return jsonify({"error": "No data found for the given date range."})

    # Extract the result values
    min_temp, avg_temp, max_temp = results[0]

    temp_stats = {
        "TMIN": min_temp,
        "TAVG": avg_temp,
        "TMAX": max_temp
    }

    return jsonify(temp_stats)

if __name__ == '__main__':
    app.run(debug=True)
