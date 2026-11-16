# ============================================================
#  PASO 1: La lógica del juego "Picas y Fijas" (sin internet,
#  sin servidor, sin Kubernetes). Solo Python puro.
# ============================================================

import random   # librería estándar de Python para números aleatorios


def validar_numero(numero):
    """
    Revisa que el número cumpla las reglas.
    Devuelve un texto con el error, o None si todo está bien.
    """
    # 1) Debe llegar como texto (string). Lo tratamos como texto y no
    #    como entero para que "0123" no pierda el cero inicial.
    if not isinstance(numero, str):
        return "El número debe ser un texto, por ejemplo \"4271\""

    # 2) Exactamente 4 caracteres
    if len(numero) != 4:
        return "El número debe tener exactamente 4 dígitos"

    # 3) Cada carácter debe ser un dígito del 0 al 9 (nada de letras,
    #    espacios, signos...)
    for caracter in numero:
        if caracter not in "0123456789":
            return "El número solo puede contener dígitos (0-9)"

    # 4) Sin dígitos repetidos. Un "set" (conjunto) elimina repetidos:
    #    set("4271") -> {'4','2','7','1'} (4 elementos)
    #    set("4471") -> {'4','7','1'}     (3 elementos) -> hay repetido
    if len(set(numero)) != 4:
        return "Los 4 dígitos deben ser diferentes"

    return None   # None = "no hay error"


def calcular_picas_fijas(secreto, intento):
    """
    Compara el intento con el secreto, posición por posición.
    - Fija: mismo dígito en la misma posición.
    - Pica: el dígito existe en el secreto, pero en otra posición.
    """
    fijas = 0
    picas = 0
    for i in range(4):                 # i toma los valores 0, 1, 2, 3
        if intento[i] == secreto[i]:
            fijas = fijas + 1
        elif intento[i] in secreto:
            picas = picas + 1
    return fijas, picas


# ------------------------------------------------------------
#  Pruebas rápidas: si algo está mal, "assert" detiene el programa
# ------------------------------------------------------------
def probar():
    # El ejemplo exacto del PDF del profesor
    assert calcular_picas_fijas("4271", "1234") == (1, 2)
    assert calcular_picas_fijas("4271", "4271") == (4, 0)
    assert calcular_picas_fijas("4271", "5689") == (0, 0)

    assert validar_numero("4271") is None
    assert validar_numero("0123") is None
    assert validar_numero("123") is not None     # muy corto
    assert validar_numero("12a4") is not None    # tiene letra
    assert validar_numero("1123") is not None    # dígito repetido
    assert validar_numero(1234) is not None      # no es texto
    print("Todas las pruebas pasaron ✔")


# ------------------------------------------------------------
#  Un juego de 2 jugadores en la consola (para practicar los turnos)
# ------------------------------------------------------------
def pedir_numero(mensaje):
    while True:                         # repite hasta que sea válido
        numero = input(mensaje)
        error = validar_numero(numero)
        if error is None:
            return numero
        print("  ✘", error)


def jugar_en_consola():
    nombres = [input("Nombre jugador 1: "), input("Nombre jugador 2: ")]
    secretos = [pedir_numero(nombres[0] + ", escribe tu número secreto: "),
                pedir_numero(nombres[1] + ", escribe tu número secreto: ")]

    turno = random.randint(0, 1)        # 0 o 1 al azar: quién empieza
    print("\nEmpieza", nombres[turno], "(escogido al azar)\n")

    while True:
        rival = 1 - turno               # si turno es 0, rival es 1, y viceversa
        intento = pedir_numero(nombres[turno] + ", adivina el número de "
                               + nombres[rival] + ": ")
        fijas, picas = calcular_picas_fijas(secretos[rival], intento)
        print("  ->", fijas, "fijas,", picas, "picas")

        if fijas == 4:
            print("\n¡Ganó", nombres[turno] + "!")
            break
        turno = rival                   # cambio de turno


# Esto solo se ejecuta cuando corres el archivo directamente
if __name__ == "__main__":
    probar()
    jugar_en_consola()
