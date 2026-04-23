import pyttsx3
import sounddevice as sd
import speech_recognition as sr
from groq import Groq
import re
import tkinter as tk
import threading

client = Groq(api_key="SECRETO")

# Variables de animacion
hablando = False

def hablar(texto):
    global hablando
    texto = re.sub(r'\*+', '', texto)
    texto = re.sub(r'#+', '', texto)
    texto = re.sub(r'\d+\.', '', texto)
    texto = texto.strip()
    print("Yarvis:", texto)
    hablando = True
    engine = pyttsx3.init()
    engine.say(texto)
    engine.runAndWait()
    engine.stop()
    hablando = False

def escuchar():
    r = sr.Recognizer()
    print("Escuchando...")
    frecuencia = 16000
    duracion = 6
    grabacion = sd.rec(int(duracion * frecuencia), samplerate=frecuencia, channels=1, dtype='int16')
    sd.wait()
    audio = sr.AudioData(grabacion.tobytes(), frecuencia, 2)
    try:
        texto = r.recognize_google(audio, language="es-ES")
        print("Tu dijiste:", texto)
        return texto
    except:
        hablar("No te entendi, repite por favor.")
        return ""

def responder(texto):
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Yarvis, un asistente virtual inteligente. Responde en español, de forma breve, clara y sin usar simbolos ni listas con asteriscos."},
            {"role": "user", "content": texto}
        ]
    )
    return respuesta.choices[0].message.content

def loop_yarvis():
    hablar("Hola Juan, soy Yarvis. En que te puedo ayudar?")
    while True:
        comando = escuchar()
        if comando:
            if "adios" in comando.lower() or "adiós" in comando.lower() or "chao" in comando.lower() or "salir" in comando.lower() or "hasta luego" in comando.lower():
                hablar("Hasta luego Juan, fue un placer ayudarte.")
                ventana.quit()
                break
            respuesta = responder(comando)
            hablar(respuesta)

# Interfaz visual
ventana = tk.Tk()
ventana.title("Yarvis")
ventana.configure(bg="black")
ventana.geometry("400x400")

canvas = tk.Canvas(ventana, width=400, height=400, bg="black", highlightthickness=0)
canvas.pack()

radio = 80
cx, cy = 200, 200
incremento = 1

def animar():
    global radio, incremento
    canvas.delete("all")

    # Circulos de fondo
    for i in range(4, 0, -1):
        opacidad = i * 20
        canvas.create_oval(
            cx - radio - i*20, cy - radio - i*20,
            cx + radio + i*20, cy + radio + i*20,
            outline=f"#00{opacidad:02x}ff", width=1
        )

    # Circulo principal
    if hablando:
        color = "#00aaff"
        canvas.create_oval(cx-radio, cy-radio, cx+radio, cy+radio, fill=color, outline="#00ffff", width=3)
        radio += incremento
        if radio > 100 or radio < 80:
            incremento *= -1
    else:
        canvas.create_oval(cx-80, cy-80, cx+80, cy+80, fill="#003366", outline="#0055aa", width=2)
        radio = 80

    # Texto
    canvas.create_text(cx, cy, text="YARVIS", fill="#00ffff", font=("Arial", 18, "bold"))

    ventana.after(50, animar)

# Iniciar Yarvis en hilo separado
hilo = threading.Thread(target=loop_yarvis, daemon=True)
hilo.start()

animar()
ventana.mainloop()