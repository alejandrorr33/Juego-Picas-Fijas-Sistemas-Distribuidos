DIGITOS = 4


def validar_numero(numero):
    if not isinstance(numero, str):
        return "El número debe ser un texto, por ejemplo \"4271\""
    if len(numero) != DIGITOS:
        return f"El número debe tener exactamente {DIGITOS} dígitos"
    if not all(c in "0123456789" for c in numero):
        return "El número solo puede contener dígitos (0-9)"
    if len(set(numero)) != DIGITOS:
        return f"Los {DIGITOS} dígitos deben ser diferentes"
    return None


def calcular_picas_fijas(secreto, intento):
    fijas = 0
    picas = 0
    for i in range(DIGITOS):
        if intento[i] == secreto[i]:
            fijas += 1
        elif intento[i] in secreto:
            picas += 1
    return fijas, picas


if __name__ == "__main__":
    assert calcular_picas_fijas("4271", "1234") == (1, 2)
    assert calcular_picas_fijas("4271", "4271") == (4, 0)
    assert calcular_picas_fijas("4271", "5689") == (0, 0)
    assert validar_numero("0123") is None
    assert validar_numero("123") is not None
    assert validar_numero("12a4") is not None
    assert validar_numero("1123") is not None
    assert validar_numero(1234) is not None
    print("Pruebas OK")
