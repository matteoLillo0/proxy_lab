import socket
import threading
import select

HOST= "0.0.0.0"
PORT= 8080

BLOCKED_S = ["pataccaburdel.it"] # policy for blocked url

def gestisci_client(client_socket, client_address):
    try:
        richiesta = client_socket.recv(4096)
        if not richiesta:
            client_socket.close()
            return

        prima_riga = richiesta.split(b'\n')[0].decode('utf-8', errors='ignore')
        print(f"[{client_address[1]}] Richiesta: {prima_riga.strip()}")

        metodo = prima_riga.split(' ')[0]
        url = prima_riga.split(' ')[1]
        
        vietato = False

        for site in BLOCKED_S:
            if site in url:
                vietato = True
                break
            
        # actual block 
        if vietato:
            print(f"[!] BLOCCO ATTIVATO per {client_address[1]} verso {url}")
            client_socket.close()
            return
        
        print(f"[OK] Traffico consentito verso {url}")


        port = 80
        url_pulito = url

        # sanitization
        if "://" in url:
            url_pulito = url.split("://")[1]
            if url.split("://")[0] == "https":
                port = 443

        url_pulito = url_pulito.split('/')[0]

        if ":" in url_pulito:
            host = url_pulito.split(":")[0]
            port = int(url_pulito.split(":")[1])
        else:
            host = url_pulito
            if metodo == "CONNECT":
                port = 443

        # forwarding logic
        tunnel(host, port, metodo, richiesta, client_socket)

    except Exception as e:
        pass
    finally:
        client_socket.close()

def tunnel(host, port, metodo, richiesta_originale, client_socket):

    socket_esterno = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_esterno.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        socket_esterno.connect((host, port))
        
        if metodo == "CONNECT":
            risposta_ok = b"HTTP/1.1 200 Connection Established\r\n\r\n"
            client_socket.send(risposta_ok)
        else:
            socket_esterno.send(richiesta_originale)

        sockets_da_monitorare = [client_socket, socket_esterno]
    
        while True:
            
            readable, _, error_sockets = select.select(sockets_da_monitorare, [], sockets_da_monitorare, 10)
            
            if error_sockets:
                break
            for s in readable:
                dati = s.recv(8192)
                if not dati:
                    return
                if s is client_socket:
                    socket_esterno.sendall(dati)
                else:
                    client_socket.sendall(dati)

    except Exception as e:
        pass 

    finally: 
        socket_esterno.close() 

def start_proxy():

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # if u restart the script the port wont be blocked
    server_socket.bind((HOST, PORT))
    server_socket.listen(100)

    print(f"[*] Proxy in ascolto su {HOST}:{PORT}")

    while True:
        try:
            client_socket, client_address = server_socket.accept()
            client_thread = threading.Thread(
                target=gestisci_client,
                args=(client_socket, client_address)
            )
            client_thread.daemon = True
            client_thread.start()

        except KeyboardInterrupt:
            print("chiusura")
            break

if __name__=="__main__":
    start_proxy()