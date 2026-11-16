# ============================================================
#  PASO 3 (completo): login, crear / listar / ver / unirse / jugar.
# ============================================================

import random   # para escoger al azar quién empieza

# Traemos tres herramientas de Flask:
#   Flask   -> crea la aplicación (el servidor)
#   request -> permite leer lo que nos envió el cliente
#   jsonify -> convierte datos de Python en una respuesta JSON
from flask import Flask, request, jsonify

# Reutilizamos la lógica del paso 1 (archivo logica.py).
# Gracias al  if __name__ == "__main__"  de ese archivo, importar NO
# arranca el juego de consola: solo trae las funciones.
from logica import validar_numero, calcular_picas_fijas

app = Flask(__name__)    # creamos el servidor
app.json.ensure_ascii = False   # muestra tildes y ñ tal cual (no como í)

# "Base de datos" en memoria (el PDF dice que no se necesita BD).
# Si el servidor se apaga, se borra todo.
jugadores = []   # lista de nombres registrados
juegos = {}      # diccionario:  id del juego -> datos del juego


# ------------------------------------------------------------
#  Función auxiliar: lo que se le puede MOSTRAR a cualquiera
#  de un juego. Copia todo MENOS los números secretos.
# ------------------------------------------------------------
def vista_publica(juego):
    return {
        "id": juego["id"],
        "creador": juego["creador"],
        "jugadores": juego["jugadores"],
        "estado": juego["estado"],
        "turno": juego["turno"],
        "ganador": juego["ganador"],
        "intentos": juego["intentos"],
    }


# ------------------------------------------------------------
#  GET /   -> envía la página web (el archivo static/index.html)
#  "static" es la carpeta donde Flask busca archivos fijos
#  (HTML, imágenes, CSS...) por convención.
# ------------------------------------------------------------
@app.route("/", methods=["GET"])
def inicio():
    return app.send_static_file("index.html")


# ------------------------------------------------------------
#  POST /login  -> registra el nombre del jugador
#  El cliente envía:   {"nombre": "Ana"}
# ------------------------------------------------------------
@app.route("/login", methods=["POST"])
def login():
    # Leemos el cuerpo de la petición y lo convertimos de JSON a Python.
    # silent=True: si no es un JSON válido, devuelve None en vez de fallar.
    datos = request.get_json(silent=True)

    # Validación 1: tiene que ser un JSON con forma de objeto {...}
    if not isinstance(datos, dict):
        return jsonify({"error": "Debes enviar un JSON como {\"nombre\": \"Ana\"}"}), 400

    # Validación 2: tiene que traer un "nombre" que sea texto y no esté vacío
    nombre = datos.get("nombre")         # .get devuelve None si no existe
    if not isinstance(nombre, str) or nombre.strip() == "":
        return jsonify({"error": "Debes enviar un nombre"}), 400

    nombre = nombre.strip()              # quitamos espacios al inicio y al final

    # Si ya estaba registrado, simplemente le damos la bienvenida (200 = OK)
    if nombre in jugadores:
        return jsonify({"mensaje": "Bienvenido de nuevo, " + nombre,
                        "nombre": nombre}), 200

    # Si es nuevo, lo guardamos (201 = Created, "se creó algo nuevo")
    jugadores.append(nombre)
    return jsonify({"mensaje": "Jugador registrado: " + nombre,
                    "nombre": nombre}), 201


# ------------------------------------------------------------
#  GET /jugadores -> EXTRA (no lo pide el PDF), sirve para ver
#  en el navegador quiénes se han registrado.
# ------------------------------------------------------------
@app.route("/jugadores", methods=["GET"])
def listar_jugadores():
    return jsonify(jugadores)


# ------------------------------------------------------------
#  POST /juego  -> crear un juego
#  El cliente envía:   {"nombre": "Ana", "numero": "4271"}
# ------------------------------------------------------------
@app.route("/juego", methods=["POST"])
def crear_juego():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Debes enviar un JSON"}), 400

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    # El jugador debe haber hecho /login antes
    if nombre not in jugadores:
        return jsonify({"error": "Jugador no registrado, haz /login primero"}), 400

    # Validamos el número con la función del paso 1
    error = validar_numero(numero)
    if error is not None:
        return jsonify({"error": error}), 400

    # Creamos el juego. El id es simplemente el siguiente número:
    # si hay 0 juegos -> id 1, si hay 1 -> id 2, etc.
    id_juego = len(juegos) + 1
    juego = {
        "id": id_juego,
        "creador": nombre,
        "jugadores": [nombre],          # por ahora solo el creador
        "secretos": {nombre: numero},   # ¡esto NUNCA se envía al cliente!
        "estado": "esperando",          # esperando -> en_juego -> terminado
        "turno": None,                  # se decide cuando entre el 2.º jugador
        "ganador": None,
        "intentos": [],                 # historial de jugadas
    }
    juegos[id_juego] = juego

    return jsonify(vista_publica(juego)), 201


# ------------------------------------------------------------
#  GET /juego  -> listar todos los juegos (resumen)
# ------------------------------------------------------------
@app.route("/juego", methods=["GET"])
def listar_juegos():
    lista = []
    for juego in juegos.values():
        lista.append({
            "id": juego["id"],
            "creador": juego["creador"],
            "estado": juego["estado"],
            "jugadores": juego["jugadores"],
            "ganador": juego["ganador"],
        })
    return jsonify(lista)


# ------------------------------------------------------------
#  GET /juego/<id>  -> ver el estado de UN juego
#  <int:id_juego> significa: "aquí va un número, pásamelo a la
#  función en la variable id_juego". Ej: /juego/3 -> id_juego = 3
# ------------------------------------------------------------
@app.route("/juego/<int:id_juego>", methods=["GET"])
def ver_juego(id_juego):
    if id_juego not in juegos:
        return jsonify({"error": "El juego no existe"}), 404
    return jsonify(vista_publica(juegos[id_juego]))


# ------------------------------------------------------------
#  PUT /juego/<id>  -> unirse a un juego
#  El cliente envía:   {"nombre": "Luis", "numero": "5689"}
#  Códigos que usamos:
#    400 = la petición está mal escrita (dato inválido)
#    404 = el juego no existe
#    409 = la petición está bien, pero choca con el estado del juego
#          (Conflict), por ejemplo: el juego ya está lleno
# ------------------------------------------------------------
@app.route("/juego/<int:id_juego>", methods=["PUT"])
def unirse_juego(id_juego):
    if id_juego not in juegos:
        return jsonify({"error": "El juego no existe"}), 404
    juego = juegos[id_juego]

    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Debes enviar un JSON"}), 400

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    if nombre not in jugadores:
        return jsonify({"error": "Jugador no registrado, haz /login primero"}), 400

    if nombre in juego["jugadores"]:
        return jsonify({"error": "Ya estás en este juego"}), 400

    if juego["estado"] != "esperando":
        return jsonify({"error": "El juego ya no acepta jugadores"}), 409

    error = validar_numero(numero)
    if error is not None:
        return jsonify({"error": error}), 400

    # Todo bien: agregamos al segundo jugador y el juego INICIA
    juego["jugadores"].append(nombre)
    juego["secretos"][nombre] = numero
    juego["estado"] = "en_juego"
    juego["turno"] = random.choice(juego["jugadores"])   # primer turno al azar

    return jsonify(vista_publica(juego)), 200


# ------------------------------------------------------------
#  POST /juego/<id>/jugar  -> enviar un intento
#  El cliente envía:   {"nombre": "Ana", "numero": "1234"}
# ------------------------------------------------------------
@app.route("/juego/<int:id_juego>/jugar", methods=["POST"])
def jugar(id_juego):
    if id_juego not in juegos:
        return jsonify({"error": "El juego no existe"}), 404
    juego = juegos[id_juego]

    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Debes enviar un JSON"}), 400

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    if nombre not in juego["jugadores"]:
        return jsonify({"error": "No eres jugador de este juego"}), 400

    if juego["estado"] != "en_juego":
        return jsonify({"error": "El juego no está en curso"}), 409

    if juego["turno"] != nombre:
        return jsonify({"error": "No es tu turno, es el turno de "
                        + juego["turno"]}), 409

    error = validar_numero(numero)
    if error is not None:
        return jsonify({"error": error}), 400

    # ¿Quién es el rival? El jugador de la lista que NO soy yo.
    if juego["jugadores"][0] == nombre:
        rival = juego["jugadores"][1]
    else:
        rival = juego["jugadores"][0]

    # Comparamos contra el secreto del RIVAL (función del paso 1)
    fijas, picas = calcular_picas_fijas(juego["secretos"][rival], numero)

    # Guardamos la jugada en el historial
    juego["intentos"].append({
        "jugador": nombre,
        "numero": numero,
        "fijas": fijas,
        "picas": picas,
    })

    if fijas == 4:
        # ¡Adivinó! El juego termina
        juego["estado"] = "terminado"
        juego["ganador"] = nombre
        juego["turno"] = None
    else:
        # No adivinó: el turno pasa al rival
        juego["turno"] = rival

    return jsonify({
        "fijas": fijas,
        "picas": picas,
        "ganaste": fijas == 4,
        "juego": vista_publica(juego),
    }), 200


# Arranca el servidor cuando ejecutamos "python app.py"
#   host="0.0.0.0" -> acepta conexiones que vengan de FUERA de la máquina
#                     (necesario dentro de un contenedor; con el valor por
#                     defecto, 127.0.0.1, solo aceptaría conexiones internas)
#   port=5000      -> el "número de puerta" donde escucha el servidor
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
