import xmlrpc.client
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class OdooGoogleSheetsIntegration:
    def __init__(self, odoo_url, odoo_db, odoo_username, odoo_password,
                 google_credentials_file, spreadsheet_id):
        # Configuração do Odoo
        self.odoo_url = odoo_url
        self.odoo_db = odoo_db
        self.username = odoo_username
        self.password = odoo_password
        
        # Conexão com Odoo
        self.common = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/common')
        self.uid = self.common.authenticate(self.odoo_db, self.username, self.password, {})
        self.models = xmlrpc.client.ServerProxy(f'{self.odoo_url}/xmlrpc/2/object')
        
        # Configuração do Google Sheets
        self.credentials = service_account.Credentials.from_service_account_file(
            google_credentials_file,
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.spreadsheet_id = spreadsheet_id

    def get_odoo_data(self, model, domain=None, fields=None):
        """
        Busca dados do Odoo
        :param model: Nome do modelo Odoo (ex: 'res.partner')
        :param domain: Lista de condições para filtrar dados
        :param fields: Lista de campos para recuperar
        :return: Lista de registros
        """
        if domain is None:
            domain = []
        if fields is None:
            fields = []
            
        return self.models.execute_kw(
            self.odoo_db, self.uid, self.password,
            model, 'search_read',
            [domain],
            {'fields': fields}
        )

    def update_sheet(self, range_name, values):
        """
        Atualiza dados no Google Sheets
        :param range_name: Range onde os dados serão escritos (ex: 'Sheet1!A1:D10')
        :param values: Lista de listas com os dados
        """
        try:
            body = {
                'values': values
            }
            self.sheets_service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id,
                range=range_name,
                valueInputOption='RAW',
                body=body
            ).execute()
            print(f'Dados atualizados em {range_name}')
        except HttpError as error:
            print(f'Erro ao atualizar planilha: {error}')

    def sync_data(self, model, sheet_range, domain=None, fields=None):
        """
        Sincroniza dados do Odoo para o Google Sheets
        :param model: Modelo do Odoo
        :param sheet_range: Range do Google Sheets
        :param domain: Filtros do Odoo
        :param fields: Campos do Odoo
        """
        # Busca dados do Odoo
        odoo_data = self.get_odoo_data(model, domain, fields)
        
        # Prepara dados para o Google Sheets
        if not odoo_data:
            return
            
        # Cria cabeçalho
        headers = list(odoo_data[0].keys())
        values = [headers]
        
        # Adiciona dados
        for record in odoo_data:
            row = [str(record[field]) for field in headers]
            values.append(row)
            
        # Atualiza planilha
        self.update_sheet(sheet_range, values)

# Exemplo de uso
if __name__ == "__main__":
    # Configurações
    ODOO_URL = "https://seu-odoo.com"
    ODOO_DB = "nome-banco"
    ODOO_USERNAME = "admin"
    ODOO_PASSWORD = "senha"
    GOOGLE_CREDS_FILE = "caminho/para/credentials.json"
    SPREADSHEET_ID = "id-da-sua-planilha"
    
    # Cria instância da integração
    integration = OdooGoogleSheetsIntegration(
        ODOO_URL, ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD,
        GOOGLE_CREDS_FILE, SPREADSHEET_ID
    )
    
    # Exemplo: sincronizar parceiros
    integration.sync_data(
        model='res.partner',
        sheet_range='Parceiros!A1:Z1000',
        fields=['name', 'email', 'phone']
    )