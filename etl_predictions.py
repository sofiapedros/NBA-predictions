from bs4 import BeautifulSoup
import requests

def extract():
    '''
    Función que extrae todos los datos de la página
    web sobre la que se va a basar la predicción.

    '''
    # Abrimos la página web de la que vamos a coger los datos
    r = requests.get('https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/')

    return r

def transform(a):
    '''
    Función que transforma la request en un objeto de beautiful soup
    y busca los datos de los equipos y victorias que se usarán en la
    predicción.
    '''
    # Creamos el objeto de BeuatifulSoup
    soup = BeautifulSoup(a.text, 'lxml')

    # Busca todos los equipos que aparece que juegan proximamente
    equipos = soup.find_all("div", {"class":"w-1/2 text-center break-word p-1 dark:text-white"})
    
    # Adaptamos el formato:
    for i in range(len(equipos)):

        equipos[i] = equipos[i].text[1:-1]
    # Para ver quién tiene más probabilidades de ganar, usamos los datos de la página, que muestra en verde
    # el equipo que gana (1 o 2, dependiendo si es el equipo que aparece a la izquierda o a la derecha en la web)
    # también pueden empatar, que es lo que ocurre cuando se marca una x en verde. En todos los casos, por cómo está
    # creada la página, podemos encontrar por un lado (con las mismas etiquetas) qué valores (entre "1","X" y "2")
    # están en gris y cuál es el que está en verde. 

    # Entonces, para hacer la predicción, vamos a buscar qué elemento está en verde para el próximo partido y, en
    # función de su valor, devolveremos si gana el primer equipo, el segundo o hay empate
    verde = soup.find_all("span",{"class": "flex justify-center items-center h-7 w-6 rounded-md font-semibold bg-primary-green text-white mx-1"})

    return equipos, verde

def load(equipos, verde):
    '''
    Función que con los datos de equipos y quién tiene
    más probabilidades de ganar, imprime el resultado por
    pantalla (predicción para el próximo partido)
    '''
    if verde[0].text == "1":
        print(f"En el próximo partido ganará: {equipos[0]} a {equipos[1]}")
    
    elif verde[0].text == "2":
        print(f"En el próximo partido ganará {equipos[1]} a {equipos[0]}")
    
    else:
        print(f"En el próximo partido empatarán {equipos[0]} y {equipos[1]}")


if __name__ == "__main__":
    
    request = extract()
    equipos, verde = transform(request)
    load(equipos, verde)

    # Vamos a dar la opción al usuario de consultar el resultado para un partido que solicite
    equipo = input("Introduzca el nombre del equipo del que quiere consultar la predicción para su próximo partido o ENTER para salir: ",)
    while equipo != "":
        if equipo in equipos:
            indice = equipos.index(equipo)
            impar = True
            if indice % 2 == 0:
                impar = False

            indicev = indice//2

            if verde[indicev].text == "1" and impar:
                print(f"En el próximo partido ganará: {equipos[indice-1]} a {equipos[indice]}")
            
            elif verde[indicev].text == "1" and not impar:
                print(f"En el próximo partido ganará {equipos[indice]} a {equipos[indice+1]}")
            
            elif verde[indicev].text == "2" and impar:
                print(f"En el próximo partido ganará {equipos[indice]} a {equipos[indice-1]}")
            
            elif verde[indicev].text == "2" and not impar:
                print(f"En el próximo partido ganará {equipos[indice+1]} a {equipos[indice]}")
            
            elif verde[indicev].text == "X" and impar:
                print(f"En el próximo partido ganará {equipos[indice-1]} a {equipos[indice]}")
            
            else:
                print(f"En el próximo partido empatarán {equipos[indice]} y {equipos[indice+1]}")
        else:
            print("Lo sentimos, el equipo que ha introudcido no tiene próximos partidos disponibles")
        
        equipo = input("Introduzca el nombre del equipo del que quiere consultar la predicción para su próximo partido o ENTER para salir: ",)
