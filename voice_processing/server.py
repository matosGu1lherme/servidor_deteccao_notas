import socket
import threading
import time
import pyaudio
import numpy as np

thread_event = threading.Event()
stop_flag = False

CHUNK = 2048  
FORMAT = pyaudio.paInt16  
CHANNELS = 1  
RATE = 44100  


def freq_to_note(freq):
    A4 = 440.0  # Frequência padrão do Lá4
    notes = [
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
    ]
    if freq == 0:  # Sem frequência detectada
        return None

    semitones = int(np.round(12 * np.log2(freq / A4)))
    note_index = (semitones + 69) % 12  # Nota correspondente
    octave = (semitones + 69) // 12  # Oitava
    return f"{notes[note_index]}{octave}"


def ouvir_notas(server_socket, client_address):
    print("Iniciando thread e módulos")

    global stop_flag

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Escuta e processamento de áudio iniciados!")
    while True:
        if stop_flag:
            print("Parando thread...")
            thread_event.wait()
            print("Continuando a execução")
        else:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)

            fft = np.fft.fft(samples)
            freqs = np.fft.fftfreq(len(fft), 1 / RATE)

            magnitude = np.abs(fft)
            peak_index = np.argmax(magnitude[:CHUNK // 2])  
            dominant_freq = abs(freqs[peak_index])

            note = freq_to_note(dominant_freq)
            if note:
                try:
                    server_socket.sendto(note.encode(), client_address)
                except Exception as e:
                    print(f"Erro ao enviar dados para o cliente: {e}")
                    break


def ouvir_sinais(server_socket):
    global stop_flag

    client_address = None
    while True:
        data, address = server_socket.recvfrom(1024)  
        sinal = data.decode().strip()

        if client_address is None:
            client_address = address  
            print(f"Cliente conectado: {client_address}")

        if sinal.lower() == "parar":
            print("Sinal de PARAR recebido")
            stop_flag = True
        elif sinal.lower() == "iniciar":
            print("Sinal de INICIAR recebido")
            ouvir_thread = threading.Thread(target=ouvir_notas, args=(server_socket, client_address))
            ouvir_thread.start()
        elif sinal.lower() == "continuar":
            print("Sinal de CONTINUAR recebido")
            stop_flag = False
            thread_event.set()


def servidor_notas(host='127.0.0.1', port=12346):
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Usa UDP
    server_socket.bind((host, port))
    print(f"O servidor está rodando no seguinte endereço {host}:{port}...")

    try:
        ouvir_sinais(server_socket)
    except KeyboardInterrupt:
        print("Servidor finalizado")
    finally:
        server_socket.close()


if __name__ == "__main__":
    servidor_notas()
