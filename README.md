# 🛡️ proxy_lab — L7 Forward Proxy con filtro sui domini

Forward proxy HTTP/HTTPS multithread scritto in Python usando esclusivamente la standard library (`socket`, `threading`, `select`), senza framework esterni.

Il progetto nasce per studiare da vicino come funziona un proxy: gestione dei socket TCP a basso livello, parsing delle richieste HTTP, tunneling delle connessioni cifrate tramite il metodo `CONNECT` e multiplexing dell'I/O.

## ✨ Funzionalità

* **Parsing e filtraggio a livello 7 (HTTP):** il proxy legge la richiesta HTTP in chiaro, ne estrae host e porta di destinazione e applica una policy di filtraggio basata su una blocklist di domini e stringhe.
* **Tunneling HTTPS (metodo `CONNECT`):** per le connessioni cifrate il proxy apre un tunnel TCP bidirezionale tra client e server remoto e si limita a inoltrare i byte, senza decifrare né ispezionare il contenuto. Il filtraggio sulle connessioni HTTPS avviene quindi solo sull'hostname indicato nella richiesta `CONNECT`.
* **I/O multiplexing con `select`:** l'inoltro full-duplex tra client e server è gestito con la system call `select`, così un singolo thread può attendere dati su entrambi i socket senza restare bloccato su una sola direzione.
* **Un thread per client:** ogni connessione in ingresso viene servita da un thread daemon dedicato, permettendo di gestire più client della LAN in parallelo.
* **Log in tempo reale:** il terminale mostra le connessioni in ingresso e le azioni del filtro.

## ⚙️ Come funziona

```
Client (browser) ──► proxy_lab :8080 ──► Server remoto
                        │
                        ├─ HTTP:  parsing header → controllo blocklist → inoltro richiesta
                        └─ HTTPS: CONNECT host:443 → controllo blocklist → "200 Connection Established" → tunnel TCP
```

1. **Listening:** il proxy esegue il bind su `0.0.0.0:8080` e accetta connessioni da qualsiasi interfaccia di rete.
2. **Parsing:** dopo l'accettazione della connessione, il proxy legge la prima richiesta del client e, rimuovendo schema e percorso dall'URL, ricava hostname e porta di destinazione.
3. **Filtraggio:** l'hostname viene confrontato con la lista `BLOCKED_S`. In caso di corrispondenza la richiesta viene rifiutata chiudendo la connessione con il client.
4. **Inoltro:** se la richiesta è consentita, il proxy apre un socket verso il server di destinazione.
   * Per **HTTP** inoltra la richiesta originale così com'è e restituisce la risposta al client.
   * Per **HTTPS** risponde al client con `HTTP/1.1 200 Connection Established` e da quel momento inoltra in entrambe le direzioni il traffico TLS, che resta cifrato end-to-end tra browser e server.

## 🚀 Installazione e utilizzo

### Prerequisiti

* Python 3.x
* Nessuna dipendenza esterna

### Avvio

```bash
git clone https://github.com/matteoLillo0/proxy_lab.git
cd proxy_lab
python proxy.py
```

All'avvio il terminale mostra:

```
[*] Proxy in ascolto su 0.0.0.0:8080
```

### Configurazione dei client nella LAN

1. Individua l'indirizzo IPv4 della macchina che esegue il proxy (ad esempio `192.168.1.X`).
2. Sul client, apri le impostazioni di rete del browser (ad esempio in Firefox: *Impostazioni → Rete → Configurazione manuale dei proxy*).
3. Inserisci l'IP della macchina host come proxy HTTP, imposta la porta `8080` e abilita l'uso dello stesso proxy anche per HTTPS.

Per una prova rapida senza browser:

```bash
curl -x http://192.168.1.X:8080 http://example.com
curl -x http://192.168.1.X:8080 https://example.com
```

## 🚧 Limiti noti

Essendo un progetto di studio, alcune funzionalità tipiche di un proxy di produzione sono volutamente assenti:

* nessuna ispezione del contenuto HTTPS (niente TLS interception), quindi il filtro HTTPS agisce solo sul nome host;
* blocklist definita nel codice anziché in un file di configurazione;
* nessun supporto a keep-alive HTTP, caching o autenticazione dei client;
* modello un-thread-per-connessione, semplice da leggere ma non adatto a carichi elevati.

## ⚠️ Disclaimer

Progetto sviluppato a scopo esclusivamente didattico, per lo studio delle architetture di rete e dei protocolli di trasporto. Da usare solo su reti e dispositivi di cui si ha il controllo o l'autorizzazione.

## 📄 Licenza

Distribuito con licenza MIT. Vedi il file `LICENSE`.
