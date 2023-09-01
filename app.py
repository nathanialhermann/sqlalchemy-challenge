# Import the dependencies.
from flask import Flask, jsonify, request
import pandas as pd
import datetime as dt
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, funcpython
import numpy as np
import sqlalchemy

#################################################
# Database Setup
#################################################
engine = create_engine('sqlite:///Resources/hawaii.sqlite')

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

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
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    local_session = Session(engine) 

    last_date = session.query(measurement.date).all()[-1][0]
    last_date_format = dt.date.fromisoformat(last_date)
    new_date = last_date_format - dt.timedelta(days=365)
    new_date_str = new_date.isoformat()
    date_precip = session.query(measurement.date, measurement.prcp) \
                        .filter(measurement.date >= new_date_str)

    session.close()

    precip_dictionary = {}

    for row in date_precip:
        precip_dictionary[row['date']] = row['prcp']
    
    return jsonify(precip_dictionary)

@app.route("/api/v1.0/stations")
def stations():
    local_session = Session(engine)
    stations = local_session.query(station.station, station.name).all()
    station_data = {station: name for station, name in stations}
    local_session.close()
    return jsonify(station_data)

@app.route("/api/v1.0/tobs")
def tobs():
    local_session = Session(engine)
    
    most_active = session.query(measurement.station,\
        func.count(measurement.station)).group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    
    results = session.query(measurement.date, measurement.tobs, measurement.station).\
        filter(measurement.date >= dt.date(2016, 8, 18)).\
        filter(measurement.station == most_active[0]).all()
   
    response_data = {date: tobs for date, tobs, station in results}
    
    # Jsonify the results
    local_session.close()
    return jsonify(response_data)

@app.route("/api/v1.0/temp/start", methods=['POST'])
def start():
    local_session = Session(engine)
    results = session.query(measurement.date,func.min(measurement.tobs),\
        func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).all()
             
    session.close()
    
    response_date = []
    for date, min, avg, max in results:
        info_dict = {}
        info_dict["DATE"] = date
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX"] = max
        info.append(info_dict)

    return jsonify(info)

@app.route("/api/v1.0/temp/start/end", methods=['POST'])
def start_end():
    local_session = Session(engine)
    
    results = session.query(func.min(measurement.tobs),\
        func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start).filter(measurement.date <= start_end).all()

    session.close()        
    
    info = []

    for min, avg, max in results:
        info_dict = {}
        info_dict["TMIN"] = min
        info_dict["TAVG"] = avg
        info_dict["TMAX "] = max
        info.append(info_dict)

    return jsonify(info)