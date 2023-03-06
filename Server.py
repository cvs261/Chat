from socket import *
from threading import *

# definim adresa IP și portul pentru server
HOST = '127.0.0.1'
PORT = 7500

# cream un socket pentru server
server = socket(AF_INET, SOCK_STREAM)
server.bind((HOST, PORT))

# lista pentru clientii conectati si nickname-urile lor
connected_clients = []
nicknames = []


def broadcast(message, sender_conn):
    """
    Trimite un mesaj către toți clienții conectați la server, în afară de cel care a trimis mesajul.
    """
    for conn, nickname in zip(connected_clients, nicknames):
        if conn is not sender_conn:
            try:
                conn.send(f"{message}".encode())
            except Exception as e:
                print(f"[ERROR] Failed to send message to {nickname}: {e}")
                # Eliminăm clientul din listele noastre
                index = connected_clients.index(conn)
                connected_clients.pop(index)
                nicknames.pop(index)
                # Trimitem un mesaj tuturor celorlalți clienți
                broadcast(f"{nickname} has left the chat!", server)


def handle_client(conn, addr):
    """
    Functie care gestioneaza conexiunile si mesajele primite de la clienti
    """
    global connected_clients, nicknames
    print(f"[NEW CONNECTION] {addr} connected.")

    # asteptam sa primim nickname-ul de la client
    nickname = conn.recv(1024).decode()

    # verificam daca nickname-ul este deja folosit
    while nickname in nicknames:
        conn.send("ERROR".encode())
        nickname = conn.recv(1024).decode()

    conn.send("OK".encode())

    # adaugă clientul și nickname-ul în liste
    connected_clients.append(conn)
    nicknames.append(nickname)

    # trimitem un mesaj tuturor clientilor ca un nou utilizator s-a conectat
    broadcast(f"{nickname} has joined the chat!", conn)

    while True:
        # primim mesajul de la client
        message = conn.recv(1024).decode()

        # verificam daca clientul a trimis mesajul de deconectare
        if message == "!DISCONNECT":
            # eliminam clientul din liste si inchidem conexiunea
            index = connected_clients.index(conn)
            connected_clients.remove(conn)
            nickname = nicknames[index]
            nicknames.remove(nickname)
            conn.close()
            print(f"[DISCONNECTED] {nickname} ({addr}) disconnected.")
            # trimitem un mesaj tuturor clientilor ca un utilizator s-a deconectat
            broadcast(f"{nickname} has left the chat!", conn)
            break
        else:
            # trimitem mesajul catre toti clientii conectati la server, in afara de cel care a trimis mesajul
            index = connected_clients.index(conn)
            nickname = nicknames[index]
            broadcast(f'{nickname}: {message}', conn)

    # inchidem conexiunea
    conn.close()


def start():
    # ascultam conexiuni
    server.listen()
    print(f"[LISTENING] Server is listening on {HOST}:{PORT}")

    while True:
        # acceptam o noua conexiune
        conn, addr = server.accept()
        # pornim un thread pentru a gestiona conexiunea cu clientul
        client_thread = Thread(target=handle_client, args=(conn, addr))
        client_thread.start()
        # afisam numarul de clienti conectati
        print(f"[ACTIVE CONNECTIONS] {active_count() - 1}")


start()
