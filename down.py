import os
from util import get_downloadpath, time_cal, data_size_cal, log, fpath, is_online, Status
import time
import requests
import queue
from threading import Thread, Timer

class Down:
    def __init__(self) -> None:
        #path to save the file
        self.save_path = get_downloadpath()

        # chunk size
        self.chunk = 8485


    def remove_symbol_from_filename(self, filename: str):
        return filename.replace("%20", " ")
    
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

                        # print(f"Paths:ContentDisciption : {fileName}")
                        return fileName
            except Exception as e:
                print(f"Failed to find the path from hearder : {e}")
        
        

        if url:
            try:

                fileName = url[url.rfind("/")+1 : ]
                fileName = self.remove_symbol_from_filename(fileName)
                popExt = [".webm", ".mkv", ".png", ".exe", ".iso", ".zip", ".wmv", ".wav", ".txt",
                                ".pdf", ".msi", ".mp4", ".mp3", ".m4a", ".jpg", "jpej", ".jar", ".iso", ".html"]

                path, ext = os.path.splitext(fileName)
                if ext in popExt:
                    # print(f"Paths:Urls : {fileName}")
                    return fileName
                
                else:
                    # print(f"Sepecific File Format is Not Found...{fileName}")
                    if ext  != "":
                        return fileName
                    
                    else:
                        return False
                    
            except Exception as e:
                print(f"Failed to find path from url : {e}")
            
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
            from_byte = os.stat(fpath).st_size

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
            status = self.save(response=response, file_path=file_path, content_length=content_length, from_byte=from_byte)

            #checking save status...
            if not status:
                if not is_online():
                    return "offline"

                if trial >= 5:
                    log("Maximum trial ended... now cancelling this file..")
                    return "Error"
                
                log(f"Trying again.. trial number : {trial}")
                return self.direct_download(url=url, trial=trial + 1)
            
            log(f"File downloaded : {file_path}")
            return status

        else:
            log(f"Error[11]: Status_Code==> {response.status_code}")
            print(f"coockies==> {response.cookies.items()}")
            print(f"Header==> {response.headers}")
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
                return True
            
            else:
                log("Error[]: Not able to downnload file.. please check it manually..")
                return False
            

    def __store(self, tf, status:  Status):
        while True:
            data = status.data_queue.get()
            if data is None:
                print("error[08]: data is none")
                break
            # write data
            tf.write(data)

            if status.stop and status.data_queue.empty():
                print("info[001] : Stopping the writing...")
                break

    def save(self, response,  file_path, content_length, from_byte):
        mode = "wb"
        if from_byte != 0:
            mode = "ab"

        status = Status()
        status.content_length = content_length
        
        try:
            with open(file_path, mode) as tf:
                status.downloaded_length = tf.tell()
                log("Downloading....")

                status.write_thr = Thread(target=self.__store, args=(tf, status), daemon=True)
                status.write_thr.start()

                status.progress_thr = Thread(target=self.update_progress, args=(status, ), daemon=True)
                status.progress_thr.start()

                for chunk in response.iter_content(self.chunk):
                    if chunk: # filter out keep-alive new chunks
                        status.data_queue.put(chunk)
                        status.downloaded_length += len(chunk)

                status.stop = True
                print("Chunk block is ended...")


            print("File is closed for good...")
            if status.downloaded_length == status.content_length:
                log(f"***** File Downloaded Success& size={data_size_cal(status.downloaded_length)} ************")
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
        
        Timer(2.0, self.update_progress, (status, )).start()

        content_length = status.content_length
        downloaded_length = status.downloaded_length
        prev_length = status.prev_length

        # saving the current downloaded_length to prev_length
        status.prev_length = downloaded_length
        per_sec_size = (downloaded_length - prev_length) //2

        try:
            timest = f"{time_cal((content_length - downloaded_length) // per_sec_size)} left"
        except:
            timest = "Cal.."

        speed = f"({data_size_cal(downloaded_length)} of {data_size_cal(content_length)} , {data_size_cal(per_sec_size)}/Sec)"
        print(f"  {speed}   {timest}                          ", end='\r')



    def download(self, url: list):
        if isinstance(url, str):
            urls = [urls]

        elif isinstance(url, list):
            urls = url

        else:
            raise TypeError("Url must be a string or list of strings")
        

        for url in urls:
            log(f"Getting Link : {url}")
            
            #download
            self.direct_download(url=url, trial=1)

        
if __name__  == "__main__":
    down = Down()
    
    urls = [
        "https://worker-mute-frost-7a43.cemeso9920.workers.dev/696bd82969437f67d69658e661e1156a8c22a2c12ef2d69affb33198907b52aa78e88adc9c72059ecab0a5a3b66a3336011395b9789625cc2c0284a12229757f3a353b5600acc2df6efff5324356ecad79e82f23ed4df7746460adcd7d12bed930f831d7fc75c49be286f5e683810ca8d105abab7b735ec8da068a9157e86e1789e1dba5b835338e9a6a370345c00d7c1aa6699701d4078ef3cc8aea5d2a3742fa41c06de2ea0561902d35cd4a926a54::2044f41c3b4a0b4fe66784604b11acfe/Lamborghini%20%20The%20Man%20Behind%20the%20Legend%20(2022)%201080p%20BluRay%20[Hindi%20DDP%202.0%20%20English%20DTS%205.1]%20x264%20(HDSUHDMovies).mkv"

    ]

    down.download(url=urls)