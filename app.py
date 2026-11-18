import random

from flask import Flask, jsonify, request

from logica import DIGITOS, calcular_picas_fijas, validar_numero

app = Flask(__name__)
app.json.ensure_ascii = False

jugadores = []
juegos = {}


def responder_error(mensaje, codigo=400):
    return jsonify({"error": mensaje}), codigo


def leer_datos():
    datos = request.get_json(silent=True)
    if isinstance(datos, dict):
        return datos
    return None


def vista_publica(juego):
    return {clave: valor for clave, valor in juego.items() if clave != "secretos"}


@app.route("/", methods=["GET"])
def inicio():
    return app.send_static_file("index.html")


@app.route("/login", methods=["POST"])
def login():
    datos = leer_datos()
    if datos is None:
        return responder_error("Debes enviar un JSON como {\"nombre\": \"Ana\"}")

    nombre = datos.get("nombre")
    if not isinstance(nombre, str) or nombre.strip() == "":
        return responder_error("Debes enviar un nombre")
    nombre = nombre.strip()

    if nombre in jugadores:
        return jsonify({"mensaje": f"Bienvenido de nuevo, {nombre}", "nombre": nombre}), 200

    jugadores.append(nombre)
    return jsonify({"mensaje": f"Jugador registrado: {nombre}", "nombre": nombre}), 201


@app.route("/jugadores", methods=["GET"])
def listar_jugadores():
    return jsonify(jugadores)


@app.route("/juego", methods=["POST"])
def crear_juego():
    datos = leer_datos()
    if datos is None:
        return responder_error("Debes enviar un JSON")

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    if nombre not in jugadores:
        return responder_error("Jugador no registrado, haz /login primero")

    problema = validar_numero(numero)
    if problema is not None:
        return responder_error(problema)

    id_juego = len(juegos) + 1
    juegos[id_juego] = {
        "id": id_juego,
        "creador": nombre,
        "jugadores": [nombre],
        "secretos": {nombre: numero},
        "estado": "esperando",
        "turno": None,
        "ganador": None,
        "intentos": [],
    }
    return jsonify(vista_publica(juegos[id_juego])), 201


@app.route("/juego", methods=["GET"])
def listar_juegos():
    resumen = []
    for juego in juegos.values():
        resumen.append({
            "id": juego["id"],
            "creador": juego["creador"],
            "estado": juego["estado"],
            "jugadores": juego["jugadores"],
            "ganador": juego["ganador"],
        })
    return jsonify(resumen)


@app.route("/juego/<int:id_juego>", methods=["GET"])
def ver_juego(id_juego):
    juego = juegos.get(id_juego)
    if juego is None:
        return responder_error("El juego no existe", 404)
    return jsonify(vista_publica(juego))


@app.route("/juego/<int:id_juego>", methods=["PUT"])
def unirse_juego(id_juego):
    juego = juegos.get(id_juego)
    if juego is None:
        return responder_error("El juego no existe", 404)

    datos = leer_datos()
    if datos is None:
        return responder_error("Debes enviar un JSON")

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    if nombre not in jugadores:
        return responder_error("Jugador no registrado, haz /login primero")
    if nombre in juego["jugadores"]:
        return responder_error("Ya estás en este juego")
    if juego["estado"] != "esperando":
        return responder_error("El juego ya no acepta jugadores", 409)

    problema = validar_numero(numero)
    if problema is not None:
        return responder_error(problema)

    juego["jugadores"].append(nombre)
    juego["secretos"][nombre] = numero
    juego["estado"] = "en_juego"
    juego["turno"] = random.choice(juego["jugadores"])
    return jsonify(vista_publica(juego)), 200


@app.route("/juego/<int:id_juego>/jugar", methods=["POST"])
def jugar(id_juego):
    juego = juegos.get(id_juego)
    if juego is None:
        return responder_error("El juego no existe", 404)

    datos = leer_datos()
    if datos is None:
        return responder_error("Debes enviar un JSON")

    nombre = datos.get("nombre")
    numero = datos.get("numero")

    if nombre not in juego["jugadores"]:
        return responder_error("No eres jugador de este juego")
    if juego["estado"] != "en_juego":
        return responder_error("El juego no está en curso", 409)
    if juego["turno"] != nombre:
        return responder_error(f"No es tu turno, es el turno de {juego['turno']}", 409)

    problema = validar_numero(numero)
    if problema is not None:
        return responder_error(problema)

    primero, segundo = juego["jugadores"]
    rival = segundo if nombre == primero else primero

    fijas, picas = calcular_picas_fijas(juego["secretos"][rival], numero)
    juego["intentos"].append({"jugador": nombre, "numero": numero, "fijas": fijas, "picas": picas})

    gano = fijas == DIGITOS
    if gano:
        juego["estado"] = "terminado"
        juego["ganador"] = nombre
        juego["turno"] = None
    else:
        juego["turno"] = rival

    return jsonify({
        "fijas": fijas,
        "picas": picas,
        "ganaste": gano,
        "juego": vista_publica(juego),
    }), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
