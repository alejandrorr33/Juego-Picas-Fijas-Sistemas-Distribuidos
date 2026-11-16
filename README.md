# Picas y Fijas — versión distribuida

Proyecto del curso **Sistemas Distribuidos**. Es el juego "Picas y Fijas" para
dos jugadores, implementado como un servicio **RESTful con JSON** en Python
(Flask), con un front básico en HTML/JavaScript, y desplegable en **Kubernetes**.

## Reglas del juego

Cada jugador elige un número secreto de 4 dígitos, todos diferentes. Por turnos,
cada uno intenta adivinar el número del otro y recibe:

- **Fija:** dígito correcto en la posición correcta.
- **Pica:** dígito correcto en otra posición.

Ejemplo: secreto `4271`, intento `1234` → 1 fija (el 2) y 2 picas (el 4 y el 1).
Gana el primero que logra 4 fijas.

## Estructura del proyecto

```
app.py              -> servidor Flask: todos los endpoints
logica.py           -> reglas del juego: validar número y calcular picas/fijas
static/index.html   -> front básico para jugar desde el navegador
requirements.txt    -> librerías de Python que necesita el proyecto
```

## Endpoints

| Método | Ruta                   | Qué hace                                   | Cuerpo JSON de ejemplo                   |
|--------|------------------------|--------------------------------------------|------------------------------------------|
| POST   | `/login`               | Registra el nombre del jugador             | `{"nombre": "Ana"}`                      |
| POST   | `/juego`               | Crea un juego con el número del creador    | `{"nombre": "Ana", "numero": "4271"}`    |
| PUT    | `/juego/{id}`          | Se une al juego; el juego inicia           | `{"nombre": "Luis", "numero": "5689"}`   |
| POST   | `/juego/{id}/jugar`    | Envía un intento (solo en su turno)        | `{"nombre": "Ana", "numero": "1234"}`    |
| GET    | `/juego/{id}`          | Estado del juego (y ganador si terminó)    | —                                        |
| GET    | `/juego`               | Lista todos los juegos                     | —                                        |

Códigos de respuesta: `200` OK, `201` creado, `400` datos inválidos,
`404` juego no existe, `409` acción no permitida en el estado actual del juego.

## Cómo ejecutarlo en tu computador

```
pip install -r requirements.txt
python app.py
```

Luego abre <http://127.0.0.1:5000/> en el navegador.
