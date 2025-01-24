import socket
import threading

def receber_notas(client_socket):
    while True:
        try:
            data, _ = client_socket.recvfrom(1024) 
            nota = data.decode()
            print(f"Nota recebida: {nota}")
        except Exception as e:
            print(f"Erro ao receber dados: {e}")
            break


def cliente_notas(host='127.0.0.1', port=12346):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        threading.Thread(target=receber_notas, args=(client_socket,), daemon=True).start()

        while True:
            print("Digite um comando (iniciar, parar, continuar, sair):")
            comando = input().strip().lower()

            if comando in ['iniciar', 'parar', 'continuar']:
                client_socket.sendto(comando.encode(), (host, port))
            elif comando == 'sair':
                print("Encerrando cliente...")
                break
            else:
                print("Comando inválido. Tente novamente.")
    except KeyboardInterrupt:
        print("Cliente encerrado manualmente.")
    finally:
        client_socket.close()


if __name__ == "__main__":
    cliente_notas()
