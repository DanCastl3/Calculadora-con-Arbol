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

# Definir primero el token de número decimal
def t_NUMERO_DECIMAL(t):
    r'\d+\.\d+'  # Coincide con números como 123.456
    t.value = float(t.value)  # Convertir el valor a float
    return t

# Luego definir el token de número entero
def t_NUMERO_ENTERO(t):
    r'\d+'  # Coincide con números enteros como 123
    t.value = int(t.value)  # Convertir el valor a int
    return t

# Ignorar espacios y tabs
t_ignore = ' \t'

# Manejar errores
def t_error(t):
    print(f"Carácter ilegal {t.value[0]}")
    t.lexer.skip(1)

# Construir el lexer
lexer = lex.lex()


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
        p[0] = p[1] / p[3]  # En la división siempre se devuelve un decimal

    # Verificar si algún número es decimal y asegurarse de devolver float en esos casos
    if isinstance(p[1], float) or isinstance(p[3], float):
        p[0] = float(p[0])  # Convertir el resultado a decimal si algún operando es decimal

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

# Ruta para  la expresión
@app.route('/calcular', methods=['POST'])
def calcular():
    data = request.json
    expresion = data['expresion'].replace(' ', '')  

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

    try:
        resultado = parser.parse(expresion)

        session['tokens'] = tokens
        return jsonify({"resultado": resultado, "tokens": tokens})
    except Exception as e:
        return jsonify({"error": str(e), "tokens": tokens})

@app.route('/nueva_pagina')
def nueva_pagina():
    tokens = session.get('tokens', [])
    return render_template('nueva_pagina.html', tokens=tokens)

if __name__ == '__main__':
    app.run(debug=True)
