import asyncio
import os
import sqlite3
from asyncua import Client, ua
from asyncua.crypto.security_policies import SecurityPolicyAes128Sha256RsaOaep
from asyncua.ua import MessageSecurityMode


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pomiary.db")

Server_URL = "opc.tcp://localhost:4840"


async def main():
    conn_init = sqlite3.connect(DB_PATH)
    cursor_init = conn_init.cursor()
    cursor_init.execute("""
                   CREATE TABLE IF NOT EXISTS odczyty_opc(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nazwa_zmiennej TEXT,
                    wartosc TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)
    """)
    conn_init.commit()
    conn_init.close()

    client = Client(url=Server_URL)

    client.set_user("Login")
    client.set_password("Hasło")

    await client.set_security(
        SecurityPolicyAes128Sha256RsaOaep,
        certificate="client-cert.pem",
        private_key="client-key.pem",
        mode=MessageSecurityMode.SignAndEncrypt,
    )

    async with client:
        print("Połączono z serwerem pomyślnie!\n")

        hex_ids = [
            "01000000A6E12A718AF7333ABAFA2D7686EF60478CF76E7DA0F72579AAEC357A9DE63214",
            "01000000A6E12A718AF7333ABAFA2D7686EF60478CF76E66ACE5267D8AEA257A8AFA40",
            "01000000A6E12A718AF7333ABAFA2D7686EF60478CF76E6CA5EA2E71AFE235789D83",
            "01000000A6E12A718AF7333ABAFA2D7686EF60478CF76E6CBBF62E479EEA34778183",
        ]

        nodes = [
            client.get_node(
                ua.NodeId(bytes.fromhex(h_id), 5, ua.NodeIdType.ByteString)
            )
            for h_id in hex_ids
        ]

        node_names = []
        for node in nodes:
            display_name = await node.read_display_name()
            node_names.append(display_name.Text)

        while True:
            print("--- Nowy odczyt ---")

            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()

            for name, node in zip(node_names, nodes):
                value = await node.read_value()
                print(f"{name}: {value}")

                try:

                    cursor.execute(
                        """
                        INSERT INTO odczyty_opc (nazwa_zmiennej, wartosc) 
                        VALUES (?, ?)
                    """,
                        (name, str(value)),
                    )
                except Exception as e:
                    print(f"--> BŁĄD ZAPISU DLA {name}: {e}")

            conn.commit()
            conn.close()

            print("-" * 30)
            await asyncio.sleep(1)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram zakończony.")
