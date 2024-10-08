import gspread
from google.oauth2 import service_account
import pandas as pd
from datetime import datetime
from time import sleep

json_file = "project-to-web-scraping-e782cbd91f6b.json"


def login(json_file, scopes):
  credentials = service_account.Credentials.from_service_account_file(
    json_file)
  scoped_credentials = credentials.with_scopes(scopes)
  google_client = gspread.authorize(scoped_credentials)
  return google_client


def write_coins_to_spreadsheet(coins, table, json_file=json_file):
  scopes = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
  ]
  try:
    google_client = login(json_file, scopes)
    worksheet = google_client.open('tcc-api').worksheet(table)

    # Create a DataFrame with the data
    data = {}
    for item in coins:
      date = datetime.strptime(item['date'], '%d-%m-%Y').date()
      item['date'] = date.strftime('%d-%m-%Y')
      for coin in item['cryptos']:
        if coin['coin'] not in data:
          data[coin['coin']] = {}
        if not isinstance(data[coin['coin']], dict):
          data[coin['coin']] = {}
        data[coin['coin']][item['date']] = str(
          coin['value']) 
      print(f"Escrevendo a data {item['date']} na planilha...")
      sleep(10)
    df = pd.DataFrame.from_dict(data, orient='columns')
    df = df.where(pd.notnull(df), None)
    df.index.name = 'date'
    df = df.reset_index().rename(columns={'index': 'date'})

    # Write the DataFrame to the worksheet
    worksheet.clear()
    header = df.columns.values.tolist()
    worksheet.insert_row(header, 1)
    df_values = df.values.tolist()
    worksheet.insert_rows(df_values, 2)

    return "Planilha atualizada com sucesso."
  except Exception as e:
    return f"Erro ao atualizar planilha: {str(e)}"
