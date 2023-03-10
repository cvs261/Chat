from socket import *
from threading import *
from tkinter import *

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

HOST = '127.0.0.1'
PORT = 7500
nickname = ""


def connectToServer():
    """
    Se solicită utilizatorului să introducă un nume de utilizator, care este apoi trimis către server prin socket.
    Dacă numele de utilizator este deja utilizat, utilizatorului i se afișează un mesaj de eroare.
    În caz contrar, fereastra de chat este deschisă prin apelarea funcției openChatWindow(nickname).
    """
    global nickname, clientSocket
    nickname = txtNickname.get()
    if nickname.strip() == '':
        lblError.config(text='Please enter a nickname')
    else:
        lblError.config(text='')

        # închidem socket-ul existent (dacă există)
        if 'clientSocket' in globals():
            clientSocket.close()

        # creăm un nou socket pentru a ne conecta la server cu noul nickname
        clientSocket = socket(AF_INET, SOCK_STREAM)
        clientSocket.connect((HOST, PORT))

        # trimite nickname-ul la server
        clientSocket.send(nickname.encode())

        # așteaptă răspunsul de la server
        response = clientSocket.recv(1024).decode()
        if response == "OK":
            openChatWindow(nickname)
        else:
            lblError.config(text='Nickname already in use.')


def openChatWindow(nick):
    """
    Afișează mesajul de bun venit în fereastra de chat, apoi creează un câmp de text unde mesajele sunt afișate,
    un câmp de text pentru utilizator să introducă mesajele sale și un buton "Trimite" pentru a trimite mesajele.
    De asemenea, este creat un fir de execuție pentru a primi mesajele de la server și a le afișa în câmpul de text.
    """
    connect_window.destroy()

    window = Tk()
    window.title('Connected To: ' + HOST + ':' + str(PORT))

    txt_messages = Text(window, width=50)
    txt_messages.grid(row=0, column=0, padx=10, pady=10)

    # Adaugati aici mesajul de bun venit
    txt_messages.insert(END, "Bun venit in chat, " + nick + "!\n")

    txt_your_message = Entry(window, width=50)
    txt_your_message.insert(0, 'Your message')
    txt_your_message.grid(row=1, column=0, padx=10, pady=10)

    def sendMessage():
        """
        În funcția sendMessage(), mesajul utilizatorului este extras din câmpul de text
        și trimis prin socket către server, care îl trimite la toți ceilalți utilizatori conectați.
        Mesajul este apoi afișat în câmpul de text al utilizatorului.

        """
        client_message = txt_your_message.get()
        txt_messages.insert(END, '\n' + nickname + ': ' + client_message)
        clientSocket.send(client_message.encode('utf-8'))
        txt_your_message.delete(0, END)

    bttn_send = Button(window, text='Send', width=20, command=sendMessage)
    bttn_send.grid(row=2, column=0, padx=10, pady=10)

    def recvMessage():
        """
        Funcția recvMessage() este responsabilă pentru primirea mesajelor de la server.
        Acesta rulează într-un fir de execuție separat pentru a nu bloca firul principal.
        Mesajele primite sunt decodate și afișate în câmpul de text al tuturor utilizatorilor.

        """
        while True:
            server_message = clientSocket.recv(1024).decode('utf-8')
            if server_message == "!DISCONNECT":
                txt_messages.insert(END, "\nServerul a inchis conexiunea. Aplicatia va fi inchisa.")
                window.after(3000, window.destroy)
                break
            txt_messages.insert(END, '\n' + server_message)

    recv_thread = Thread(target=recvMessage)
    recv_thread.daemon = True
    recv_thread.start()

    def disconnect():
        clientSocket.send("!DISCONNECT".encode('utf-8'))

    bttn_disconn = Button(window, text='Disconnect', width=20, command=disconnect)
    bttn_disconn.grid(row=3, column=0, padx=10, pady=10)

    window.mainloop()


connect_window = Tk()
connect_window.title('Connect to Server')

lblNickname = Label(connect_window, text='Enter your nickname:')
lblNickname.grid(row=0, column=0, padx=10, pady=10)

txtNickname = Entry(connect_window, width=20)
txtNickname.grid(row=0, column=1, padx=10, pady=10)

btnConnect = Button(connect_window, text='Connect', width=20, command=connectToServer)
btnConnect.grid(row=1, column=1, padx=10, pady=10)

lblError = Label(connect_window, fg='red')
lblError.grid(row=2, columnspan=2)

connect_window.mainloop()
