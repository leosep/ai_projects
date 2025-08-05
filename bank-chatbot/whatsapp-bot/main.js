const { makeWASocket, DisconnectReason, useMultiFileAuthState } = require("@whiskeysockets/baileys");
const { default: axios } = require("axios");
const path = require('path');
const qrcode = require('qrcode-terminal');

async function startBot() {
    const authPath = path.resolve(__dirname, 'auth');
    const { state, saveCreds } = await useMultiFileAuthState(authPath);

    const sock = makeWASocket({
        auth: state,
        browser: ['Aetheria Bank Bot', 'Safari', '1.0'],
    });

    sock.ev.on("creds.update", saveCreds);

    sock.ev.on("connection.update", (update) => {
        const { connection, lastDisconnect, qr } = update;
        if (qr) {
            console.log("Código QR recibido. Escanéalo con tu app de WhatsApp:");
            qrcode.generate(qr, { small: true });
        }

        if (connection === "close") {
            const shouldReconnect = (lastDisconnect.error?.output?.statusCode !== DisconnectReason.loggedOut);
            console.log("Conexión cerrada debido a ", lastDisconnect.error, ", reconectando ", shouldReconnect);
            if (shouldReconnect) {
                startBot();
            }
        } else if (connection === "open") {
            console.log("¡Conexión abierta!");
        }
    });

    sock.ev.on("messages.upsert", async ({ messages, type }) => {
        if (type === "notify") {
            const msg = messages[0];
            if (!msg.message || msg.key.fromMe || msg.key.remoteJid === 'status@broadcast') return;

            const senderJid = msg.key.remoteJid;
            const userText = msg.message.conversation || msg.message.extendedTextMessage?.text || msg.message.imageMessage?.caption || msg.message.videoMessage?.caption;

            if (!userText) return;

            console.log(`Mensaje recibido de ${senderJid}: ${userText}`);

            try {
                // Change the URL to your backend's URL
                const response = await axios.post("http://localhost:5000/ask", {
                    question: userText,
                    sender: senderJid
                });
                await sock.sendMessage(senderJid, { text: response.data.answer });
            } catch (error) {
                console.error("Error al comunicarse con el backend:", error.message);
                if (error.response) {
                    console.error("Datos de respuesta del backend:", error.response.data);
                    console.error("Estado de respuesta del backend:", error.response.status);
                }
                await sock.sendMessage(senderJid, { text: "Lo siento, tengo problemas para procesar tu solicitud en este momento. Por favor, intenta de nuevo más tarde o contacta a un administrador." });
            }
        }
    });
}

startBot();