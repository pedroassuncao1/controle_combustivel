import pandas as pd 
from App_Combustivel.models import Veiculo
import openpyxl

# Caminho do arquivo Excel: 
caminho_arquivo = "C:/Users/Usuário/Desktop/gestao_veiculos/diario_veiculos.xlsx"

# Carregar os dados da planilha 
df = pd.read_excel(caminho_arquivo, engine="openpyxl", header=1)
df = df.dropna(axis=1, how='all')  # Remove colunas vazias


print("aqui",df.columns)

# Renomear colunas para os nomes do modelo Django
# df = df.rename(columns={
#     "EQUIPAMENTO": "equipamento",
#     "ATIVO": "ativo",
#     "MARCA": "marca",
#     "MODELO": "modelo",
#     "CHASSIS/SÉRIE": "chassis",
#     "PLACA": "placa",
#     "ANO": "ano",
#     "OBRA": "obra",
#     "PROPRIETÁRIO": "proprietario",
#     "HS. ACUMULADO": "horas_acumuladas"
# })

# # Inserir os dados no banco de dados
# for index, row in df.iterrows():
#     Veiculo.objects.create(
#         equipamento=row["equipamento"],
#         ativo=row["ativo"],
#         marca=row["marca"],
#         modelo=row["modelo"],
#         chassis=row["chassis"],
#         placa=row["placa"],
#         ano=int(row["ano"]),
#         obra=row["obra"],
#         proprietario=row["proprietario"],
#         horas_acumuladas=float(row["horas_acumuladas"])
#     )

print("Dados importados com sucesso!")