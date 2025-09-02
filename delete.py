import os
from util import log

def remove_data(line: str, data: str):
    start_index = line.find(data)
    quote = line[start_index - 1]

    data_to_delete = f"{quote}{data}{quote}"
    new_line = line.replace(data_to_delete, '')

    line_to_write = new_line[:start_index - 1]
    data_in_wich_comma_exists = new_line[start_index - 1:].lstrip()

    if (len(data_in_wich_comma_exists) > 0):
        # delete the first comma
        if data_in_wich_comma_exists[0] == ",":
            data_in_wich_comma_exists = data_in_wich_comma_exists[1:]

    line_to_write += data_in_wich_comma_exists

    if line_to_write.strip() == "":
        print(f"nothing is in the line")
        return ""
    else:
        return line_to_write + "\n"


def delete(file_path: str,  data: str):
    if not os.path.exists(file_path):
        log(f"FileNotExists : {file_path}")
        return 
    
    # open the file
    try:
        new_file_data = ''
        is_replaced = False

        with open(file_path, "r") as ff:
            for line in ff:
                if data in line:
                    new_file_data += remove_data(line, data)
                    is_replaced = True

                else:
                    new_file_data += line

                
        if not is_replaced:
            return False
        
        with open(file_path, "w") as tf:
            tf.write(new_file_data)

        log(f"DataIsRemovedFromFile : {data}")
        return True

    except Exception as e:
        log(f"ErrorInOpeningFile : {e}")
        return
    
  
if __name__ == "__main__":

    my_str = ["my name is aditya",   'love you']

    file_path = os.path.abspath(__file__)

    delete(file_path=file_path, data=my_str[1])

    

    


    
