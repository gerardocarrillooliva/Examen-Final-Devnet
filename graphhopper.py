import os
import requests

API_KEY = os.getenv("GRAPHHOPPER_API_KEY")

if not API_KEY:
    print("ERROR: No se encontró la API Key de GraphHopper.")
    print("Configure la variable GRAPHHOPPER_API_KEY antes de ejecutar el programa.")
    exit()


def obtener_coordenadas(ciudad):
    url = "https://graphhopper.com/api/1/geocode"

    parametros = {
        "q": ciudad,
        "locale": "es",
        "limit": 1,
        "key": API_KEY
    }

    respuesta = requests.get(url, params=parametros)
    datos = respuesta.json()

    if "hits" not in datos or len(datos["hits"]) == 0:
        return None

    resultado = datos["hits"][0]

    return resultado["point"]["lat"], resultado["point"]["lng"]


def calcular_ruta(origen, destino, transporte):
    url = "https://graphhopper.com/api/1/route"

    parametros = [
        ("point", f"{origen[0]},{origen[1]}"),
        ("point", f"{destino[0]},{destino[1]}"),
        ("profile", transporte),
        ("locale", "es"),
        ("instructions", "true"),
        ("calc_points", "true"),
        ("key", API_KEY)
    ]

    respuesta = requests.get(url, params=parametros)
    return respuesta.json()


while True:
    print("\n===== RUTA CHILE - ARGENTINA =====")
    print("Escriba V para salir.")

    ciudad_origen = input("Ciudad de Origen: ")

    if ciudad_origen.lower() == "v":
        print("Programa finalizado.")
        break

    ciudad_destino = input("Ciudad de Destino: ")

    if ciudad_destino.lower() == "v":
        print("Programa finalizado.")
        break

    print("\nSeleccione medio de transporte:")
    print("1. Automóvil")
    print("2. Bicicleta")
    print("3. A pie")

    opcion = input("Opción: ")

    if opcion == "1":
        transporte = "car"
    elif opcion == "2":
        transporte = "bike"
    elif opcion == "3":
        transporte = "foot"
    else:
        print("Opción no válida.")
        continue

    print("\nBuscando ciudades...")

    origen = obtener_coordenadas(ciudad_origen + ", Chile")
    destino = obtener_coordenadas(ciudad_destino + ", Argentina")

    if origen is None or destino is None:
        print("No fue posible encontrar una de las ciudades.")
        continue

    datos_ruta = calcular_ruta(origen, destino, transporte)

    if "paths" not in datos_ruta:
        print("No fue posible calcular la ruta.")
        print(datos_ruta)
        continue

    ruta = datos_ruta["paths"][0]

    kilometros = ruta["distance"] / 1000
    millas = kilometros * 0.621371

    tiempo_ms = ruta["time"]
    minutos_totales = tiempo_ms / 60000

    horas = int(minutos_totales // 60)
    minutos = int(minutos_totales % 60)

    print("\n===== INFORMACIÓN DEL VIAJE =====")
    print(f"Ciudad de Origen: {ciudad_origen}")
    print(f"Ciudad de Destino: {ciudad_destino}")
    print(f"Distancia en kilómetros: {kilometros:.2f} km")
    print(f"Distancia en millas: {millas:.2f} mi")
    print(f"Duración estimada: {horas} horas y {minutos} minutos")

    print("\n===== NARRATIVA DEL VIAJE =====")

    for paso in ruta["instructions"]:
        texto = paso["text"]
        distancia = paso["distance"] / 1000

        print(f"- {texto} ({distancia:.2f} km)")