# Flask : library utama untuk membuat API
# render_template : agar dapat memberikan respon file html
# request : untuk membaca data yang diterima saat request datang
from flask import Flask, render_template, request
# plotly dan plotly.graph_objs : membuat plot
import plotly
import plotly.graph_objs as go
# pandas : untuk membaca csv dan men-generate dataframe
import pandas as pd
import json
from sqlalchemy import create_engine

## Joblib untuk Load Model
import joblib

# untuk membuat route
app = Flask(__name__)

###################
## CATEGORY PLOT ##
###################

## IMPORT DATA USING pd.read_csv
df = pd.read_csv('JCDS Cahyo/Dashboard/dashboard_cpu/static/data_clean.csv')

# IMPORT DATA USING pd.read_sql
# sqlengine = create_engine('mysql+pymysql://kal:s3cret123@127.0.0.1/flaskapp', pool_recycle=3605)
# dbConnection = sqlengine.connect()
# engine = sqlengine.raw_connection()
# cursor = engine.cursor()
# tips = pd.read_sql("select * from tips", dbConnection)

# category plot function
def category_plot(
    cat_plot = 'histplot',
    cat_x = 'Gender', cat_y = 'MaritalStatus',
    estimator = 'count', hue = 'JobSatisfaction'):

    # generate dataframe tips.csv
    # tips = pd.read_csv('./static/tips.csv')

    # jika menu yang dipilih adalah histogram
    if cat_plot == 'histplot':
        # siapkan list kosong untuk menampung konfigurasi hist
        data = []
        # generate config histogram dengan mengatur sumbu x dan sumbu y
        for val in df[hue].unique():
            hist = go.Histogram(
                x=df[df[hue]==val][cat_x],
                y=df[df[hue]==val][cat_y],
                histfunc=estimator,
                name=val
            )
            #masukkan ke dalam array
            data.append(hist)
        #tentukan title dari plot yang akan ditampilkan
        title='Histogram'

    elif cat_plot == 'boxplot':
        data = []

        for val in df[hue].unique():
            box = go.Box(
                x=df[df[hue] == val][cat_x], #series
                y=df[df[hue] == val][cat_y],
                name = val
            )
            data.append(box)
        title='Box'

    # menyiapkan config layout tempat plot akan ditampilkan
    # menentukan nama sumbu x dan sumbu y
    if cat_plot == 'histplot':
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title='person'),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    else:
        layout = go.Layout(
            title=title,
            xaxis=dict(title=cat_x),
            yaxis=dict(title=cat_y),
            # boxmode group digunakan berfungsi untuk mengelompokkan box berdasarkan hue
            boxmode = 'group'
        )
    #simpan config plot dan layout pada dictionary
    result = {'data': data, 'layout': layout}

    #json.dumps akan mengenerate plot dan menyimpan hasilnya pada graphjson
    graphJSON = json.dumps(result, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

# akses halaman menuju route '/' untuk men-test
# apakah API sudah running atau belum
@app.route('/')
def index():

    plot = category_plot()
    # dropdown menu
    # kita lihat pada halaman dashboard terdapat menu dropdown
    # terdapat lima menu dropdown, sehingga kita mengirimkan kelima variable di bawah ini
    # kita mengirimnya dalam bentuk list agar mudah mengolahnya di halaman html menggunakan looping
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('Gender', 'Gender'), ('MaritalStatus', 'MaritalStatus'), ('BusinessTravel', 'BusinessTravel'), ('WorkingHours', 'WorkingHours')]
    list_y = [('EnvironmentSatisfaction', 'EnvironmentSatisfaction'), ('JobSatisfaction', 'JobSatisfaction')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('Gender', 'Gender'), ('MaritalStatus', 'MaritalStatus'), ('BusinessTravel', 'BusinessTravel'), ('WorkingHours', 'WorkingHours')]

    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot='histplot',
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x='Gender',

        # untuk sumbu Y tidak ada, nantinya menu dropdown Y akan di disable
        # karena pada histogram, sumbu Y akan menunjukkan kuantitas data

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator='count',
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue='MaritalStatus',
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue)

# ada dua kondisi di mana kita akan melakukan request terhadap route ini
# pertama saat klik menu tab (Histogram & Box)
# kedua saat mengirim form (saat merubah salah satu dropdown) 
@app.route('/cat_fn/<nav>')
def cat_fn(nav):

    # saat klik menu navigasi
    if nav == 'True':
        cat_plot = 'histplot'
        cat_x = 'Gender'
        cat_y = 'JobSatisfaction'
        estimator = 'count'
        hue = 'MaritalStatus'
    
    # saat memilih value dari form
    else:
        cat_plot = request.args.get('cat_plot')
        cat_x = request.args.get('cat_x')
        cat_y = request.args.get('cat_y')
        estimator = request.args.get('estimator')
        hue = request.args.get('hue')

    # Dari boxplot ke histogram akan None
    if estimator == None:
        estimator = 'count'
    
    # Saat estimator == 'count', dropdown menu sumbu Y menjadi disabled dan memberikan nilai None
    if cat_y == None:
        cat_y = 'JobSatisfaction'

    # Dropdown menu
    list_plot = [('histplot', 'Histogram'), ('boxplot', 'Box')]
    list_x = [('Gender', 'Gender'), ('MaritalStatus', 'MaritalStatus'), ('BusinessTravel', 'BusinessTravel'), ('WorkingHours', 'WorkingHours')]
    list_y = [('EnvironmentSatisfaction', 'EnvironmentSatisfaction'), ('JobSatisfaction', 'JobSatisfaction')]
    list_est = [('count', 'Count'), ('avg', 'Average'), ('max', 'Max'), ('min', 'Min')]
    list_hue = [('Gender', 'Gender'), ('MaritalStatus', 'MaritalStatus'), ('BusinessTravel', 'BusinessTravel'), ('WorkingHours', 'WorkingHours')]

    plot = category_plot(cat_plot, cat_x, cat_y, estimator, hue)
    return render_template(
        # file yang akan menjadi response dari API
        'category.html',
        # plot yang akan ditampilkan
        plot=plot,
        # menu yang akan tampil di dropdown 'Jenis Plot'
        focus_plot=cat_plot,
        # menu yang akan muncul di dropdown 'sumbu X'
        focus_x=cat_x,
        focus_y=cat_y,

        # menu yang akan muncul di dropdown 'Estimator'
        focus_estimator=estimator,
        # menu yang akan tampil di dropdown 'Hue'
        focus_hue=hue,
        # list yang akan digunakan looping untuk membuat dropdown 'Jenis Plot'
        drop_plot= list_plot,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu X'
        drop_x= list_x,
        # list yang akan digunakan looping untuk membuat dropdown 'Sumbu Y'
        drop_y= list_y,
        # list yang akan digunakan looping untuk membuat dropdown 'Estimator'
        drop_estimator= list_est,
        # list yang akan digunakan looping untuk membuat dropdown 'Hue'
        drop_hue= list_hue
    )

##############
## PIE PLOT ##
##############

def pie_plot(hue = 'Gender'):
    


    vcounts = df[hue].value_counts()

    labels = []
    values = []

    for item in vcounts.iteritems():
        labels.append(item[0])
        values.append(item[1])
    
    data = [
        go.Pie(
            labels=labels,
            values=values
        )
    ]

    layout = go.Layout(title='Pie', title_x= 0.48)

    result = {'data': data, 'layout': layout}

    graphJSON = json.dumps(result,cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON

@app.route('/pie_fn')
def pie_fn():
    hue = request.args.get('hue')

    if hue == None:
        hue = 'Gender'

    list_hue = [('Gender', 'Gender'), ('MaritalStatus', 'MaritalStatus'), ('BusinessTravel', 'BusinessTravel'), ('JobSatisfaction', 'JobSatisfaction'), ('EnvironmentSatisfaction', 'EnvironmentSatisfaction')]

    plot = pie_plot(hue)
    return render_template('pie.html', plot=plot, focus_hue=hue, drop_hue= list_hue)

@app.route('/data_fn')
def data_fn():
    data = pd.read_csv('JCDS Cahyo/Dashboard/dashboard_cpu/static/data_clean.csv')
    df = data.head(21).to_html(classes = 'data')
    return render_template('data.html',  tables=[df])


@app.route('/pred_lr')
## Menampilkan Dataset
def pred_lr():
    return render_template('predict.html')

@app.route('/pred_result', methods=['POST', 'GET'])
def pred_result():

    if request.method == 'POST':
    ## Untuk Predict
        input = request.form
            
        # EnvironmentSatisfaction= input['EnvironmentSatisfaction']
        # if EnvironmentSatisfaction == '1':
        #     EnvironmentSatisfaction = 1
        # elif EnvironmentSatisfaction == '2':
        #     EnvironmentSatisfaction = 2
        # elif EnvironmentSatisfaction == '3':
        #     EnvironmentSatisfaction = 3     
        # elif EnvironmentSatisfaction == '4':
        #     EnvironmentSatisfaction = 4
        
        # JobSatisfaction= input['JobSatisfaction']
        # if JobSatisfaction  == '1.0':
        #     JobSatisfaction = 1
        # elif JobSatisfaction  == '2.0':
        #     JobSatisfaction = 2
        # elif JobSatisfaction  == '3.0':
        #     JobSatisfaction = 3     
        # elif JobSatisfaction == '4.0':
        #     JobSatisfaction = 4

        EnvironmentSatisfaction=int(input['EnvironmentSatisfaction'])
        JobSatisfaction=int(input['JobSatisfaction'])

        Age= int(input['Age'])

        # BusinessTravel = ''
        # if BusinessTravel == 'Non-Travel':
        #     BusinessTravel = 0
        # elif BusinessTravel == 'Travel_Rarely':
        #     BusinessTravel = 1
        # elif BusinessTravel == 'Travel_Frequently':
        #     BusinessTravel = 2
        
        BusinessTravel=int(input['BusinessTravel'])
        TotalWorkingYears= int(input['TotalWorkingYears']) 
        MonthlyIncome= int(input['MonthlyIncome'])
        YearsAtCompany= int(input['YearsAtCompany'])
        YearsWithCurrManager= int(input['YearsWithCurrManager'])
        WorkingHours= int(input['WorkingHours'])
        
        feature= pd.DataFrame({
            'EnvironmentSatisfaction': [EnvironmentSatisfaction],
            'JobSatisfaction': [JobSatisfaction],
            'Age': [Age],
            'BusinessTravel': [BusinessTravel],
            'TotalWorkingYears': [TotalWorkingYears],
            'MonthlyIncome': [MonthlyIncome],
            'YearsAtCompany': [YearsAtCompany],
            'YearsWithCurrManager': [YearsWithCurrManager],
            'WorkingHours': [WorkingHours]
        })

        pred = model.predict(feature)[0].round(2)
        print(pred)

        if pred == 0:
            pred = 'No Attrition'
        else:
            pred = 'Yes Attrition'

        return render_template('result.html',
            EnvironmentSatisfaction= EnvironmentSatisfaction,
            JobSatisfaction= JobSatisfaction,
            Age= Age,
            BusinessTravel= BusinessTravel,
            TotalWorkingYears= TotalWorkingYears,
            MonthlyIncome= MonthlyIncome,
            YearsAtCompany= YearsAtCompany,
            YearsWithCurrManager= YearsWithCurrManager,
            WorkingHours= WorkingHours,
            pred= pred
            )


if __name__ == '__main__':
    ## Load Model
    model = joblib.load('JCDS Cahyo/Dashboard/dashboard_cpu/employee_attrition_RF_tuned')
    app.run(debug=True)