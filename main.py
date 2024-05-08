import speedtest
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from datetime import datetime
import time


def get_servers_list():
    s = speedtest.Speedtest()
    s.get_servers()
    servers = s.servers
    return servers


def choose_server(servers):
    print("Escolha um servidor para realizar o teste:")
    for idx, server in enumerate(servers):
        print(f"{idx + 1}. {servers[server][0]['name']} ({servers[server][0]['country']})")

    while True:
        choice = input("Digite o número do servidor ou pressione Enter para escolher o melhor servidor: ")
        if choice == "":
            return list(servers.keys())[0]
        try:
            choice_idx = int(choice) - 1
            if choice_idx >= 0 and choice_idx < len(servers):
                return list(servers.keys())[choice_idx]
            else:
                print("Escolha inválida. Por favor, escolha um número válido.")
        except ValueError:
            print("Entrada inválida. Por favor, digite um número.")


def run_speedtest(num_tests, interval_minutes, num_rounds, server):
    results = pd.DataFrame(columns=['Round', 'Timestamp', 'Download_Speed_Mbps', 'Upload_Speed_Mbps', 'Ping_ms'])

    st = speedtest.Speedtest()
    st.get_servers().get(server)  # Selecionando o servidor

    for round in range(1, num_rounds + 1):
        for test in range(1, num_tests + 1):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            download_speed = st.download() / 1000000  # em Mbps
            upload_speed = st.upload() / 1000000  # em Mbps
            ping = st.results.ping  # em ms

            results = results._append({'Round': round, 'Timestamp': timestamp,
                                       'Download_Speed_Mbps': download_speed,
                                       'Upload_Speed_Mbps': upload_speed,
                                       'Ping_ms': ping}, ignore_index=True)
            time.sleep(1)  # pausa de 1 segundo entre os testes

        if round < num_rounds:
            print(f"Rodada {round} concluída. Próxima rodada em {interval_minutes} minutos...")
            time.sleep(interval_minutes * 60)  # converter minutos para segundos

    # Salvar resultados em CSV a cada rodada
    results.to_csv(f'results_{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.csv', index=False)

    return results


def create_dashboard(results):
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=results, x='Timestamp', y='Download_Speed_Mbps', label='Download Speed (Mbps)', ci=None)
    sns.lineplot(data=results, x='Timestamp', y='Upload_Speed_Mbps', label='Upload Speed (Mbps)', ci=None)
    sns.lineplot(data=results, x='Timestamp', y='Ping_ms', label='Ping (ms)', ci=None)

    # Calculando médias
    avg_download_speed = results['Download_Speed_Mbps'].mean()
    avg_upload_speed = results['Upload_Speed_Mbps'].mean()
    avg_ping = results['Ping_ms'].mean()

    # Adicionando informações sobre as médias no gráfico
    plt.text(results.iloc[-1]['Timestamp'], avg_download_speed, f'Avg Download: {avg_download_speed:.2f} Mbps',
             ha='right')
    plt.text(results.iloc[-1]['Timestamp'], avg_upload_speed, f'Avg Upload: {avg_upload_speed:.2f} Mbps', ha='right')
    plt.text(results.iloc[-1]['Timestamp'], avg_ping, f'Avg Ping: {avg_ping:.2f} ms', ha='right')

    plt.xlabel('Timestamp')
    plt.ylabel('Speed/Ping')
    plt.title('Internet Speed Test Results')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    servers = get_servers_list()
    server = choose_server(servers)

    num_tests = int(input("Número de testes por rodada: "))
    interval_minutes = int(input("Intervalo de tempo entre as rodadas (minutos): "))
    num_rounds = int(input("Número de rodadas: "))

    print("Iniciando os testes...")
    results = run_speedtest(num_tests, interval_minutes, num_rounds, server)
    print("Testes concluídos!")

    print("Criando o dashboard...")
    create_dashboard(results)
