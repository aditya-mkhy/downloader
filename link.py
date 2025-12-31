import os
from util import log
from typing import Tuple, Literal

class Link:
    def __init__(self):
        self.file_path = "./link.txt"

    def get_link(self) -> str:
        # reading data from file
        with open(self.file_path, "r") as ff:
            data = ff.read()

        # file is empty
        if len(data) == 0:
            return
    
        return self._get_down_url(data)
    
    def is_exists(self, url: str) -> bool:
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.strip() == url:
                        return True
        except FileNotFoundError:
            return False
    
    def add_link(self, url: str) -> bool:
        # check if already in file
        if self.is_exists(url):
            return False
        
        try:
            with open(self.file_path, "a", encoding="utf-8") as tf:
                tf.write(url + "\n")
                return True
            
        except Exception as e:
            print(f"Error [add_link] : {e}")

    
    def remove_link(self, url: str):
        new_file_data = ''
        is_replaced = False

        with open(self.file_path, "r") as ff:
            for line in ff:
                if is_replaced:
                    new_file_data += line
                    continue

                if url in line:
                    is_replaced = True
                else:
                    new_file_data += line

                
        if not is_replaced:
            return False
        
        with open(self.file_path, "w") as tf:
            tf.write(new_file_data)

        log(f"Link Removed : {url}")
        return True
        
    def _find_info(self, url_data: str) -> tuple[str, Literal["done", "failed"] | None]:
        """
        to find the info like->  done | failed
        """
        info = None
        url = None

        indx = url_data.find("->")
        if indx == -1:
            return url_data, info
        
        info = url_data[:indx].strip()
        url = url_data[indx + 2:].strip()
        return url, info


    def _get_down_url(self, data: str, retry: bool = False):
        '''
        Get url from link txt...
        '''
        while True:
            # getting index of the new_line chr.. to get the first url
            indx = data.find("\n")
            if indx != -1:
                url_data = data[:indx].strip()
            
            else:
                # if it's the last line
                url_data = data.strip()
                data = ""
            
            url, info = self._find_info(url_data)
            if not info:
                return url
            

            if data == "":
                return
            
            data = data[indx + 1:]

  
if __name__ == "__main__":
    lnk = Link()

    url = lnk.get_link()
    print(f"Link ==> {url}")

    lnk.remove_link(url)
    lnk.add_link("https://www.amazon.in/")
    # lnk.add_link("https://www.linkedin.com/feed/")