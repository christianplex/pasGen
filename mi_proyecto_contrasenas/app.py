import random
import csv
from flask import Flask, render_template

app = Flask(__name__)

# Función para cargar y procesar las palabras del CSV
# Esto se hace una sola vez cuando se inicia el servidor, ¡lo que lo hace muy rápido!
def cargar_palabras(nombre_archivo="palabras.csv"):
    palabras = []
    try:
        with open(nombre_archivo, mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.reader(archivo)
            for fila in lector_csv:
                if fila and fila[0].strip():
                    palabra = fila[0].strip().lower()
                    palabras.append(palabra)
    except FileNotFoundError:
        return []
    return palabras

# Cargar las palabras al iniciar la aplicación
PALABRAS_DISPONIBLES = cargar_palabras()

@app.route('/')
def index():
    contrasena = generar_contrasena_doble_palabra()
    return render_template('index.html', contrasena=contrasena)

def generar_contrasena_doble_palabra():
    palabras = PALABRAS_DISPONIBLES
    
    if len(palabras) < 2:
        return "Error: Se necesitan al menos 2 palabras en el archivo CSV."

    pares_validos = []
    for palabra1 in palabras:
        for palabra2 in palabras:
            if palabra1 != palabra2:
                longitud_total = len(palabra1) + len(palabra2)
                if 6 <= longitud_total <= 9:
                    pares_validos.append((palabra1, palabra2))

    if not pares_validos:
        return "Error: No se encontraron pares de palabras con la longitud adecuada."

    palabra1, palabra2 = random.choice(pares_validos)
    numeros = [str(random.randint(0, 9)) for _ in range(2)]
    
    caracteres_contrasena = list(palabra1 + palabra2) + numeros + ['.']
    random.shuffle(caracteres_contrasena)
    
    return "".join(caracteres_contrasena)

if __name__ == '__main__':
    # Ejecutamos el servidor web en modo de depuración para probarlo
    app.run(debug=True)