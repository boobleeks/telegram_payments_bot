import gspread
from oauth2client.service_account import ServiceAccountCredentials
from database.models import User

async def export_to_google_sheets():
    # Авторизация Google API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("google_sheets_client/credentials.json", scope)
    client = gspread.authorize(creds)

    sheet = client.open("ExportedBotData").sheet1
    sheet.clear()


    headers = [
        "payment_id", "tg_id", "phone_number", "created_at",
        "transaction_id", "card_number", "amount", "x_id",
        "verification_code", "type", "status", "transaction_created_at"
    ]
    sheet.append_row(headers)

 
    users = await User.all().prefetch_related("transactions")

    for user in users:
        for tx in user.transactions:
            row = [
                user.payment_id,
                user.tg_id,
                user.phone_number,
                user.created_at.isoformat(),

                tx.id,
                tx.card_number,
                tx.amount,
                tx.x_id,
                tx.verification_code,
                tx.type,
                tx.status,
                tx.created_at.isoformat()
            ]
            sheet.append_row(row)

    print("✅ Экспорт завершён.")
