# 🛡️L7 Forward Proxy & Application Firewall

Un Forward Proxy multithread e Next-Generation Firewall (NGFW) di Livello 7 scritto interamente in Python senza l'ausilio di framework esterni. 

Questo progetto dimostra i fondamenti dell'ingegneria di rete, la manipolazione dei socket TCP a basso livello, il tunneling cieco per connessioni cifrate e il multiplexing dell'I/O.

## ✨ Funzionalità Principali

* **Ispezione a Livello 7 (HTTP):** Intercetta, decodifica e analizza gli header HTTP in chiaro per applicare policy di filtraggio (Blocklist) basate su stringhe e domini.
* **Tunneling HTTPS (Metodo CONNECT):** Gestisce dinamicamente le richieste di connessione sicura instaurando un tunnel TCP cieco e bidirezionale tra il client e il server remoto.
* **Multiplexing I/O Asincrono:** Utilizza la system call `select` per gestire il traffico Full-Duplex senza incappare in blocchi di I/O (I/O Blocking), garantendo una latenza minima.
* **Architettura Multithread:** Genera thread demone indipendenti per ogni client connesso, permettendo la gestione concorrente di connessioni multiple sulla LAN.

## ⚙️ Architettura Tecnica

Il sistema opera come un "Man in the Middle" autorizzato all'interno di una rete locale (LAN). 
1. **Fase di Listening:** Il proxy esegue un bind sull'indirizzo `0.0.0.0`, mettendosi in ascolto di richieste provenienti da qualsiasi interfaccia di rete (es. porta `8080`).
2. **Handshake e Parsing:** Al completamento del Three-Way Handshake TCP con un client, il payload viene letto e processato. L'URL viene ripulito da percorsi e protocolli per estrarre l'Hostname e la Porta target.
3. **Firewall Policy:** L'Hostname viene confrontato con le regole della `BLOCKED_S` list. Se viene rilevata una violazione, il pacchetto subisce un drop istantaneo (chiusura del socket).
4. **Forwarding & Pipe:** Se il traffico è legittimo, il proxy istanzia un socket client verso l'esterno. Per l'HTTP, inoltra gli header grezzi; per l'HTTPS, risponde al client con `200 Connection Established` e avvia il tunneling cifrato.

## 🚀 Installazione e Utilizzo

### Prerequisiti
* Python 3.x installato sul sistema.
* Nessuna dipendenza esterna o libreria di terze parti richiesta (utilizza solo `socket`, `threading`, e `select` della standard library).

### Avvio del Server Proxy
1. Clonare la repository o scaricare il file `proxy.py`.
2. Aprire un terminale e avviare lo script:
   ```bash
   python proxy.py

    Il terminale mostrerà il messaggio: [*] Proxy in ascolto su 0.0.0.0:8080. Il log in tempo reale registrerà le connessioni in entrata e le azioni del firewall.

Configurazione dei Client (LAN)

Per far transitare il traffico attraverso il proxy:

    Individuare l'indirizzo IPv4 della macchina host sulla rete locale (es. 192.168.1.X).

    Aprire le impostazioni di rete del browser client (es. Firefox).

    Selezionare Configurazione manuale dei proxy.

    Inserire l'indirizzo IP dell'host alla voce Proxy HTTP/HTTPS e impostare la porta su 8080.

⚠️ Disclaimer

Questo progetto è stato sviluppato a scopo puramente didattico e accademico per lo studio delle architetture di rete e dei protocolli di trasporto.

***
