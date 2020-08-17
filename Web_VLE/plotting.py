import pygal

def plottingIsoBar(xVals, tempListBub, tempListDew, compList, temp_units):

    strTitle = "Isobaric VLE Diagram for Mixture:\n{} and {}".format(compList[0], compList[1], fontsize=18,
                                                                       fontname='Times New Roman')
    strY = "Temperature ({})".format(temp_units, fontsize=16, fontname='Times New Roman')
    strX = "Mole Fraction of Component 1: {}".format(compList[0], fontsize=16, fontname='Times New Roman')

    chart = pygal.XY(width=800, height=800, explicit_size=True)
    chart.title = strTitle
    chart.x_title = strX
    chart.y_title = strY
    chart.legend_at_bottom = True
    chart.x_labels = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)
    chart.add('Bubble Point Curve', tempListBub)
    chart.add('Dew Point Curve', tempListDew)

    chart_data = chart.render_data_uri()

    return chart_data


def plottingIsoTherm(xVals, presListBub, presListDew, compList, pressure_units):

    strTitle = "Isothermal VLE Diagram for Mixture:\n{} and {}".format(compList[0], compList[1], fontsize=18,
                fontname='Times New Roman')
    strY = "Pressure ({})".format(pressure_units, fontsize=16, fontname='Times New Roman')
    strX = "Mole Fraction of Component 1: {}".format(compList[0], fontsize=16, fontname='Times New Roman')

    chart = pygal.XY(width=800, height=800, explicit_size=True)
    chart.title = strTitle
    chart.x_title = strX
    chart.y_title = strY
    chart.legend_at_bottom = True
    chart.add('Bubble Point Curve', presListBub)
    chart.add('Dew Point Curve', presListDew)
    chart.x_labels = (0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0)

    chart_data = chart.render_data_uri()

    return chart_data