# NBA-predictions

## FICHEROS:
- requirements.txt
- config.txt
- etl.py (ejecutar con config.txt completo)
- etl_predictions.py (ejecutar)
- Report_Orlando Magic.pdf

### Requirements.txt
Fichero que contiene las librerías necesarias para la correcta ejecución del programa

### config.txt
Fichero que hay que completar con las claves de las API con el siguiente formato:
auth=xxxx   donde xxxx se corresponde con la clave de SPORTS API (https://dashboard.api-football.com/nba/tester)
key=yyyy    donde yyyy se corresponde con la clave de SPORTS DATA IO (https://sportsdata.io/developers/api-documentation/nba)

### etl.py
Programa que genera un reporte de un equipo de la NBA con información general sobre el equipo, datos de los jugadores, estadísticas de los jugadores (esto solamente en los casos en los que estén disponibles los datos) y estadísticas de juego del equipo. Toda esta información es la de la temporada actual (2022-2023). Cada reporte se guarda como Report_nombre_del_equipo.pdf.
AL comienzo del programa se pide al usuario que introduzca el nombre de un equipo o que presione ENTER para obtener el reporte de un equipo al azar de la lista de equipos disponibles (obtenida de la primera API)

### etl_predictions.py
Programa que ofrece una predicción sobre qué equipo va a ganar en el próximo partido que se juegue en la NBA. También permite al usuario introducir nombres de equipos de los que quiera conocer el resultado del próximo partido. Es decir, en todos los casos imprime por pantalla la predicción del próximo partido en general y, a continuación, permite al usuario buscar el próximo partido de todos los equipos que desee hasta que presione "ENTER".
Utiliza el pronóstico 1x2 de los datos de sportytrader (https://www.sportytrader.es/pronosticos/baloncesto/usa/nba-306/) que obtiene a través de webscrapping con Beautiful Soup considerando como ganador aquel equipo que tenga más apuestas a su favor en esa página.

### Report_Orlando_Magic.pdf
Ejemplo de reporte completo generado por la primera etl
