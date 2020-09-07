import json
import time
import datetime
from django.shortcuts import render
from projects.models import Project
from django.http import JsonResponse
from django.core import serializers
from influxdb_metrics.utils import query

# Create your views here.
def project_index(request):
    projects = Project.objects.all()
    context = {
        'projects': projects
    }
    return render(request, 'project_index.html', context)

def project_detail(request, pk):
    project = Project.objects.get(pk=pk)
    click = {}
    click[1] = "valve"
    click[2] = "shot"
    click[3] = "blast"
    if (click.get(pk) == "valve"): 
        infxql0 = query("select * from average_temperature where location = 'santa_monica' order by time desc limit 1")
        infxql1 = query("select * from average_temperature where location = 'coyote_creek' order by time desc limit 1")
        infxql2 = query("select * from h2o_temperature where location = 'santa_monica' order by time desc limit 1")
        infxql3 = query("select * from h2o_temperature where location = 'coyote_creek' order by time desc limit 1")
        latestt = query("select * from average_temperature order by time desc limit 1")
        datalog = list()
        for series in infxql0.get_points(measurement='average_temperature'):
            datalog.append(series['degrees'])
        for series in infxql1.get_points(measurement='average_temperature'):
            datalog.append(series['degrees'])
        for series in infxql2.get_points(measurement='h2o_temperature'):
            datalog.append(series['degrees'])
        for series in infxql3.get_points(measurement='h2o_temperature'):
            datalog.append(series['degrees'])
        for series in latestt.get_points(measurement='average_temperature'):
            #print(type(series['time']))
            datalog.append(series['time'])
        context = {
            'project' : project,
            'station' : 'valve',
            'influxql' : 'Retrieve a 2-dimensional array of [10x4] of One Reading Weight Data',
            'timestamp' : datalog[-1],
            'value1' : datalog[0],
            'value2' : datalog[1],
            'value3' : datalog[2],
            'value4' : datalog[3]
        }
        return render(request, 'project_detail.html', context)
    elif (click.get(pk) == "shot"):
        ### influxdb query ###
        infxql0 = query("select * from h2o_pH where location = 'coyote_creek' order by time desc limit 30")
        infxql1 = query("select * from h2o_temperature where location = 'santa_monica' order by time desc limit 30")
        infxtag = query("show tag values from h2o_pH with key=location")
        taglist = list()
        for series in infxtag.get_points(measurement='h2o_pH'):
            taglist.append(series['value'])
        print(taglist)
        ### create a list of lists of <time, value> ###
        graflog0 = list()
        ### for loop to iterate the influxdb query result ###
        for series in infxql0.get_points(measurement='h2o_pH'):
            entry = list()
            t = time.mktime(datetime.datetime.strptime(series['time'], "%Y-%m-%dT%H:%M:%SZ").timetuple())
            entry.append(int(t)*1000)
            entry.append(series['pH'])
            graflog0.append(entry)
        graflog1 = list()
        for series in infxql1.get_points(measurement='h2o_temperature'):
            entry = list()
            t = time.mktime(datetime.datetime.strptime(series['time'], "%Y-%m-%dT%H:%M:%SZ").timetuple())
            entry.append(int(t)*1000)
            entry.append(series['degrees'])
            graflog1.append(entry)
        ### return html page with packed data in json format ###
        context = {
            'project' : project,
            'station' : 'shot',
            'influxql' : 'Retrieve four different output/feedback data from Omron PLC',
            'loggraf1' : json.dumps(graflog0),
            'loggraf2' : json.dumps(graflog1)
        }
        return render(request, 'project_detail.html', context)
    elif (click.get(pk) == "blast"):
        return render(request, 'project_detail.html', context)



''' 
    preDict = {}
    preDict[1] = "select * from average_temperature where location = 'santa_monica' order by time desc limit 100"
    preDict[2] = "select * from h2o_pH where location = 'coyote_creek' order by time desc limit 100"
    preDict[3] = "select * from h2o_temperature where location = 'santa_monica' order by time desc limit 100"
    preMeasure = {}
    preMeasure[1] = ['average_temperature','degrees']
    preMeasure[2] = ['h2o_pH','pH']
    preMeasure[3] = ['h2o_temperature','degrees']
    #print(preDict[project.title])
    infxql = query(preDict.get(pk))
    param = preMeasure.get(pk)
    #print(preMeasure.get(project.title))
    datalog = list()
    
    for series in infxql.get_points(measurement=param[0]):
        entry = list()
        t = time.mktime(datetime.datetime.strptime(series['time'], "%Y-%m-%dT%H:%M:%SZ").timetuple())
        entry.append(int(t))
        entry.append(series[param[1]])
        #timestamp.append(series['time'])
        datalog.append(entry)

    #print(datalog[0])
    context = {
        'project': project,
        'influxql' : preDict.get(pk),
        'logdata' : json.dumps(datalog)
    }
    return render(request, 'project_detail.html', context)
'''
