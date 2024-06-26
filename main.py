import warnings
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
    results = pd.DataFrame(columns=['Client', 'Round', 'Timestamp', 'Download_Speed_Mbps', 'Upload_Speed_Mbps',
                                    'Ping_ms', 'Latency'])

    download_speed = 0
    upload_speed = 0
    ping = 0
    latency = 0
    client = 0

    for round in range(1, num_rounds + 1):
        for test in range(1, num_tests + 1):
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            st = speedtest.Speedtest()
            st.get_servers().get(server)  # Selecionando o servidor
            st.download()  # download speed
            st.upload()  # upload speed
            res_dict = st.results.dict()  # resultados em dicionário
            download_speed = res_dict['download'] / 1000000  # em Mbps
            upload_speed = res_dict['upload'] / 1000000  # em Mbps
            ping = res_dict['ping']  # em ms
            latency = res_dict['server']['latency']  # latency
            client = res_dict['client']['isp']  # provedor de internet

            with warnings.catch_warnings():
                # pandas 2.1.0 has a FutureWarning for concatenating DataFrames with Null entries
                warnings.filterwarnings("ignore", category=FutureWarning)
                results = results._append({'Client': client, 'Round': round, 'Timestamp': timestamp,
                                           'Download_Speed_Mbps': download_speed,
                                           'Upload_Speed_Mbps': upload_speed,
                                           'Ping_ms': ping, 'Latency': latency}, ignore_index=True)
            time.sleep(1)  # pausa de 1 segundo entre os testes

        if round < num_rounds:
            print(f"Download: {download_speed:.2f} Mbps | Upload: {upload_speed:.2f} Mbps | Ping: {ping:.2f} ms | "
                  f"Latency: {latency:.2f} | Cliente: {client} | Timestamp: {timestamp} | ")
            print(f"Rodada {round} concluída. Próxima rodada em {interval_minutes} minutos...")
            time.sleep(interval_minutes * 60)  # converter minutos para segundos

    # Salvar resultados em CSV a cada rodada
    results.to_csv(f'results_{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.csv', index=False)

    return results


def create_dashboard(results):
    plt.figure(figsize=(30, 15))
    sns.lineplot(data=results, x='Timestamp', y='Download_Speed_Mbps',
                 label=f'Download Speed (Avg: {results["Download_Speed_Mbps"].mean():.2f} Mbps)', errorbar=None)
    sns.lineplot(data=results, x='Timestamp', y='Upload_Speed_Mbps',
                 label=f'Upload Speed (Avg: {results["Upload_Speed_Mbps"].mean():.2f} Mbps)', errorbar=None)
    sns.lineplot(data=results, x='Timestamp', y='Ping_ms', label=f'Ping (Avg: {results["Ping_ms"].mean():.2f} ms)',
                 errorbar=None)
    sns.lineplot(data=results, x='Timestamp', y='Latency', label=f'Latency (Avg: {results["Latency"].mean():.2f})',
                 errorbar=None)

    # Ajustando os parâmetros para deixar as letras maiores
    plt.xlabel('Timestamp', fontsize=18)
    plt.ylabel('Speed/Ping', fontsize=18)
    plt.title(f'Internet Speed Test - {results["Client"].unique()[0]} - Results', fontsize=24)
    plt.legend(fontsize=24)
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.savefig(f'dashboard_{results["Client"].unique()[0]}_{datetime.now().strftime("%Y-%m-%d %H-%M-%S")}.png', dpi=300)
    plt.show()


if __name__ == "__main__":
    servers = get_servers_list()
    server = choose_server(servers)

    num_tests = 1  # int(input("Número de testes por rodada: "))
    interval_minutes = int(input("Intervalo de tempo entre testes (minutos): "))
    num_rounds = int(input("Número de testes: "))

    print("Iniciando os testes...")
    results = run_speedtest(num_tests, interval_minutes, num_rounds, server)
    print("Testes concluídos!")

    print("Criando o dashboard...")
    create_dashboard(results)
