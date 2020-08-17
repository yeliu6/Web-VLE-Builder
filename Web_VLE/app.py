from flask import Flask, request, session, render_template, url_for
from compound import Compound
from data_scrape import antoineParameters, boilPoint, AntoineError, BoilPointError
import numpy as np
from plotting import plottingIsoBar, plottingIsoTherm

app = Flask(__name__)
app.config["SECRET_KEY"] = "my_key_3" # TODO: set key
# TODO: Encryption, https

@app.route("/", methods=["GET", "POST"])
@app.route("/index", methods=["GET", "POST"])
@app.route("/result", methods=["GET", "POST"])

def index():
    if "inputs" not in session:
        session["inputs"] = []

    errors = ""
    if request.method == "POST":
        try:
            if str(request.form.get('UseComp2')) == 'on': # swaps order
                session["inputs"].append(request.form["Compound 2"])
                session["inputs"].append(request.form["Compound 1"])
            else:
                session["inputs"].append(request.form["Compound 1"])
                session["inputs"].append(request.form["Compound 2"])
            session.modified = True
        except:
            errors = "error"

        # if len(session["inputs"]) == 0:
        #     errors = "no inputs"

        if request.form["action"] == "Calculate":
            result = []
            compObjList = []
            compList = []
            xVals = np.linspace(0, 1, int(request.form.get('Specificity'))+1)
            if str(request.form.get('Ideal')) == 'on':  # ideal calculations
                pressure_units = request.form["PUnits"]
                temp_units = request.form["TUnits"]
                temp = float(request.form["Temperature"])
                pressure = float(request.form["Pressure"])

                # convert given P/T to bar/K
                if pressure_units == 'atm':
                    pressure = float(request.form["Pressure"]) / 1.01325
                elif pressure_units == 'kPa':
                    pressure = float(request.form["Pressure"]) * 100
                elif pressure_units == 'Pa':
                    pressure = float(request.form["Pressure"]) * 100000
                elif pressure_units == 'mmHg':
                    pressure = float(request.form["Pressure"]) / 1.01325 * 760
                #else it's bar

                if temp_units == '\u00b0F':
                    temp = (float(request.form["Temperature"]) - 273.15) * 9 / 5 + 32
                elif temp_units == '\u00b0C':
                    temp = float(request.form["Temperature"]) - 273.15
                #else it's K

                for compound in session["inputs"]:
                    compList.append(compound)
                    boilP = boilPoint(compound)
                    result.append(compound + " Boil : " + boilP + " K")
                    if str(request.form.get('IgnoreAnt')) == 'on':
                        antData = antoineParameters(compound)[0]
                        result.append(compound + " Antoine : " + str(antData)) # getting first set of data

                        comp = Compound(compound, antData[0], float(antData[1]), float(antData[2]), float(antData[3]), boilP)
                        compObjList.append(comp)
                    else:
                        # parses through to working temperature range
                        antList = antoineParameters(compound)
                        result.append(compound + "All Antoine : " + str(antList))
                        useSet = []  # initialize

                        for i in range(0, len(antList)):
                            useSet = antList[i]
                            tRange = useSet[0]
                            tLow = tRange.split(" - ")[0]
                            tHigh = tRange.split(" - ")[1]
                            if float(tLow) <= temp and float(tHigh) >= temp:
                                break  # breaks loop if temp within range
                            else:
                                if i == len(antList) - 1:  # happens when currently on last listed antoine set
                                    useSet = []
                        if useSet != []:  # if empty, means temperature is out of antoine range ### double error message here
                            aVal = float(useSet[1])  # if error occurs here, temp out of range likely
                            bVal = float(useSet[2])
                            cVal = float(useSet[3])
                            comp = Compound(compound, tRange, aVal, bVal, cVal, boilP)
                            compObjList.append(comp)
                        else:
                            #error msg
                            pass

                    result.append(comp.description()) #object creation is working

                result.append("Pressure : " + request.form["Pressure"] + " " + request.form["PUnits"])
                result.append("Temperature : " + request.form["Temperature"] + " " + request.form["TUnits"])
                result.append("Spec : " + request.form["Specificity"])

                if str(request.form.get('IsoCalc')) == 'IsoThermal':
                    bub = compObjList[0].bubbleIsoTherm(xVals, compObjList, temp)
                    dew = compObjList[0].dewIsoTherm(xVals, compObjList, temp)

                    if pressure_units != 'bar':
                        tempB = []
                        tempD = []
                        for i in range(0, len(bub[0])):
                            if pressure_units == 'atm':
                                tempB.append(bub[1][i] / 1.01325)
                            elif pressure_units == 'mmHg':
                                tempB.append(bub[1][i] / 1.01325 * 760)
                            elif pressure_units == 'Pa':
                                tempB.append(bub[1][i] * 100000)
                            elif pressure_units == 'kPa':
                                tempB.append(bub[1][i] * 100)

                        for i in range(0, len(dew[0])):
                            if pressure_units == 'atm':
                                tempD.append(dew[1][i] / 1.01325)
                            elif pressure_units == 'mmHg':
                                tempD.append(dew[1][i] / 1.01325 * 760)
                            elif pressure_units == 'Pa':
                                tempD.append(dew[1][i] * 100000)
                            elif pressure_units == 'kPa':
                                tempD.append(dew[1][i] * 100)
                        bub = [bub[0], tempB]
                        dew = [dew[0], tempD]

                    result.append("bub : " + str(bub))
                    result.append("dew : " + str(dew))
                    result.append("test : " + str(tuple(zip(bub[0], bub[1]))))

                    bubUse = tuple(zip(bub[0], bub[1]))
                    dewUse = tuple(zip(dew[0], dew[1]))
                    data = [list(a) for a in zip(bub[0], bub[1], dew[1])]
                    for i in data:
                        for j in range(0, len(i)):
                            i[j] = '%.3f' % (i[j])

                    chart_data = plottingIsoTherm(xVals, bubUse, dewUse, compList, pressure_units)
                elif str(request.form.get('IsoCalc')) == 'IsoBaric':
                    if str(request.form.get('Ideal')) == 'on':
                        bub = compObjList[0].bubbleIsoBar(xVals, compObjList, temp, pressure)
                        dew = compObjList[0].dewIsoBar(xVals, compObjList, temp, pressure)

                        if temp_units != 'K':
                            tempB = []
                            tempD = []
                            for i in range(0, len(bub[0])):
                                if temp_units == '\u00b0C':
                                    tempB.append(bub[1][i] - 273.15)
                                elif temp_units == '\u00b0F':
                                    tempB.append((bub[1][i] - 273.15)*9/5 + 32)

                            for i in range(0, len(dew[0])):
                                if temp_units == '\u00b0C':
                                    tempD.append(dew[1][i] - 273.15)
                                elif temp_units == '\u00b0F':
                                    tempD.append((dew[1][i] - 273.15) * 9 / 5 + 32)
                            bub = [bub[0], tempB]
                            dew = [dew[0], tempD]

                        result.append("bub : " + str(bub))
                        result.append("dew : " + str(dew))

                        bubUse = tuple(zip(bub[0], bub[1]))
                        dewUse = tuple(zip(dew[0], dew[1]))

                        data = [list(a) for a in zip(bub[0], bub[1], dew[1])]
                        for i in data:
                            for j in range(0, len(i)):
                                i[j] = '%.3f' % (i[j])

                        chart_data = plottingIsoBar(xVals, bubUse, dewUse, compList, temp_units)
                    else:
                        pass

                result.append("ideal : " + str(request.form.get('Ideal'))) # typecast to str in case it's NoneType
                result.append("Ant : " + str(request.form.get('IgnoreAnt')))
                result.append("Comp : " + str(request.form.get('UseComp2')))
                result.append("Iso : " + str(request.form.get('IsoCalc')))

                session["inputs"].clear()
                session.modified = True

                result = "" # clears result so no debug print, temp fix

                return render_template('results.html', title='Results', result=result, chart=chart_data, data=data)
            else:
                pass # non-ideal case

    return render_template('inputs.html', title='Inputs', errors=errors)

if __name__ == '__main__':
    app.run()