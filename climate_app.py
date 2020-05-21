import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify
import datetime as dt
from datetime import datetime

engine = create_engine("sqlite:///Resources/hawaii.sqlite")
Base = automap_base()
Base.prepare(engine, reflect=True)

# Save reference to the tables
Measurement = Base.classes.measurement
Station = Base.classes.station

app = Flask(__name__)

#  Home - List all routes that are available.
@app.route("/")
def home():
    print("Take me 'Home' JSON road...")
    return (
        f"Welcome to the Hawaii Vacation Precipitation Home Page!<br/><br/>"
        f"Available Routes:<br/><br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/><br/>"
        f"Replace 'yyyy-mm-dd' with year, month, and day information<br/>"
        f"/api/v1.0/yyyy-mm-dd/<br/>"
        f"/api/v1.0/yyyy-mm-dd/yyyy-mm-dd<br/>"
    )

# since both the precipitation and tobs routs need the last year of data I've moved the variables outside of the functions so they can be used in both.
session = Session(engine)    
# station with the highest number of observations (from part 1) with cool adjustment
Bigguy = session.query(Measurement.station, func.count(Measurement.station)).group_by(Measurement.station)\
        .order_by(func.count(Measurement.station).desc()).all()[0][0]
# The last day of the report (also from part 1)
l_day = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
# the day 1 year prior to the last day
f_day = datetime.strptime(l_day, '%Y-%m-%d') - dt.timedelta(days=365)
f_day = f_day.strftime('%Y-%m-%d')
session.close()

# Convert the query results to a dictionary using `date` as the key and `prcp` as the value
@app.route("/api/v1.0/precipitation")
def precipitation():
    print(f"Rain, Rain Go Away...{f_day} to {l_day}")

    # Query all dates and precipitation values
    session = Session(engine)
    results = session.query(Measurement.date,Measurement.prcp)\
        .filter(Measurement.date.between(f_day, l_day)).all()
    session.close()
    
    p_dict = dict(results)
    return jsonify(p_dict)  

# Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def station():
    print("STATION!") #Excellent!

    # Query all stations
    session = Session(engine)
    sresults = session.query(Station.station).all()
    session.close()
    
    # ravel
    all_stations = list(np.ravel(sresults))
    return jsonify(all_stations)  

# Query the dates and temperature observations of the most active station for the last year of data
@app.route("/api/v1.0/tobs")
def tobs():
    print(f"{Bigguy} temperatures for the last year")
    
    session = Session(engine)
    # the data for the station with the most measurments for one year from the last day of reporting
    year_temps = session.query(Measurement.date,Measurement.prcp)\
        .filter(Measurement.date.between(f_day, l_day))\
        .filter(Measurement.station==Bigguy).all()    
    session.close()

    return jsonify(year_temps)  

# Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # for dates after the start date
@app.route("/api/v1.0/<start_date>/")
def from_start_date(start_date):
    print("Min, Avg, and Max Temperature from given date to end date of reporting")
    session = Session(engine)

    # from the function in the jupyter notebook
    MinAvgMax = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).all()
    session.close()
    return jsonify(MinAvgMax) 

    # for dates between the start and end date inclusive
@app.route("/api/v1.0/<start_date>/<end_date>")
def from_start_to_end_date(start_date, end_date):
    print("Min, Avg, and Max Temperature for given date range")
    session = Session(engine)

    # from the function in the jupyter notebook
    MinAvgMax = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()

    session.close()

    return jsonify(MinAvgMax) 

if __name__ == "__main__":
    app.run(debug=True)
    