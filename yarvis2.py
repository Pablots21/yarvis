import pyttsx3
import sounddevice as sd
import speech_recognition as sr
from groq import Groq
import re
import threading
import webbrowser
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import numpy as np

client = Groq(api_key="SECRETO")

eventos = []

def enviar_evento(estado=None, mensaje=None, hablando=None):
    data = {}
    if estado: data['estado'] = estado
    if mensaje: data['mensaje'] = mensaje
    if hablando is not None: data['hablando'] = hablando
    eventos.append(json.dumps(data))

class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            ruta = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'yarvis.html')
            with open(ruta, 'rb') as f:
                self.wfile.write(f.read())
        elif self.path == '/events':
            self.send_response(200)
            self.send_header('Content-type', 'text/event-stream')
            self.send_header('Cache-Control', 'no-cache')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                while True:
                    if eventos:
                        msg = eventos.pop(0)
                        self.wfile.write(f"data: {msg}\n\n".encode())
                        self.wfile.flush()
                    time.sleep(0.1)
            except:
                pass

def hablar(texto):
    texto = re.sub(r'\*+', '', texto)
    texto = re.sub(r'#+', '', texto)
    texto = re.sub(r'\d+\.', '', texto)
    texto = texto.strip()
    print("Yarvis:", texto)
    enviar_evento(estado='HABLANDO', mensaje=texto, hablando=True)
    engine = pyttsx3.init()
    voces = engine.getProperty('voices')
    for voz in voces:
        if 'david' in voz.name.lower() or 'mark' in voz.name.lower() or 'male' in voz.name.lower():
            engine.setProperty('voice', voz.id)
            break
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
    engine.say(texto)
    engine.runAndWait()
    engine.stop()
    enviar_evento(estado='ESCUCHANDO', hablando=False)

def escuchar():
    enviar_evento(estado='ESCUCHANDO', mensaje='Habla ahora...')
    print("Escuchando...")
    frecuencia = 16000
    duracion = 8
    grabacion = sd.rec(int(duracion * frecuencia), samplerate=frecuencia, channels=1, dtype='int16')
    sd.wait()
    audio = sr.AudioData(grabacion.tobytes(), frecuencia, 2)
    r = sr.Recognizer()
    try:
        texto = r.recognize_google(audio, language="es-ES")
        print("Tu dijiste:", texto)
        enviar_evento(mensaje=f'Tu: {texto}')
        return texto
    except:
        hablar("No te entendi, repite por favor.")
        return ""

def responder(texto):
    enviar_evento(estado='PENSANDO...')
    respuesta = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": "Eres Yarvis, un asistente virtual inteligente. Responde en español, de forma breve, clara y sin usar simbolos ni listas con asteriscos."},
            {"role": "user", "content": texto}
        ]
    )
    return respuesta.choices[0].message.content

def loop_yarvis():
    time.sleep(2)
    hablar("Hola Juan, soy Yarvis. En que te puedo ayudar?")
    while True:
        comando = escuchar()
        if comando:
            if "adios" in comando.lower() or "adiós" in comando.lower() or "chao" in comando.lower() or "salir" in comando.lower() or "hasta luego" in comando.lower():
                hablar("Hasta luego Juan, fue un placer ayudarte.")
                break
            respuesta = responder(comando)
            hablar(respuesta)

servidor = HTTPServer(('localhost', 8080), Handler)
hilo_servidor = threading.Thread(target=servidor.serve_forever, daemon=True)
hilo_servidor.start()

time.sleep(1)
webbrowser.open('http://localhost:8080')

hilo_yarvis = threading.Thread(target=loop_yarvis, daemon=True)
hilo_yarvis.start()

print("Yarvis iniciado en http://localhost:8080")
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Yarvis apagado.")