# Código de una ETL que extraiga datos de una API de datos de la NBA y guarde un informe de los puntos clave del equipo en cuestión en formato pdf 
# Una ETL que obtenga datos usando técnicas de web scraping donde se tendrá que elegir una fuente de datos para obtener pronósticos y ofrezca
# por pantalla la predicción para el próximo partido


'''
En el informe estará todo lo que devuelva con el nombre del equipo
y todo lo que devuelva con jugadores en el equipo y las estadísticas
de ese equipo
'''
import requests
import json
import pandas as pd
from fpdf import FPDF
from fpdf.enums import XPos, YPos
import random

class PDF(FPDF):
    '''
    Clase pdf para crear un pdf
    '''
    # Cabecera que aparece en todas las páginas
    def header(self):
        self.image('NBA_logo.png',10,8,20)
        # Asignamos el tipo de letra times en negrita de tamaño 20
        self.set_font('times','B',20)
        # Espacio en blanco entre el logo y el título
        self.cell(20,20)
        # Título del reporte en el centro
        self.cell(0,10,'TEAM REPORT', new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False,align='C')
    
    # Pie de página
    def footer(self):
        # Espacio en blanco al final de cada página: 15mm
        self.set_y(-15)
        # Tipo de letra del lnúmero de páginas, times tamaño 10 en cursiva
        self.set_font('times','I',10)
        # Número de página
        self.cell(0,10,f'Page {self.page_no()}',align = 'C')


def extract(team_name, auth, key):
    '''
    Función que extrae los datos a incluir en el
    reporde de dos apis y los guarda en un diccionario
    '''
    dic = {}
    # DATOS GENERALES DEL EQUIPO:
    url = f"https://v2.nba.api-sports.io/teams?name={team_name}"

    payload={}
    headers = {
    'x-rapidapi-key': auth,
    'x-rapidapi-host': 'api-nba-v1.p.rapidapi.com'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    resp = response.json()

    team_id = resp['response'][0]['id']
    team_abr = resp['response'][0]['code']

    dic['DATOS GENERALES'] = resp['response'][0]

    # Jugadores
    url = f"https://v2.nba.api-sports.io/players/?team={team_id}&season=2022"

    payload={}
    headers = {
    'x-rapidapi-key': auth,
    'x-rapidapi-host': 'api-nba-v1.p.rapidapi.com'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()
    dic['JUGADORES'] = response['response']

    # Estadísticas
    url = f"https://v2.nba.api-sports.io/teams/statistics?season=2022&id={team_id}"

    payload={}
    headers = {
    'x-rapidapi-key': auth,
    'x-rapidapi-host': 'api-nba-v1.p.rapidapi.com'
    }

    response = requests.request("GET", url, headers=headers, data=payload)
    response = response.json()

    dic['ESTADISTICAS'] = response['response'][0]

    
    # ESTADÍSTICAS JUGADORES

    url = f"https://api.sportsdata.io/v3/nba/scores/json/Players/{team_abr}?key={key}"

    response = requests.request("GET", url)
    response = response.json()
    

    dic['ESTADISTICAS_JUGADORES'] = response

    # ESTADÍSTICAS POR POR JUGADOR
    url = f" https://api.sportsdata.io/v3/nba/stats/json/PlayerSeasonStatsByTeam/2022/{team_abr}?key={key}"

    response = requests.request("GET", url)
    response = response.json()
    

    dic['ESTADISTICAS_JU'] = response


    return dic


def transform(dic):
    '''
    La mayoría de los datos que devuelve, se pueden cargar en un pdf
    como están. Para facilitar la subida de los jugadores y sus
    estadísticas, vamos a crear dos dataframes. En el primero estarán
    en cada fila un jugador con sus datos más importantes y en el segundo
    las estadísticas de los jugadores por filas. 
    También hay que cambiar el formato de leages para que se vea mejor
    '''

    # Creamos el primer dataframe
    df = pd.DataFrame(columns=['Name','Lastname','nba_start','nba_pro','affiliation','position','injury_status'])

    # Pasamos los datos a un dataframe
    datos_recogidos_API = dic['JUGADORES']
    datos_jugadores = dic['ESTADISTICAS_JUGADORES']
    for i in range(len(datos_recogidos_API)):
        name = datos_recogidos_API[i]['firstname']
        lastname = datos_recogidos_API[i]['lastname']
        nba_start = datos_recogidos_API[i]['nba']['start']
        nba_pro = datos_recogidos_API[i]['nba']['pro']
        affiliation = datos_recogidos_API[i]['affiliation']
        
        # Para poder incluir en el reporte datos sobre su posición
        # y si está o no lesionado (que venían de otra request)
        for i in range(len(datos_jugadores)):
            if datos_jugadores[i]['FirstName'] == name:
                datos_jugador = datos_jugadores[i]
                break
        try:
            position = datos_jugador['Position']
            injury = datos_jugador['InjuryStatus']
            df.loc[i] = [name, lastname, nba_start, nba_pro, affiliation, position, injury]
        except:
            df.loc[i] = [name, lastname, nba_start, nba_pro, affiliation, "None", "Scrambled"]

    # Cambiamos el formato de leagues a una lista
    leages = dic['DATOS GENERALES']['leagues']
    dic['DATOS GENERALES']['leagues'] = list(leages.keys())

    # ESTADISTICAS JUGADORES
    df2 = pd.DataFrame(columns=['Name','Games','EffectiveFieldGoalsPercentage','TwoPointersPercentage','ThreePointersPercentage','FreeThrowsPercentage','PlayerEfficiencyRating'])
    estadisticas = dic['ESTADISTICAS_JU']
    # Cargamos los datos para cada jugador en una fila
    for i in range(len(estadisticas)):
        name = estadisticas[i]['Name']
        games = estadisticas[i]['Games']
        fg = estadisticas[i]['EffectiveFieldGoalsPercentage']
        tp = estadisticas[i]['TwoPointersPercentage']
        t3p = estadisticas[i]['ThreePointersPercentage']
        ft = estadisticas[i]['FreeThrowsPercentage']
        pe = estadisticas[i]['PlayerEfficiencyRating']
        df2.loc[i] = [name,games,fg,tp,t3p,ft,pe]

    return df, df2


def load(dic, df, df2):
    '''
    Función que crea un pdf con todos los datos
    recogidos del equipo
    '''

    # Nombre del equipo: para guardar el pdf
    # con ese nombre
    equipo = dic['DATOS GENERALES']['name']

    # Creamos el objeto pdf
    pdf = PDF('P','mm','A4')

    # Cuando queden 15 mm al final de la página,
    # crea una nueva página automáticamente
    pdf.set_auto_page_break(auto = True, margin = 15)
    pdf.set_font('times','B',20)

    # Añadimos una página
    pdf.add_page()
    
    # AÑADIR DATOS GENERALES
    # Se incluirán en una página los detalles generales del equipo
    datos_generales = dic['DATOS GENERALES']
    pdf.cell(120,25,'GENERAL INFORMATION',new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
    pdf.set_font('times','',11)
    for key, value in datos_generales.items():
        pdf.cell(70,10,key)
        pdf.cell(70,10,str(value),new_x=XPos.LMARGIN, new_y=YPos.NEXT)


    pdf.add_page()
    
    # AÑADIR JUGADORES
    # En esta parte se crea una tabla con todos los jugadores
    # y sus datos generales (sin incluir estadísticas de juego)
    pdf.set_font('times','B',20)
    pdf.cell(120,25,'PLAYERS',new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
    pdf.set_font('times','B',10)
    pdf.cell(20,10,'Name',border=True)
    pdf.cell(20,10,"Lastname",border=True)
    pdf.cell(20,10,"nba_start",border=True)
    pdf.cell(20,10,"nba_pro",border=True)
    pdf.cell(20,10,"Position",border=True)
    pdf.cell(30,10,"Injury status",border=True)
    pdf.cell(60,10,'affiliation',new_x=XPos.LMARGIN, new_y=YPos.NEXT,border=True)
    pdf.set_font('times','',9)
    for i in range(len(df)):
        fila = df.iloc[i]
        name = fila['Name']
        lastname = fila['Lastname']
        nba_start = str(fila['nba_start'])
        nba_pro = str(fila['nba_pro'])
        position = str(fila['position'])
        injury = str(fila['injury_status'])
        affiliation = str(fila['affiliation'])
        pdf.cell(20,10,name,border=True)
        pdf.cell(20,10,lastname,border=True)
        pdf.cell(20,10,nba_start,border=True)
        pdf.cell(20,10,nba_pro,border=True)
        pdf.cell(20,10,position,border=True)
        pdf.cell(30,10,injury,border=True)
        pdf.cell(60,10,affiliation,new_x=XPos.LMARGIN, new_y=YPos.NEXT,border=True)

    # AÑADIR ESTADÍSTICAS
    
    if len(df2)>1:
        pdf.add_page()
        # AÑADIR JUGADORES
        # Aquí se añade al pdf las estadísticas de las jugadores, también en formato de tabla
        pdf.set_font('times','B',20)
        pdf.cell(120,25,'PLAYER STADISTICS',new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
        pdf.set_font('times','B',9)
        pdf.cell(30,10,'Name',border=True)
        pdf.cell(20,10,"Games",border=True)
        pdf.cell(20,10,"FieldGoals",border=True)
        pdf.cell(20,10,"TwoPointers",border=True)
        pdf.cell(25,10,"ThreePointers",border=True)
        pdf.cell(30,10,"FreeThrows",border=True)
        pdf.cell(30,10,'EfficiencyRating',new_x=XPos.LMARGIN, new_y=YPos.NEXT,border=True)
        pdf.set_font('times','',9)
        for i in range(len(df2)):
            fila = df2.iloc[i]
            name = fila['Name']
            lastname = str(fila['Games'])
            nba_start = str(fila['EffectiveFieldGoalsPercentage'])
            nba_pro = str(fila['TwoPointersPercentage'])
            position = str(fila['ThreePointersPercentage'])
            injury = str(fila['FreeThrowsPercentage'])
            affiliation = str(fila['PlayerEfficiencyRating'])
            pdf.cell(30,10,name,border=True)
            pdf.cell(20,10,lastname,border=True)
            pdf.cell(20,10,nba_start,border=True)
            pdf.cell(20,10,nba_pro,border=True)
            pdf.cell(25,10,position,border=True)
            pdf.cell(30,10,injury,border=True)
            pdf.cell(30,10,affiliation,new_x=XPos.LMARGIN, new_y=YPos.NEXT,border=True)

    # AÑADIR ESTADÍSTICAS GENRALES
    # Se añade una lista con las estadísticas generales del equipo
    pdf.add_page()
    estadisticas = dic['ESTADISTICAS']
    pdf.set_font('times','B',20)
    pdf.cell(120,25,'TEAM STADISTICS',new_x=XPos.LMARGIN, new_y=YPos.NEXT, border=False)
    pdf.set_font('times','',9)
    for key, value in estadisticas.items():
        pdf.cell(70,10,key)
        pdf.cell(70,10,str(value),new_x=XPos.LMARGIN, new_y=YPos.NEXT)


    # GUARDAR EL REPORTE
    pdf.output(f"Report_{equipo}.pdf")
    return 


if __name__ == "__main__":
    with open('config.txt','r') as file:
        line = file.readline()
        auth = line.split("=")
        auth = auth[1]
        auth = auth.split("\n")[0]
        line_2 = file.readline()
        key = line_2.split("=")
        key = key[1]
    
    posible_names = ['Boston Celtics','Brooklyn Nets','New York Knicks','Philadelphia 76ers',
                    'Toronto Raptors','Golden State Warriors','LA Clippers','Los Angeles Lakers',
                    'Sacramento Kings','Chicago Bulls','Cleveland Cavaliers',
                    'Detroit Pistons','Milwaukee Bucks','Atlanta Hawks',           
                    'Charlotte Hornets','Miami Heat','Orlando Magic','Washington Wizards',
                    'Minnesota Timberwolves','Oklahoma City Thunder',
                    'Portland Trail Blazers','Dallas Mavericks','Houston Rockets',
                    'Memphis Grizzlies','New Orleans Pelicans','San Antonio Spurs']

    name = input("Introduce the name of the team you want a report from (or press ENTER to obtain an example report of a random team) ")
    print("Take into account that the report will be generated for the current season (2022-2023)")

    if name not in posible_names and name != "":
        print("The team you entered is not valid, a report from a random team will be generated")
        print("Note the names of the teams must be written with a capitalized first letter in every word")
        name = ""

    if name == "":
        name = posible_names[random.randint(0,len(posible_names)-1)]
        print(f"Report will be generated for {name}")
        dic = extract(name, auth, key)

    else:
        dic = extract(name, auth, key)
    df, df2 = transform(dic)
    
    load(dic, df,df2)
    print(f"Report generated for {name}")