from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
import numpy as np

app = Flask(__name__)

engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect=True)

Measurement = Base.classes.measurement
Station = Base.classes.station

#Calculate the query dates
session = Session(engine)

last_date = session.query(Measurement.date).\
            order_by(Measurement.date.desc()).\
            first()
last_date = dt.datetime.strptime((*last_date), '%Y-%m-%d')
first_date = last_date - dt.timedelta(days=365)

session.close()

@app.route("/")
def home():
    print("Server received request for 'Home' page.")
    return (
        
        "Thank you for contacting the homework assignment of Tyler Ward.<br/>"
        "You have the following options for navigation:<br/>"
        "/api/v1.0/precipitation<br/>"
        "/api/v1.0/stations<br/>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/start/end"

    )


# Convert the query results to a dictionary using `date` as the key and `prcp` as the value.
# Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():

    #Create session link
    session = Session(engine)

    #Perform a query to retrieve the data and precipitation scores
    sel = [Measurement.date, Measurement.prcp]
    yr_prcp_data = session.query(*sel).filter(Measurement.date >= first_date).\
        order_by('date').all()

    #Close the session
    session.close()

    all_prcp_data = []
    for date, prcp in yr_prcp_data:
        prcp_dict = {}
        prcp_dict[date] = prcp
        all_prcp_data.append(prcp_dict)

    return jsonify(all_prcp_data)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():

    #Create session link
    session = Session(engine)

    #Perform a query to retrieve all of the stations
    act_station = session.query(Measurement.station).distinct().all()

    #Close the session
    session.close()

    #Convert list of tuples into a normal list

    all_stations = list(np.ravel(act_station))

    return jsonify(all_stations)

# Query the dates and temperature observations of the most active station for the last year of data.
# Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")

def temp():

    #Create session link
    session = Session(engine)

    #Perform a query to find the most active station

    most_act_station = session.query(Measurement.station,\
            func.count(Measurement.station)).group_by(Measurement.station).\
            order_by(func.count(Measurement.station).desc()).all()

    #pull the first station in the sequence of stations ordered in descending activity
    most_act = most_act_station[0][0]
    
    tobs_most_act = session.query(Measurement.tobs).\
            filter(Measurement.station == most_act).\
            filter(Measurement.date >= first_date).all()

    #Close the session
    session.close()

    all_temps = list(np.ravel(tobs_most_act))   
    return jsonify(all_temps)

# Return a JSON list of the minimum temperature, the average temperature, 
#       and the max temperature for a given start or start-end range.
# When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all 
#       dates greater than and equal to the start date.
# When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for 
#       dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def stats(start=None, end=None):

    #Create session link
    session = Session(engine)

    #Specivy required functions
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs),func.max(Measurement.tobs)]

    #Specify what to do if there is no end function
    if not end:
        start_only = session.query(*sel).filter(Measurement.date >= start).all()

        start_temps = list(np.ravel(start_only))

        return jsonify(start_temps)
    
    #Specify protocol if both start and end are present
    start_end = session.query(*sel).filter(Measurement.date.between(start, end)).all()

    start_end_temps = list(np.ravel(start_end))
    return jsonify(start_end_temps)

    #Close the session
    session.close()

#Run the app
if __name__ == "__main__":
    app.run(debug=True)