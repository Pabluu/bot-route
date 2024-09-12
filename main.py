
def Main(fileLoad):
  #
  from utils import load_file, copy_sheet, index_column_address, insert_column, organize_worksheet, remove_duplicate, remove_apartment, save_workbook, path_file_XLSX, edit_length, check_address, formatDateFile

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

  name_file = f'downloads/{formatDateFile()}'

  save_workbook(data, name_file)

  return path_file_XLSX(name_file)