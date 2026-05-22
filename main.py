from api import TemanUmkmApiError, TemanUmkmClient
from agent import TemanUmkmAgent


def main() -> None:
    client = TemanUmkmClient()
    agent = TemanUmkmAgent(client)

    try:
        agent.login()
    except TemanUmkmApiError as exc:
        print(f"Login gagal: {exc}")
        return

    print("Login berhasil.")
    print("Ketik 'exit' untuk keluar.")

    while True:
        user_message = input("\nYou: ").strip()

        if user_message.lower() == "exit":
            break

        try:
            print(agent.process(user_message))
        except TemanUmkmApiError as exc:
            print(f"AI: Maaf, request gagal. {exc}")

if __name__ == "__main__":
    main()