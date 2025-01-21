import socket
import threading
import time
import pyaudio
import numpy as np


#Variaveis de controle de Threads
thread_event = threading.Event()
stop_flag = False

#Variaveis de configurações de áudio
CHUNK = 2048  # Tamanho do buffer
FORMAT = pyaudio.paInt16  # Formato do áudio
CHANNELS = 1  # Mono
RATE = 44100  # Taxa de amostragem (Hz)

def freq_to_note(freq):
    A4 = 440.0  # Frequência padrão do Lá4
    notes = [
        "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"
    ]
    if freq == 0:  # Sem frequência detectada
        return None

    # Calcula o número de semitons em relação ao A4
    semitones = int(np.round(12 * np.log2(freq / A4)))
    note_index = (semitones + 69) % 12  # Nota correspondente
    octave = (semitones + 69) // 12  # Oitava
    return f"{notes[note_index]}{octave}"

def ouvir_notas(client_socket):
    print("Iniciando thread e módulos")
    
    global stop_flag

    audio = pyaudio.PyAudio()
    stream = audio.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)

    print("Escuta e processamento de aúdio iniciados!")
    while True:
        if stop_flag:
            print("Parando thread...")
            thread_event.wait()
            print("Continuando a execução")
        else:
            data = stream.read(CHUNK, exception_on_overflow=False)
            samples = np.frombuffer(data, dtype=np.int16)

            # Calcula a FFT (Transformada Rápida de Fourier)
            fft = np.fft.fft(samples)
            freqs = np.fft.fftfreq(len(fft), 1 / RATE)

            # Obtém a frequência dominante
            magnitude = np.abs(fft)
            peak_index = np.argmax(magnitude[:CHUNK // 2])  # Somente metade útil
            dominant_freq = abs(freqs[peak_index])

            # Converte frequência em nota
            note = freq_to_note(dominant_freq)
            if note:
                try: 
                    client_socket.send(note.encode())
                except BrokenPipeError:
                    print("Cliente desconectado. Encerrando!")
                    break

def ouvir_sinais(client_socket):
    global stop_flag
    
    while True:
        sinal = client_socket.recv(1024).decode().strip()
        if sinal.lower() == "parar":
            print("Sinal de PARAR recebido")
            stop_flag = True
        elif sinal.lower() == "iniciar":
            print("Sinal de INICIAR recebido")
            ouvir_thread = threading.Thread(target=ouvir_notas, args=(client_socket,))
            ouvir_thread.start()
        elif sinal.lower() == "continuar":
            print("Sinal de CONTINUAR recebido")
            stop_flag = False
            thread_event.set()


def servidor_notas(host='127.0.0.1', port=12346):

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Usa IPV4 e TCP
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_socket.bind((host, port))
    server_socket.listen(1)
    print(f"O servidor esta rodando no seguinte endereço {host}:{port}...")

    try:
        while True:
            print("Aguardando conexões...")
            client_socket, client_address = server_socket.accept()
            print(f"Conexão estabelecida com o tal {client_address}")

            sinais_thread = threading.Thread(target=ouvir_sinais, args=(client_socket,))
            sinais_thread.start()

    except KeyboardInterrupt:
        print("Servidor finalizado")
    finally:
        server_socket.close()


if __name__=="__main__":
    servidor_notas()