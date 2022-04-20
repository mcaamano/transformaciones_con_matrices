import datetime
import math
import os
import numpy as np
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image

ANCHO_CANVAS=300
ALTURA_CANVAS=300
ANCHO_DIVISIONES=50
COLOR_DIVISION_PRINCIPAL="#444444"
COLOR_DIVISION_SECUNDARIA="#aaaaaa"
FONDO_CANVAS="white"
COLOR_RECTA="black"

PIXELES = []
NUEVOS_PIXELES=[]
MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
CONTAR_TRANSFORMACIONES = 0
CONTAR_OPERACIONES = 0
DURACION_TRANS_SEGUNDOS = 0
DURACION_TRANS_MICROSEGUNDOS = 0

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

def rgb_to_hex(r,g,b):
    return ('#{:02X}{:02X}{:02X}').format(r,g,b)

def trans_xy_a_xyprima(pixel_xy):
    pixel_xy_prima = {}
    pixel_xy_prima['color'] = pixel_xy['color']
    pixel_xy_prima['x'] = int(pixel_xy['x'] - (ANCHO_CANVAS/2))
    pixel_xy_prima['y'] = int((ALTURA_CANVAS/2) - pixel_xy['y'])
    return pixel_xy_prima

def trans_xyprima_a_xy(pixel_xy_prima):
    pixel_xy = {}
    pixel_xy['color'] = pixel_xy_prima['color']
    pixel_xy['x'] = int(pixel_xy_prima['x'] + (ANCHO_CANVAS/2))
    pixel_xy['y'] = int((ALTURA_CANVAS/2) - pixel_xy_prima['y'])
    return pixel_xy

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

def dibujar_pixel(canvas, pixel_xyprima):
    pixel = trans_xyprima_a_xy(pixel_xyprima)
    x = pixel['x']
    y = pixel['y']
    color = pixel['color']
    canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline=color)

def dibujar_pixel_directo(canvas, x_prima, y_prima, color):
    x = int(x_prima + (ANCHO_CANVAS/2))
    y = int((ALTURA_CANVAS/2) - y_prima)
    canvas.create_rectangle(x, y, x+1, y+1, fill=color, outline=color)

def agregar_pixel(x_prima, y_prima, color):
    global PIXELES
    pixel_xyprima = {}
    pixel_xyprima['x'] = x_prima
    pixel_xyprima['y'] = y_prima
    pixel_xyprima['color'] = color
    # print('Pixel en ({},{}) color {}'.format(pixel_xyprima['x'],pixel_xyprima['y'], pixel_xyprima['color']))
    PIXELES.append(pixel_xyprima)

def dibujar_imagen(canvas, pixeles):
    borrar_canvas(canvas)
    dibujar_coordenadas(canvas)
    for pixel in pixeles:
        dibujar_pixel(canvas, pixel)
        # canvas.update()
    dibujar_coordenadas(canvas)

def cargar_imagen():
    global PIXELES, NUEVOS_PIXELES
    filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Seleccione Archivo BMP", filetypes=[("BMP Files","*.bmp")])
    if not filename:
        return # user cancelled; stop this method
    PIXELES = []
    NUEVOS_PIXELES = []
    im = Image.open(filename)
    width, height = im.size
    print('Width {} Height {}'.format(width, height))
    borrar_canvas(canvas_fuente)
    dibujar_coordenadas(canvas_fuente)
    for y in range(0, height):
        for x in range(0, width):
            R,G,B = im.getpixel((x,y))
            color = rgb_to_hex(R,G,B)
            # print('R[{}] G[{}] B[{}] hex[{}]'.format(R,G,B, color))
            agregar_pixel(x, height-y, color)
    dibujar_coordenadas(canvas_fuente)
    dibujar_imagen(canvas_fuente, PIXELES)


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


def ejecutar_transformacion():
    global CONTAR_OPERACIONES, NUEVOS_PIXELES, DURACION_TRANS_SEGUNDOS, DURACION_TRANS_MICROSEGUNDOS, CONTAR_TRANSFORMACIONES
    tmp_pixeles = []
    start = datetime.datetime.now()
    for pixel in NUEVOS_PIXELES:
        nuevo_pixel = {}
        nuevo_pixel['color'] = pixel['color']
        v = np.array([ pixel['x'], pixel['y'], 1 ])
        # print('pixel {}: {}'.format(pixel['id'], v))
        resultado = np.matmul(MATRIZ_TRANSFORMACION,v)
        # print('Resultado: {}'.format(resultado))
        nuevo_x = resultado[0]
        nuevo_y = resultado[1]
        # print('Transformando pixel ({},{}) a ({},{})'.format(pixel['x'], pixel['y'], nuevo_x, nuevo_y))
        nuevo_pixel['x'] = nuevo_x
        nuevo_pixel['y'] = nuevo_y
        tmp_pixeles.append(nuevo_pixel)
        CONTAR_OPERACIONES+=1
    end = datetime.datetime.now()
    delta = end - start
    DURACION_TRANS_SEGUNDOS += delta.seconds
    DURACION_TRANS_MICROSEGUNDOS += delta.microseconds
    CONTAR_TRANSFORMACIONES += 1
    NUEVOS_PIXELES = tmp_pixeles

def ejecutar_transformaciones_unidas():
    global NUEVOS_PIXELES, MATRIZ_TRANSFORMACION
    traslacion = ejectuar_traslacion.get()
    rotacion = ejectuar_rotacion.get()
    reflexion = ejecutar_reflexion.get() and (ejecutar_reflexion_x.get() or ejecutar_reflexion_y.get())
    estiramiento = ejectuar_estiramiento.get()
    distorcion = ejectuar_distorcion.get()
    NUEVOS_PIXELES = PIXELES

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
    ejecutar_transformacion()
    dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
    label_matriz1.config(text=MATRIZ_TRANSFORMACION)

def ejecutar_transformaciones_individuales():
    global NUEVOS_PIXELES, MATRIZ_TRANSFORMACION
    traslacion = ejectuar_traslacion.get()
    rotacion = ejectuar_rotacion.get()
    reflexion = ejecutar_reflexion.get() and (ejecutar_reflexion_x.get() or ejecutar_reflexion_y.get())
    estiramiento = ejectuar_estiramiento.get()
    distorcion = ejectuar_distorcion.get()
    NUEVOS_PIXELES = PIXELES

    if not traslacion and not rotacion and not reflexion and not estiramiento and not distorcion:
        print('Error no hay transformacion habilitada')
        messagebox.showerror(title='Error', message="No tiene transformaciones habilitadas")
        return

    # resetear matriz de transformacion, cada procesar_XXXXX modifica la matriz de transformacion
    print('Ejecutando Transformaciones')
    if traslacion:
        MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
        procesar_traslacion()
        ejecutar_transformacion()
        label_matriz1.config(text=MATRIZ_TRANSFORMACION)
        dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
        canvas_resultado.update_idletasks()
    if rotacion:
        MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
        procesar_rotacion()
        ejecutar_transformacion()
        label_matriz2.config(text=MATRIZ_TRANSFORMACION)
        dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
        canvas_resultado.update_idletasks()
    if reflexion:
        MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
        procesar_reflexion()
        ejecutar_transformacion()
        label_matriz3.config(text=MATRIZ_TRANSFORMACION)
        dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
        canvas_resultado.update_idletasks()
    if estiramiento:
        MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
        procesar_estiramiento()
        ejecutar_transformacion()
        label_matriz4.config(text=MATRIZ_TRANSFORMACION)
        dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
        canvas_resultado.update_idletasks()
    if distorcion:
        MATRIZ_TRANSFORMACION = np.array([ [1,0,0], [0,1,0], [0,0,1] ])
        procesar_distorcion()
        ejecutar_transformacion()
        label_matriz5.config(text=MATRIZ_TRANSFORMACION)
        dibujar_imagen(canvas_resultado, NUEVOS_PIXELES)
        canvas_resultado.update_idletasks()


def ejecutar_transformaciones():
    global CONTAR_OPERACIONES, DURACION_TRANS_SEGUNDOS, DURACION_TRANS_MICROSEGUNDOS, CONTAR_TRANSFORMACIONES
    CONTAR_OPERACIONES = 0
    CONTAR_TRANSFORMACIONES = 0
    DURACION_TRANS_SEGUNDOS = 0
    DURACION_TRANS_MICROSEGUNDOS = 0

    label_matriz1.config(text=' ')
    label_matriz2.config(text=' ')
    label_matriz3.config(text=' ')
    label_matriz4.config(text=' ')
    label_matriz5.config(text=' ')
    label_estadisticas.config(text=' ')

    if transformaciones_individuales.get():
        frame_matriz.config(text="Matrices de Transformación: ")
        ejecutar_transformaciones_individuales()
    else:
        frame_matriz.config(text="Matriz de Transformación: ")
        ejecutar_transformaciones_unidas()
    print('Se transformaron {} pixeles en {} transformaciones. Tiempo de ejecucion {} segundos {} microsegundos'.format(CONTAR_OPERACIONES, CONTAR_TRANSFORMACIONES, DURACION_TRANS_SEGUNDOS, DURACION_TRANS_MICROSEGUNDOS))
    label_estadisticas.config(text='Se transformaron {} pixeles en {} transformaciones. Tiempo de ejecucion {} segundos {} microsegundos'.format(CONTAR_OPERACIONES, CONTAR_TRANSFORMACIONES, DURACION_TRANS_SEGUNDOS, DURACION_TRANS_MICROSEGUNDOS))


raiz = Tk()
raiz.title('Transformación de Imagenes 2D con Matrices')
raiz.iconbitmap('brick.ico')
raiz.geometry("850x550")

frame_fuente = LabelFrame(raiz, padx=5, pady=5, text="Fuente: ")
frame_fuente.grid(row=0, column=0)

canvas_fuente = Canvas(frame_fuente, width=ANCHO_CANVAS, height=ALTURA_CANVAS, bg="white")
canvas_fuente.grid(row=0, column=0)

btn_capturar = Button(frame_fuente, text="Cargar Imagen", command=cargar_imagen)
btn_capturar.grid(row=1, column=0)

frame_trans = LabelFrame(raiz, padx=5, pady=5, text="Transformaciones: ")
frame_trans.grid(row=0, column=1)

frame_resultado = LabelFrame(raiz, padx=5, pady=5, text="Resultado: ")
frame_resultado.grid(row=0, column=2)

canvas_resultado = Canvas(frame_resultado, width=ANCHO_CANVAS, height=ALTURA_CANVAS, bg="white")
canvas_resultado.grid(row=0, column=0)

frame_matriz = LabelFrame(raiz, padx=5, pady=5, text="Matriz de Transformación: ")
frame_matriz.grid(row=1, column=0, columnspan=3)

label_matriz1 = Label(frame_matriz, text=" ")
label_matriz1.grid(row=0, column=0)
label_matriz2 = Label(frame_matriz, text=" ")
label_matriz2.grid(row=0, column=1)
label_matriz3 = Label(frame_matriz, text=" ")
label_matriz3.grid(row=0, column=2)
label_matriz4 = Label(frame_matriz, text=" ")
label_matriz4.grid(row=0, column=3)
label_matriz5 = Label(frame_matriz, text=" ")
label_matriz5.grid(row=0, column=4)

frame_estadisticas = LabelFrame(raiz, padx=5, pady=5, text="Estadisticas: ")
frame_estadisticas.grid(row=2, column=0, columnspan=3)
label_estadisticas = Label(frame_estadisticas, text=" ")
label_estadisticas.grid(row=0, column=0)

ejectuar_traslacion = BooleanVar()
ejectuar_rotacion = BooleanVar()
ejecutar_reflexion = BooleanVar()
ejecutar_reflexion_x = BooleanVar()
ejecutar_reflexion_y = BooleanVar()
ejectuar_estiramiento = BooleanVar()
ejectuar_distorcion = BooleanVar()
transformaciones_individuales = BooleanVar()

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


# Transformaciones Individuales
trans_ind_distorcion = Checkbutton(frame_trans, variable=transformaciones_individuales, onvalue=True, offvalue=False)
trans_ind_distorcion.deselect()
trans_ind_distorcion.grid(row=10, column=0)
label_distorcion = Label(frame_trans, text="Transformaciones Individuales")
label_distorcion.grid(row=10, column=1, columnspan=4)



# Boton de ejecucion
btn_ejecutar_transformacion = Button(frame_trans, text="Ejecutar Transformación", command=ejecutar_transformaciones)
btn_ejecutar_transformacion.grid(row=11, column=0, columnspan=5, pady=10)

borrar_canvas(canvas_fuente)
dibujar_coordenadas(canvas_fuente)

borrar_canvas(canvas_resultado)
dibujar_coordenadas(canvas_resultado)





# main event loop
raiz.mainloop()