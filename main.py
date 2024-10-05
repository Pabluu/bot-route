
def Main(fileLoad):
  #
<<<<<<< HEAD
  from utils import load_file, copy_sheet, index_column_address, insert_column, organize_worksheet, remove_duplicate, remove_apartment, save_workbook, path_project, edit_length, check_address, formatDateFile
=======
  from utils import load_file, copy_sheet, index_column_address, insert_column, organize_worksheet, remove_duplicate, remove_apartment, save_workbook, path_file_XLSX, edit_length, check_address, formatDateFile
>>>>>>> refs/remotes/origin/main

  _, worksheet = load_file(fileLoad)

  # faz uma copia do arquivo
  data = copy_sheet(worksheet)

  # descobre a coluna que fica o endereço
  indexColumnAddress = index_column_address(data)
  indexColumnDescription = indexColumnAddress + 1
  indexColumnLength = indexColumnDescription + 1

  #
  organize_worksheet(data, indexColumnDescription, indexColumnAddress)

  # insere a coluna 'quantidade' no final da linha
  insert_column(data, indexColumnLength, 'Quantidade', 1)

  # corrige os endereços errados que começam com "r. ", "R. " por "Rua"
  check_address(data, indexColumnAddress)
  
  data = remove_duplicate(data, indexColumnAddress, indexColumnLength)
  
  # data = fetchAddress(data, indexColumnAddress)

  # data = remove_duplicate(data, indexColumnAddress, indexColumnLength)

  # remove os endereços do por do sol e add somente a quantidade
  remove_apartment(data, indexColumnAddress, indexColumnLength)

  edit_length(data, indexColumnLength)

<<<<<<< HEAD
  name_file_posfixo = f'downloads/{formatDateFile()}'
  name_file = f'{path_project()}/{name_file_posfixo}'

  save_workbook(data, name_file)

  return name_file
=======
  name_file = f'downloads/{formatDateFile()}'

  save_workbook(data, name_file)

  return path_file_XLSX(name_file)
>>>>>>> refs/remotes/origin/main
