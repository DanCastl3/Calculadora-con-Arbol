import ply.lex as lex
import ply.yacc as yacc
from flask import Flask, render_template, request, jsonify, session

# Configurar la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'  # Necesaria para utilizar sesiones

# Definimos los tokens
tokens = (
    'NUMERO_ENTERO', 'NUMERO_DECIMAL', 'SUMA', 'RESTA', 'MULTIPLICACION', 'DIVISION', 
    'PARENTESIS_IZQUIERDO', 'PARENTESIS_DERECHO'
)

# Reglas para los tokens
t_SUMA = r'\+'
t_RESTA = r'-'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'
t_PARENTESIS_IZQUIERDO = r'\('
t_PARENTESIS_DERECHO = r'\)'

# Definimos cómo identificar los números enteros
def t_NUMERO_ENTERO(t):
    r'\d+'  # Un número entero es una o más cifras
    t.value = int(t.value)  # Convertir el valor a int
    return t

# Definimos cómo identificar los números decimales
def t_NUMERO_DECIMAL(t):
    r'\d+\.\d+'  # Un número decimal es dígitos seguidos de un punto y más dígitos
    t.value = float(t.value)  # Convertir el valor a float
    return t

# Ignorar espacios en blanco
t_ignore = ' \t'

# Manejo de errores léxicos
def t_error(t):
    print(f"Carácter ilegal {t.value[0]}")
    t.lexer.skip(1)

# Construimos el lexer
lexer = lex.lex()

# Definimos la gramática para el parser
def p_expresion_binop(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    elif p[2] == '-':
        p[0] = p[1] - p[3]
    elif p[2] == '*':
        p[0] = p[1] * p[3]
    elif p[2] == '/':
        if p[3] == 0:
            raise ZeroDivisionError("División por cero.")
        p[0] = p[1] / p[3]

def p_expresion_par(p):
    'expresion : PARENTESIS_IZQUIERDO expresion PARENTESIS_DERECHO'
    p[0] = p[2]

def p_expresion_numero(p):
    '''expresion : NUMERO_ENTERO
                 | NUMERO_DECIMAL'''
    p[0] = p[1]

# Definir la precedencia de operadores
precedence = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
    ('nonassoc', 'PARENTESIS_IZQUIERDO', 'PARENTESIS_DERECHO'),
)

def p_error(p):
    print("Error de sintaxis.")

# Construimos el parser
parser = yacc.yacc()

# Ruta para la página principal
@app.route('/')
def index():
    return render_template('index.html')

# Ruta para procesar la expresión
@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    expresion = data['expresion'].replace(' ', '')  # Eliminar espacios en blanco para procesar correctamente

    # Limpiamos los tokens antes de procesar
    lexer.input(expresion)
    tokens = []
    
    while True:
        tok = lexer.token()
        if not tok:
            break  # No hay más tokens
        token_tipo = {
            'NUMERO_ENTERO': 'Número entero',
            'NUMERO_DECIMAL': 'Número decimal',
            'SUMA': 'Suma',
            'RESTA': 'Resta',
            'MULTIPLICACION': 'Multiplicación',
            'DIVISION': 'División',
            'PARENTESIS_IZQUIERDO': 'Paréntesis izquierdo',
            'PARENTESIS_DERECHO': 'Paréntesis derecho'
        }
        tokens.append({"valor": tok.value, "tipo": token_tipo.get(tok.type, tok.type)})

    # Evaluar la expresión y obtener el resultado
    try:
        resultado = parser.parse(expresion)

        # Almacenar tokens en la sesión
        session['tokens'] = tokens
        return jsonify({"resultado": resultado, "tokens": tokens})
    except Exception as e:
        return jsonify({"error": str(e), "tokens": tokens})

# Nueva ruta para redirigir a la nueva página en blanco
@app.route('/nueva_pagina')
def nueva_pagina():
    tokens = session.get('tokens', [])
    return render_template('nueva_pagina.html', tokens=tokens)

# Ejecutar la aplicación
if __name__ == '__main__':
    app.run(debug=True)
