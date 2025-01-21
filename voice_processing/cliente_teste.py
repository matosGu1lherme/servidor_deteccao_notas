import socket
import time

def cliente_nota(host='127.0.0.1', port=12346):
    with socket.create_connection((host, port)) as client_sockt:
        print("iniciando envio...")
        client_sockt.sendall(b"iniciar")

        duracao = 5
        inicio = time.time()

        while True:
            data = client_sockt.recv(1024)
            print("Nota Recebida", data.decode())

            if time.time() - inicio > duracao:
                print(f"Tempo de escuta de {duracao} segundos finalizado")
                break
        
        client_sockt.sendall(b"parar")
        time.sleep(3)
        client_sockt.sendall(b"continuar")
        
        inicio = time.time()
        while True:
            data = client_sockt.recv(1024)
            print("Nota Recebida", data.decode())


            if time.time() - inicio > duracao:
                print(f"Tempo de escuta de {duracao} segundos finalizado")
                break

        print("CABO!")

if __name__ == "__main__":
    cliente_nota()