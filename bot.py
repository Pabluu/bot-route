<<<<<<< HEAD
from os import getenv, path
from utils import path_project, permitionUser
=======
from os import getenv, path, getcwd
>>>>>>> refs/remotes/origin/main
from  shutil import rmtree
from dotenv import load_dotenv
from uvloop import install
from pyrogram import Client, filters
from main import Main

load_dotenv()
install()

app = Client(
  'route_bot',
  api_id=getenv('TELEGRAM_API_ID'),
  api_hash=getenv('TELEGRAM_API_HASH'),
<<<<<<< HEAD
  bot_token=getenv('TELEGRAM_BOT_TOKEN'),
  timeout=10
=======
  bot_token=getenv('TELEGRAM_BOT_TOKEN')
>>>>>>> refs/remotes/origin/main
)

def log_info_user(message):
  user = message.from_user
  
  try:
    print(f'''==============INFO USER===============
ID: {user.id}
Usuario: {user.username}
Telefone: {user.phone_number}
======================================
    ''')
  except:
    pass


@app.on_message(filters.document)
async def document(client, message):
  try:
    log_info_user(message)
<<<<<<< HEAD
    user_id = message.from_user.id

    permitionUser(user_id)
=======
>>>>>>> refs/remotes/origin/main
    
    file_name = message.document.file_name
    file_extension = path.splitext(file_name)[1]

    if file_extension != '.xlsx':
      raise Exception('**Apenas arquivos .xlsx são permitidos!**')

    await message.reply('**Aguarde**', quote=True)
    document_path = await message.download()
<<<<<<< HEAD
        
    processed_file = Main(document_path)
    await client.send_document(chat_id=message.chat.id, document=processed_file)

    path_to_delet = f'{path_project()}/downloads/'    
    rmtree(path_to_delet)
=======
    processed_file = Main(document_path)
    
    await client.send_document(chat_id=message.chat.id, document=processed_file)

    rmtree(f'{getcwd()}/downloads/')
>>>>>>> refs/remotes/origin/main

  except Exception as error:
    print(error)
    await message.reply(error, quote=True)


@app.on_message()
async def messages(client, message):
  log_info_user(message)
  
  await message.reply('Somente arquivos excel: XLSX')

print('bot no ar!!!')
app.run()