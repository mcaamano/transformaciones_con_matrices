import numpy as np
import math
from tkinter import *
from tkinter import messagebox

ANCHO_CANVAS=300
ALTURA_CANVAS=300
ANCHO_DIVISIONES=50
COLOR_DIVISION_PRINCIPAL="#444444"
COLOR_DIVISION_SECUNDARIA="#aaaaaa"
FONDO_CANVAS="white"
COLOR_RECTA="black"
DELTA_VERTICE=3
LETRA_VERTICE='A'
COLORES_VERTICES=['red', 'blue', 'gold', 'brown', 'orange', 'cyan', 'purple', 'magenta', 'grey']
COLOR_POLIGONO='green'

CAPTURAR_POLIGONO=False

ULTIMO_X=None
ULTIMO_Y=None
VERTICES=[]
NUEVOS_VERTICES=[]
MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])

#
# El Canvas de Tkinter es orientado con el eje Y invertido:
# - el punto (0,0) es la esquina superior izquierda del canvas
# - el punto (ANCHO_CANVAS, ALTURA_CANVAS) es la esquina inferior derecha
#
#  
# (0,0)┌─────────────────►x
#      │                 ANCHO_CANVAS
#      │
#      │
#      │
#      │
#      ▼ ALTURA_CANVAS
#      y
#
# Normalmente se espera un plano con el punto (0,0) ubicado en el centro
# del canvas:
# 
#                       y
#                       ▲(ALTURA_CANVAS/2)
#                       │
#                       │
#                       │
#                       │
#                       │(0,0)
#      ◄────────────────┼────────────────────►x
# -(ANCHO_CANVAS/2)     │                   (ANCHO_CANVAS/2)
#                       │
#                       │
#                       │
#                       │
#                       ▼-(ALTURA_CANVAS/2)
#
# Para efecto de tener mejor visualizacion procedemos a montar un sistema coordenado
# centrado en el punto medio del canvas (x',y'), por lo que la coversion es:
# x' = x - (ANCHO_CANVAS/2)
# y' = (ALTURA_CANVAS/2) - y
#
# y el inverso
# x = x' + (ANCHO_CANVAS/2)
# y = (ALTURA_CANVAS/2) - y'
#
# Los puntos de los vertices se almacenan en el sistema (x',y') para mostrar los puntos
# al usuario, pero a la hora de dibujar los vertices y poligonos se convierten a (x,y)
#

def trans_xy_a_xyprima(vertice_xy):
    vertice_xy_prima = {}
    vertice_xy_prima['id'] = vertice_xy['id']
    vertice_xy_prima['color'] = vertice_xy['color']
    vertice_xy_prima['x'] = int(vertice_xy['x'] - (ANCHO_CANVAS/2))
    vertice_xy_prima['y'] = int((ALTURA_CANVAS/2) - vertice_xy['y'])
    return vertice_xy_prima

def trans_xyprima_a_xy(vertice_xy_prima):
    vertice_xy = {}
    vertice_xy['id'] = vertice_xy_prima['id']
    vertice_xy['color'] = vertice_xy_prima['color']
    vertice_xy['x'] = int(vertice_xy_prima['x'] + (ANCHO_CANVAS/2))
    vertice_xy['y'] = int((ALTURA_CANVAS/2) - vertice_xy_prima['y'])
    return vertice_xy

def incrementar_letra_vertice():
    global LETRA_VERTICE
    LETRA_VERTICE = chr(ord(LETRA_VERTICE)+1)

def borrar_canvas(canvas):
    canvas.create_rectangle(0, 0, ANCHO_CANVAS+1, ALTURA_CANVAS+1, fill=FONDO_CANVAS, outline=FONDO_CANVAS)

def dibujar_coordenadas(canvas):
    num_div_horizontales = int(ANCHO_CANVAS / ANCHO_DIVISIONES)
    for i in range(0, num_div_horizontales):
        x_offset = i*ANCHO_DIVISIONES
        canvas.create_line(x_offset, 0, x_offset, ALTURA_CANVAS, dash=(4,2), fill=COLOR_DIVISION_SECUNDARIA)
    num_div_verticales = int(ALTURA_CANVAS / ANCHO_DIVISIONES)
    for i in range(0, num_div_verticales):
        y_offset = i*ANCHO_DIVISIONES
        canvas.create_line(0, y_offset, ANCHO_CANVAS, y_offset, dash=(4,2), fill=COLOR_DIVISION_SECUNDARIA)
    canvas.create_line((ANCHO_CANVAS/2), 0, (ANCHO_CANVAS/2), ALTURA_CANVAS, fill=COLOR_DIVISION_PRINCIPAL)
    canvas.create_line(0, (ALTURA_CANVAS/2), ANCHO_CANVAS, (ALTURA_CANVAS/2), fill=COLOR_DIVISION_PRINCIPAL)

def dibujar_poligono(canvas, vertices):
    # print('[dibujar_poligono]')
    borrar_canvas(canvas)
    puntos=[]
    for vertice_xyprima in vertices:
        # print('Vertice {} en ({},{})'.format(vertice_xyprima['id'], vertice_xyprima['x'], vertice_xyprima['y']))
        vertice_xy = trans_xyprima_a_xy(vertice_xyprima)
        puntos.append(vertice_xy['x'])
        puntos.append(vertice_xy['y'])
    # print('Numero de vertices: {}'.format(len(vertice_xy)))
    if len(vertices) >= 3:
        canvas.create_polygon(puntos, fill=COLOR_POLIGONO, outline=COLOR_POLIGONO)
    else:
        print('ERROR: No hay suficientes vertices para un poligono')
        return
    for vertice_xyprima in vertices:
        vertice_xy = trans_xyprima_a_xy(vertice_xyprima)
        x = vertice_xy['x']
        y = vertice_xy['y']
        color = vertice_xy['color']
        canvas.create_rectangle(x-DELTA_VERTICE, y-DELTA_VERTICE, x+DELTA_VERTICE, y+DELTA_VERTICE, fill=color, outline=color)
    dibujar_coordenadas(canvas)

def dibujar_vertice(vertice_xyprima):
    global ULTIMO_X, ULTIMO_Y, VERTICES
    vertice = trans_xyprima_a_xy(vertice_xyprima)
    x = vertice['x']
    y = vertice['y']
    color = vertice['color']
    if ULTIMO_X and ULTIMO_Y:
        # tenemos un vertice anterior, dibujemos recta antes del nuevo vertice
        canvas_fuente.create_line(ULTIMO_X, ULTIMO_Y, x, y, fill=COLOR_RECTA)
    canvas_fuente.create_rectangle(x-DELTA_VERTICE, y-DELTA_VERTICE, x+DELTA_VERTICE, y+DELTA_VERTICE, fill=color, outline=color)
    ULTIMO_X = x
    ULTIMO_Y = y

def capturar_vertice(event):
    global VERTICES
    vertice = {}
    vertice['x'] = event.x
    vertice['y'] = event.y
    vertice['id'] = LETRA_VERTICE
    vertice['color'] = COLORES_VERTICES[ len(VERTICES) % len(COLORES_VERTICES)]
    vertice_xyprima = trans_xy_a_xyprima(vertice)
    print('Vertice {} en ({},{})'.format(vertice_xyprima['id'], vertice_xyprima['x'],vertice_xyprima['y']))
    VERTICES.append(vertice_xyprima)
    incrementar_letra_vertice()
    dibujar_vertice(vertice_xyprima)

def agregar_verticeprima(x_prima, y_prima):
    global VERTICES
    vertice_xyprima = {}
    vertice_xyprima['x'] = x_prima
    vertice_xyprima['y'] = y_prima
    vertice_xyprima['id'] = LETRA_VERTICE
    vertice_xyprima['color'] = COLORES_VERTICES[ len(VERTICES) % len(COLORES_VERTICES)]
    print('Vertice {} en ({},{})'.format(vertice_xyprima['id'], vertice_xyprima['x'],vertice_xyprima['y']))
    VERTICES.append(vertice_xyprima)
    incrementar_letra_vertice()
    dibujar_vertice(vertice_xyprima)


def capturar():
    global CAPTURAR_POLIGONO, ULTIMO_X, ULTIMO_Y, VERTICES, LETRA_VERTICE
    if CAPTURAR_POLIGONO:
        print('Terminando Captura de Poligono')
        CAPTURAR_POLIGONO = False
        canvas_fuente.unbind("<Button-1>")
        btn_capturar.config(text="Capturar Polígono")
        dibujar_poligono(canvas_fuente, VERTICES)
    else:
        print('Iniciando Captura de Poligono')
        CAPTURAR_POLIGONO = True
        borrar_canvas(canvas_fuente)
        dibujar_coordenadas(canvas_fuente)
        ULTIMO_X = None
        ULTIMO_Y = None
        VERTICES=[]
        LETRA_VERTICE='A'
        canvas_fuente.bind("<Button-1>", capturar_vertice)
        btn_capturar.config(text="Terminar Captura")

def habilitar_traslacion():
    if ejectuar_traslacion.get():
        print('Traslacion Habilitada')
        entry_traslacion_x.config(state='normal')
        entry_traslacion_y.config(state='normal')
        entry_traslacion_x.insert(0,"0")
        entry_traslacion_y.insert(0,"0")
    else:
        print('Traslacion Deshabilitada')
        entry_traslacion_x.delete(0,"end")
        entry_traslacion_y.delete(0,"end")
        entry_traslacion_x.config(state='disabled')
        entry_traslacion_y.config(state='disabled')

def habilitar_rotacion():
    if ejectuar_rotacion.get():
        print('Rotacion Habilitada')
        entry_rotacion_angulo.config(state='normal')
        entry_rotacion_angulo.insert(0,"0")
    else:
        print('Rotacion Deshabilitada')
        entry_rotacion_angulo.delete(0,"end")
        entry_rotacion_angulo.config(state='disabled')

def habilitar_reflexion():
    if ejecutar_reflexion.get():
        print('Reflexión Habilitada')
        chk_box_reflexion_x.config(state='normal')
        chk_box_reflexion_y.config(state='normal')
    else:
        print('Reflexión Deshabilitada')
        chk_box_reflexion_x.deselect()
        chk_box_reflexion_y.deselect()
        chk_box_reflexion_x.config(state='disabled')
        chk_box_reflexion_y.config(state='disabled')

def habilitar_estiramiento():
    if ejectuar_estiramiento.get():
        print('Estiramiento Habilitado')
        entry_estiramiento_x.config(state='normal')
        entry_estiramiento_y.config(state='normal')
        entry_estiramiento_x.insert(0,"1")
        entry_estiramiento_y.insert(0,"1")
    else:
        print('Estiramiento Deshabilitado')
        entry_estiramiento_x.delete(0,"end")
        entry_estiramiento_y.delete(0,"end")
        entry_estiramiento_x.config(state='disabled')
        entry_estiramiento_y.config(state='disabled')

def habilitar_distorcion():
    if ejectuar_distorcion.get():
        print('Distorcion Habilitado')
        entry_distorcion_x.config(state='normal')
        entry_distorcion_y.config(state='normal')
        entry_distorcion_x.insert(0,"0")
        entry_distorcion_y.insert(0,"0")
    else:
        print('Estiramiento Deshabilitado')
        entry_distorcion_x.delete(0,"end")
        entry_distorcion_y.delete(0,"end")
        entry_distorcion_x.config(state='disabled')
        entry_distorcion_y.config(state='disabled')


def procesar_traslacion():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    print('-'*50)
    print('Procesando Traslacion')
    # validar x, y
    try:
        delta_x = int(entry_traslacion_x.get())
        delta_y = int(entry_traslacion_y.get())
    except ValueError:
        print('Error valores invalidos para traslacion')
        messagebox.showerror(title='Error', message="Valores Invalidos para traslacion")
        return
    T = np.array([ [1, 0, delta_x], [0, 1, delta_y], [0, 0, 1] ])
    print('Matriz de Traslacion T:')
    print(T)
    MATRIZ_TRANSFORMACION = np.matmul(T, MATRIZ_TRANSFORMACION)
    print('Matriz de Transformacion:')
    print(MATRIZ_TRANSFORMACION)
    print('-'*50)
    print('')

def procesar_rotacion():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    print('-'*50)
    print('Procesando Rotacion')
    # validar angulo
    try:
        angulo = int(entry_rotacion_angulo.get())
    except ValueError:
        print('Error valores invalidos para rotacion')
        messagebox.showerror(title='Error', message="Valor de ángulo invalido para rotación")
        return
    radianes = math.radians(angulo)
    R = np.array([[ math.cos(radianes), -math.sin(radianes), 0 ],[ math.sin(radianes), math.cos(radianes), 0], [0,0,1]])
    print('Matriz de Rotacion R:')
    print(R)
    MATRIZ_TRANSFORMACION = np.matmul(R, MATRIZ_TRANSFORMACION)
    print('Matriz de Transformacion:')
    print(MATRIZ_TRANSFORMACION)
    print('-'*50)
    print('')

def procesar_reflexion():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    print('-'*50)
    print('Procesando Reflexion')
    if ejecutar_reflexion_x.get():
        # Reflexion en eje X
        R = np.array([[ 1,0,0],[0,-1,0],[0,0,1]])
        print('Matriz de Reflexión en x R:')
        print(R)
        MATRIZ_TRANSFORMACION = np.matmul(R, MATRIZ_TRANSFORMACION)
        print('Matriz de Transformacion:')
        print(MATRIZ_TRANSFORMACION)
    if ejecutar_reflexion_y.get():
        # Reflexion en eje y
        R = np.array([[ -1,0,0],[0,1,0],[0,0,1]])
        print('Matriz de Reflexión en y R:')
        print(R)
        MATRIZ_TRANSFORMACION = np.matmul(R, MATRIZ_TRANSFORMACION)
        print('Matriz de Transformacion:')
        print(MATRIZ_TRANSFORMACION)
    print('-'*50)
    print('')

def procesar_estiramiento():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    print('-'*50)
    print('Procesando Estiramiento')
    # validar x, y
    try:
        delta_x = float(entry_estiramiento_x.get())
        delta_y = float(entry_estiramiento_y.get())
    except ValueError:
        print('Error valores invalidos para estiramiento')
        messagebox.showerror(title='Error', message="Valores Invalidos para estiramiento")
        return
    E = np.array([ [delta_x, 0, 0], [0, delta_y, 0], [0, 0, 1] ])
    print('Estiramiento Matrix E:')
    print(E)
    MATRIZ_TRANSFORMACION = np.matmul(E, MATRIZ_TRANSFORMACION)
    print('Matriz de Transformacion:')
    print(MATRIZ_TRANSFORMACION)
    print('-'*50)
    print('')

def procesar_distorcion():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    print('-'*50)
    print('Procesando Distorcion')
    # validar x, y
    try:
        delta_x = float(entry_distorcion_x.get())
        delta_y = float(entry_distorcion_y.get())
    except ValueError:
        print('Error valores invalidos para Distorcion')
        messagebox.showerror(title='Error', message="Valores Invalidos para Distorcion")
        return
    D = np.array([ [1, delta_x, 0], [delta_y, 1, 0], [0, 0, 1] ])
    print('Distorcion Matrix D:')
    print(D)
    MATRIZ_TRANSFORMACION = np.matmul(D, MATRIZ_TRANSFORMACION)
    print('Matriz de Transformacion:')
    print(MATRIZ_TRANSFORMACION)
    print('-'*50)
    print('')


def ejecutar_transformaciones():
    global NUEVOS_VERTICES, MATRIZ_TRANSFORMACION
    traslacion = ejectuar_traslacion.get()
    rotacion = ejectuar_rotacion.get()
    reflexion = ejecutar_reflexion.get() and (ejecutar_reflexion_x.get() or ejecutar_reflexion_y.get())
    estiramiento = ejectuar_estiramiento.get()
    distorcion = ejectuar_distorcion.get()
    NUEVOS_VERTICES = VERTICES

    if not traslacion and not rotacion and not reflexion and not estiramiento and not distorcion:
        print('Error no hay transformacion habilitada')
        messagebox.showerror(title='Error', message="No tiene transformaciones habilitadas")
        return
    # resetear matriz de transformacion, cada procesar_XXXXX modifica la matriz de transformacion
    MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
    print('Ejecutando Transformaciones')
    if traslacion:
        procesar_traslacion()
    if rotacion:
        procesar_rotacion()
    if reflexion:
        procesar_reflexion()
    if estiramiento:
        procesar_estiramiento()
    if distorcion:
        procesar_distorcion()
    print('='*50)
    print('Matriz de Transformacion:')
    print(MATRIZ_TRANSFORMACION)
    print('='*50)
    label_matriz.config(text=MATRIZ_TRANSFORMACION)
    tmp_vertices = []
    for vertice in NUEVOS_VERTICES:
        nuevo_vertice = {}
        nuevo_vertice['id'] = vertice['id']
        nuevo_vertice['color'] = vertice['color']
        v = np.array([ vertice['x'], vertice['y'], 1 ])
        # print('Vertice {}: {}'.format(vertice['id'], v))
        resultado = np.matmul(MATRIZ_TRANSFORMACION,v)
        # print('Resultado: {}'.format(resultado))
        nuevo_x = resultado[0]
        nuevo_y = resultado[1]
        print('Transformando vertice {} ({},{}) a ({},{})'.format(vertice['id'], vertice['x'], vertice['y'], nuevo_x, nuevo_y))
        nuevo_vertice['x'] = nuevo_x
        nuevo_vertice['y'] = nuevo_y
        tmp_vertices.append(nuevo_vertice)
    NUEVOS_VERTICES = tmp_vertices
    dibujar_poligono(canvas_resultado, NUEVOS_VERTICES)


# ===================================================================================================
# Bloque Principal
# ===================================================================================================
raiz = Tk()
raiz.title('Transformación de Polígonos con Matrices')
raiz.iconbitmap('brick.ico')
raiz.geometry("850x550")

frame_fuente = LabelFrame(raiz, padx=5, pady=5, text="Fuente: ")
frame_fuente.grid(row=0, column=0)

canvas_fuente = Canvas(frame_fuente, width=ANCHO_CANVAS, height=ALTURA_CANVAS, bg="white")
canvas_fuente.grid(row=0, column=0)

btn_capturar = Button(frame_fuente, text="Capturar Polígono", command=capturar)
btn_capturar.grid(row=1, column=0)

frame_trans = LabelFrame(raiz, padx=5, pady=5, text="Transformaciones: ")
frame_trans.grid(row=0, column=1)

frame_resultado = LabelFrame(raiz, padx=5, pady=5, text="Resultado: ")
frame_resultado.grid(row=0, column=2)

canvas_resultado = Canvas(frame_resultado, width=ANCHO_CANVAS, height=ALTURA_CANVAS, bg="white")
canvas_resultado.grid(row=0, column=0)

frame_matriz = LabelFrame(raiz, padx=5, pady=5, text="Matriz de Transformación: ")
frame_matriz.grid(row=1, column=0, columnspan=3)

label_matriz = Label(frame_matriz, text=" ")
label_matriz.grid(row=0, column=0)

ejectuar_traslacion = BooleanVar()
ejectuar_rotacion = BooleanVar()
ejecutar_reflexion = BooleanVar()
ejecutar_reflexion_x = BooleanVar()
ejecutar_reflexion_y = BooleanVar()
ejectuar_estiramiento = BooleanVar()
ejectuar_distorcion = BooleanVar()

# Traslacion
chk_box_traslacion = Checkbutton(frame_trans, variable=ejectuar_traslacion, onvalue=True, offvalue=False, command=habilitar_traslacion)
chk_box_traslacion.deselect()
chk_box_traslacion.grid(row=0, column=0)
label_traslacion = Label(frame_trans, text="Ejecutar Traslación")
label_traslacion.grid(row=0, column=1, columnspan=4)

label_traslacion_x = Label(frame_trans, text="X:")
label_traslacion_x.grid(row=1, column=1)
entry_traslacion_x = Entry(frame_trans, width=4, state='disabled')
entry_traslacion_x.grid(row=1, column=2)

label_traslacion_y = Label(frame_trans, text="Y:")
label_traslacion_y.grid(row=1, column=3)
entry_traslacion_y = Entry(frame_trans, width=4, state='disabled')
entry_traslacion_y.grid(row=1, column=4)


# Rotacion
chk_box_rotar = Checkbutton(frame_trans, variable=ejectuar_rotacion, onvalue=True, offvalue=False, command=habilitar_rotacion)
chk_box_rotar.deselect()
chk_box_rotar.grid(row=2, column=0)
label_rotacion = Label(frame_trans, text="Ejecutar Rotación")
label_rotacion.grid(row=2, column=1, columnspan=4)

label_rotacion_angulo = Label(frame_trans, text="ángulo:")
label_rotacion_angulo.grid(row=3, column=1)
entry_rotacion_angulo = Entry(frame_trans, width=4, state='disabled')
entry_rotacion_angulo.grid(row=3, column=2, columnspan=3)


# Reflexion
chk_box_reflexion = Checkbutton(frame_trans, variable=ejecutar_reflexion, onvalue=True, offvalue=False, command=habilitar_reflexion)
chk_box_reflexion.deselect()
chk_box_reflexion.grid(row=4, column=0)
label_reflexion = Label(frame_trans, text="Ejecutar Reflexión")
label_reflexion.grid(row=4, column=1, columnspan=4)

label_reflexion_x = Label(frame_trans, text="X:")
label_reflexion_x.grid(row=5, column=1)
chk_box_reflexion_x = Checkbutton(frame_trans, variable=ejecutar_reflexion_x, onvalue=True, offvalue=False, state='disabled')
chk_box_reflexion_x.deselect()
chk_box_reflexion_x.grid(row=5, column=2)

label_reflexion_y = Label(frame_trans, text="Y:")
label_reflexion_y.grid(row=5, column=3)
chk_box_reflexion_y = Checkbutton(frame_trans, variable=ejecutar_reflexion_y, onvalue=True, offvalue=False, state='disabled')
chk_box_reflexion_y.deselect()
chk_box_reflexion_y.grid(row=5, column=4)


# Estiramiento
chk_box_estiramiento = Checkbutton(frame_trans, variable=ejectuar_estiramiento, onvalue=True, offvalue=False, command=habilitar_estiramiento)
chk_box_estiramiento.deselect()
chk_box_estiramiento.grid(row=6, column=0)
label_estiramiento = Label(frame_trans, text="Ejecutar Estiramiento")
label_estiramiento.grid(row=6, column=1, columnspan=4)

label_estiramiento_x = Label(frame_trans, text="X:")
label_estiramiento_x.grid(row=7, column=1)
entry_estiramiento_x = Entry(frame_trans, width=4, state='disabled')
entry_estiramiento_x.grid(row=7, column=2)

label_estiramiento_y = Label(frame_trans, text="Y:")
label_estiramiento_y.grid(row=7, column=3)
entry_estiramiento_y = Entry(frame_trans, width=4, state='disabled')
entry_estiramiento_y.grid(row=7, column=4)


# Distorcion
chk_box_distorcion = Checkbutton(frame_trans, variable=ejectuar_distorcion, onvalue=True, offvalue=False, command=habilitar_distorcion)
chk_box_distorcion.deselect()
chk_box_distorcion.grid(row=8, column=0)
label_distorcion = Label(frame_trans, text="Ejecutar Distorción")
label_distorcion.grid(row=8, column=1, columnspan=4)

label_distorcion_x = Label(frame_trans, text="X:")
label_distorcion_x.grid(row=9, column=1)
entry_distorcion_x = Entry(frame_trans, width=4, state='disabled')
entry_distorcion_x.grid(row=9, column=2)

label_distorcion_y = Label(frame_trans, text="Y:")
label_distorcion_y.grid(row=9, column=3)
entry_distorcion_y = Entry(frame_trans, width=4, state='disabled')
entry_distorcion_y.grid(row=9, column=4)



# Boton de ejecucion
btn_ejecutar_transformacion = Button(frame_trans, text="Ejecutar Transformación", command=ejecutar_transformaciones)
btn_ejecutar_transformacion.grid(row=10, column=0, columnspan=5, pady=10)

borrar_canvas(canvas_fuente)
dibujar_coordenadas(canvas_fuente)

borrar_canvas(canvas_resultado)
dibujar_coordenadas(canvas_resultado)


# agregar unos vertices iniciales
# agregar_verticeprima(0,0)
# agregar_verticeprima(50,0)
# agregar_verticeprima(50,50)
# agregar_verticeprima(0,50)
# dibujar_poligono(canvas_fuente, VERTICES)

# main event loop
raiz.mainloop()
