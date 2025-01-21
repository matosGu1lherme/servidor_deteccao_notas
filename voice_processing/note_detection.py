import pyaudio
import numpy as np
import librosa

# Configurações de áudio
CHUNK = 2048  # Tamanho do buffer
FORMAT = pyaudio.paInt16  # Formato do áudio
CHANNELS = 1  # Mono
RATE = 44100  # Taxa de amostragem (Hz)

# Mapeamento de frequências para notas musicais     
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

# Inicializa captura de áudio
audio = pyaudio.PyAudio()
stream = audio.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

print("Iniciando a detecção de notas... Pressione Ctrl+C para encerrar.")

try:
    while True:
        # Captura o áudio em tempo real
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
            print(f"Frequência: {dominant_freq:.2f} Hz, Nota: {note}")

except KeyboardInterrupt:
    print("Encerrando...")
finally:
    stream.stop_stream()
    stream.close()
    audio.terminate()
