import os
from util import get_downloadpath, time_cal, data_size_cal, log, fpath, is_online, Status
import time
import requests
from threading import Thread, Timer
from urllib.parse import unquote
from link import Link

class Downloader:
    def __init__(self, del_link: bool = False) -> None:
        #path to save the file
        self.save_path = get_downloadpath()
        self.del_link = del_link
        self.link = Link()
        # chunk size 8485
        self.chunk = 8485


    def remove_symbol_from_filename(self, filename: str):
        return unquote(filename).replace(":", "-").replace("|", "_")
    
    def find_path_from(self, headers=None, url=None):
        if headers:
            try:
                ContentDisposition = str(headers['Content-Disposition'])
                indx = ContentDisposition.find('filename="')
                if indx > 0:
                    txt = ContentDisposition[indx+10 :]
                    indx2 = txt.find('"')
                    if indx2 > 0:
                        fileName = txt[ : indx2]
                        fileName = self.remove_symbol_from_filename(fileName)
                        return fileName
                    
            except Exception as e:
                log(f"Failed to find the path from hearder : {e}")


        if url:
            try:

                fileName = url[url.rfind("/")+1 : ]
                fileName = self.remove_symbol_from_filename(fileName)
                popExt = [".webm", ".mkv", ".png", ".exe", ".iso", ".zip", ".wmv", ".wav", ".txt",
                                ".pdf", ".msi", ".mp4", ".mp3", ".m4a", ".jpg", "jpej", ".jar", ".iso", ".html"]

                path, ext = os.path.splitext(fileName)
                if ext in popExt:
                    return fileName
                
                else:
                    if ext  != "":
                        return fileName
                    
                    else:
                        return False
                    
            except Exception as e:
                log(f"Failed to find path from url : {e}")
            
        return False
    

        
    def direct_download(self, url :str, trial = 1):

        filename = self.find_path_from(url=url)
        response = None

        if not filename:
            #if file_path not found in url
            response = requests.get(url, stream = True)
            log(f"status_code==> {response.status_code}")

            filename = self.find_path_from(headers = response.headers)
            if not filename:
                log(f"filename is also not found in header... error")
                return "Error"

        file_path = f"{self.save_path}\\{filename}"
        log(f"FilePath : {file_path}")
        
        from_byte = 0
        headers = {}
        cookies = {}

        if os.path.exists(file_path):
            # resuming from prevoius download
            from_byte = os.stat(file_path).st_size

            log(f"File Already exists. Trying to resume it from {data_size_cal(from_byte)}")
            headers["Range"] = f"bytes={from_byte}-"
            
            if response:
                try:
                    response.close()
                    log(f"Closing the previous response object...")
                except:
                    pass

            # getting new response from previous download size
            response = requests.get(url, cookies=cookies, headers=headers, stream=True)

        if not response:
            # if file not exits then response also not exists
            response = requests.get(url, stream=True)
        
        if response.status_code == 200 or response.status_code == 206:
            if from_byte != 0:

                if from_byte == int(response.headers["Content-Length"]) and response.status_code != 416:
                    log(f"File is already downloaded.....")
                    log(f"and status_code ==> {response.status_code}")
                    response.close()

                    if self.del_link:
                        self.link.remove_link(url=url)
                    
                    return True

                if response.status_code == 206:
                    log(f"Downloading is resuming from {data_size_cal(from_byte)}")

                else:
                    log(f"Error in resuming the file from {data_size_cal(from_byte)}")

                    from_byte = 0
                    n = input("Do you want to countinue : ")

                    if n ==  "n" or n== "N" or n == "NO" or n == "No" or n == "no":
                        exit()
                    log("Restarting the download..ignoring the previous download..")


            log(f"status_code ==> {response.status_code}")
            # print(f"coockies==> {response.cookies.items()}")
            # print(f"Header==> {response.headers}")
            content_length = int(response.headers["Content-Length"])

            # save file
            status = self.save(url=url, response=response, file_path=file_path, content_length=content_length, from_byte=from_byte)

            #checking save status...
            if not status:
                if not is_online():
                    return "offline"

                if trial >= 5:
                    log("Maximum trial ended... now cancelling this file..")
                    return "Error"
                
                time.sleep(2)
                log(f"Trying again.. trial number : {trial}")
                return self.direct_download(url=url, trial=trial + 1)
            
            log(f"File downloaded : {file_path}")
            return status

        else:
            log(f"Error[11]: Status_Code==> {response.status_code}")
            # print(f"coockies==> {response.cookies.items()}")
            # print(f"Header==> {response.headers}")
            if response.status_code == 403 or response.status_code == 503:
                log("The download quota for this file has been exceeded....")
                time.sleep(2)
                log(f"Retrying for {trial} time.......")

                if trial >= 10:
                    log("Maximum trial ended... now cancelling this file..")
                    return "Error"
                
                return self.direct_download(url=url, trial=trial + 1)
            
            elif response.status_code == 416:
                response.close()
                log(f"File Alredy Dowloaded  link-> {file_path}")

                if self.del_link:
                    self.link.remove_link(url=url)
                return True
            
            else:
                log("Error[]: Not able to downnload file.. please check it manually..")
                return False
            

    def __store(self, tf, status:  Status):
        while True:
            data = status.data_queue.get()
            if data is None:
                log("error[08]: data is none")
                break
            # write data
            tf.write(data)

            if status.stop and status.data_queue.empty():
                log("info[001] : Stopping the writing...")
                break

    def save(self, url, response, file_path, content_length, from_byte):
        mode = "wb"
        if from_byte != 0:
            mode = "ab"

        status = Status()
        status.content_length = content_length
        # cause content_length includes only current dowloading length.. not pravoius dowloaded length
        status.content_length += from_byte
        
        try:
            with open(file_path, mode) as tf:
                status.downloaded_length = tf.tell()
                # to correct the download speed at first
                status.prev_length = status.downloaded_length 
                log("Downloading....")

                status.write_thr = Thread(target=self.__store, args=(tf, status), daemon=True)
                status.write_thr.start()

                # status.progress_thr = Thread(target=self.update_progress, args=(status, ), daemon=True)
                # status.progress_thr.start()
                self.update_progress(status=status)

                for chunk in response.iter_content(self.chunk):
                    if chunk is not None: # filter out keep-alive new chunks
                        status.data_queue.put(chunk)
                        status.downloaded_length += len(chunk)

                status.stop = True
                log("Chunk block is ended...")


            log("File is closed for good...")
            if status.downloaded_length == status.content_length:
                log(f"***** File Downloaded Success& size={data_size_cal(status.downloaded_length)} ************")
                log(f"File Downloaded : {file_path}")

                if self.del_link:
                    self.link.remove_link(url=url)
                return True
            
            else:
                log(f"Error[004] File not Downloaded && size={data_size_cal(status.downloaded_length)}")
                return False

        except Exception as e:
            status.stop = True

            log(f"Error[005] in saving file --> {e}")
            return False

    def update_progress(self, status: Status):
        if status.stop == True:
            return True
        
        Timer(3.0, self.update_progress, (status, )).start()

        content_length = status.content_length
        downloaded_length = status.downloaded_length
        prev_length = status.prev_length

        # saving the current downloaded_length to prev_length
        status.prev_length = downloaded_length
        delta = max(1, downloaded_length - prev_length)
        per_sec_size = delta // 3

        try:
            timest = f"{time_cal((content_length - downloaded_length) // per_sec_size)} left"
        except:
            timest = "Cal.."

        speed = f"({data_size_cal(downloaded_length)} of {data_size_cal(content_length)} , {data_size_cal(per_sec_size)}/Sec)"
        print(f"  {speed}   {timest}                          ", end='\r')



    def download(self, url: list):
        if isinstance(url, str):
            urls = [url]

        elif isinstance(url, list):
            urls = url
        else:
            raise TypeError("Url must be a string or list of strings")

        for url in urls:
            log(f"Getting Link : {url}")
            self.direct_download(url=url, trial=1)

    def run(self):

        while True:
            url = self.link.get_link()
            if not url:
                time.sleep(2)
                continue

            log(f"Getting Link : {url}")
            self.direct_download(url=url, trial=1)
            


if __name__  == "__main__":
    down = Downloader(del_link=True)
    down.save_path = "D:\\Downloads"
    down.run()
