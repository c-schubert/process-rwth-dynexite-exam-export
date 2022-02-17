import pathlib
from typing import Union, List, Set, Dict, Tuple, Optional

class dynexite_item:
    main_no : int = 1
    hash1 : str = ""
    hash2 : str = ""
    hash3 : str = ""
    upload_field_no : int = 0
    upload_filename = ""
    file_ext = ""

    def __init__(self, item : Union[str, pathlib.Path]):

        self.file_ext = item.suffix
        assert(item.is_file())

        #remove ext from itemname
        item = item.with_suffix('')
        name_parts = item.name.split("-")

        assert(len(name_parts) >= 5)
        
        self.main_no = int(name_parts[0])
        self.hash1 = name_parts[1]
        self.hash2 = name_parts[2]
        self.upload_field_no = int(name_parts[3])
        self.hash3 = name_parts[4]
    
        if len(name_parts) > 5:
            for p_str in name_parts[5:]:
                self.upload_filename += p_str

