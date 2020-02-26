import numpy as np
import pandas as pd
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify



engine = create_engine("sqlite:///hawaii.sqlite", connect_args={'check_same_thread': False})


Base = automap_base()
Base.prepare(engine, reflect=True)
Base.classes.keys()
Measurement = Base.classes.measurement
Station = Base.classes.station



session = Session(engine)



#weather app

app = Flask(__name__)


# Hay que encontrar la fecha mas actualizada y de ahi nos vamos un  año para atrás
fecha1=session.query(Measurement.date).order_by(Measurement.date.desc()).first()

#Asignamos un año atras a last year
lastyear = dt.date(2017, 8, 23) - dt.timedelta(days=365)


@app.route("/")

def home():

    return (f"Bienvenidos a Hawai  Surf's Up! Climate API<br/>"
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitaton                                --> Toda la base fecha y prcp <br/>"
            f"/api/v1.0/stations                                    --> Lista de Estaciones <br/>"
            f"/api/v1.0/tobs                                        --> Base con fecha y prcp del último año <br/>"
            f"/api/v1.0/datesearch/2010-07-26                       --> baja, alta, y promedio de temp desde la fecha dada <br/>"
            f"/api/v1.0/datesearch/2014-07-26/2017-07-26            --> baja, alta, y promedio de temp de la fecha inicial a la fecha final <br/>")


@app.route("/api/v1.0/precipitaton")
def precipitation():
    prcp_base= session.query(Measurement.date, Measurement.prcp).all()
    return jsonify(prcp_base)

@app.route("/api/v1.0/stations")
def stations():
    estacion = session.query(Station.name).all()
    todas = list(np.ravel(estacion))
    return jsonify(todas)

@app.route("/api/v1.0/tobs")
def tobs():
    prcp_base= session.query(Measurement.date, Measurement.prcp).filter(Measurement.date > lastyear).order_by(Measurement.date).all()
    return jsonify(prcp_base)


@app.route('/api/v1.0/datesearch/<start>')


def start(start):

    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).group_by(Measurement.date).all())
    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Fecha"] = result[0]
        date_dict["Baja Temp"] = result[1]
        date_dict["Promedio Temp"] = result[2]
        date_dict["Alta Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)

@app.route('/api/v1.0/datesearch/<start>/<end>')
def startEnd(start, end):
    sel = [Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]

    results =  (session.query(*sel).filter(func.strftime("%Y-%m-%d", Measurement.date) >= start).filter(func.strftime("%Y-%m-%d", Measurement.date) <= end)
                       .group_by(Measurement.date)
                       .all())

    dates = []                       
    for result in results:
        date_dict = {}
        date_dict["Fecha"] = result[0]
        date_dict["Baja Temp"] = result[1]
        date_dict["Promedio Temp"] = result[2]
        date_dict["Alta Temp"] = result[3]
        dates.append(date_dict)

    return jsonify(dates)



if __name__ == "__main__":

    app.run(debug=True)