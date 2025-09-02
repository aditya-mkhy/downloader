import os
from util import get_downloadpath, time_cal, data_size_cal, log, fpath, is_online, Status
import time
import requests
from threading import Thread, Timer
from urllib.parse import unquote
from delete import delete

class Downloader:
    def __init__(self, del_link: bool = False) -> None:
        #path to save the file
        self.save_path = get_downloadpath()
        self.del_link = del_link

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
                        this_file_path = os.path.abspath(__file__)
                        delete(file_path=this_file_path, data=url)
                    
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

                if self.del_link:
                    this_file_path = os.path.abspath(__file__)
                    delete(file_path=this_file_path, data=url)
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
                print("Chunk block is ended...")


            print("File is closed for good...")
            if status.downloaded_length == status.content_length:
                log(f"***** File Downloaded Success& size={data_size_cal(status.downloaded_length)} ************")
                log(f"File Downloaded : {file_path}")

                if self.del_link:
                    this_file_path = os.path.abspath(__file__)
                    delete(file_path=this_file_path, data=url)
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
            
            #download
            self.direct_download(url=url, trial=1)


if __name__  == "__main__":
    down = Downloader(del_link=True)
    down.save_path = "D:\\new"
    urls = [
        "https://worker-late-sunset-6792.hirah11663.workers.dev/ce37619eafcd30b47e3286e2aad51d56392915ef35fdc7bb9f697a06fa219d303793cb0136d869d8a6e6872dc84977ee247de5a9deb86f7dbcf0bfb66594265b853e30107925efd4cc0d3cda1b386e45b6f320cb5cd91841288b2882ed71e2820e7a60f919a3b8ad05a006c9e0a157da469d3809bba2aeeb2bb29e60543ebd7c8b435f2ab3a0058611421b5384d08a2151886118c3e22cc0fdb0ae1803e13883ebcde54cae3baaefb7809ae5ea67f11b::28ca267891d069db6dbe843f2f7c8f37/Star%20Trek%20Strange%20New%20Worlds%20S03E03%202160p%20AMZN%2010bit%20WEBDL%20SDR%20HEVC%20[Hindi%20DDP%202.0%20%20English%20(US)%20DDP%205.1%20%20English%20HEAAC%205.1]%20H.265%20(playWEBblackHAWK).mkv",
        "https://video-downloads.googleusercontent.com/ADGPM2nhVGHh3-EPNbZd9mgJLKP6xzNFT0UV37US3-6vPe5xOrrftPzFyuVnB6-DIraeOTetpUmnS-IgONugaMhAvLWwnl8j5CcfcSsPeb0laX5Jf5X3JiCf8ShkBrXQnE8pVl-RvrWn0jfVvT9k8AeZsN4RB_Z6IDCFOnfAjDDXE-woZYZ7vAa7PfvHUaE0jnLiI_z5lMXgTMhhAwPvqekVpLep9HzgnwAmQvYYTHbrVR-kg0W802T8AVEodRY6zOAL72c2Sg1yT8APG9fUA77g2VbhXYT1kzW7EWfySeZw_d8XAv2idlE37zl8eknjowW0jMYZUdIFubxBhapEbH9XZHCuh7el2Qs-xQbw1eaCzN2XqDNuiTXOgxIKEn1DE8By3uul3rcs1Qo5X2xZdJ2epRCCeXgn3EI7nzwBTAg0krSphR_SmStPwoOCP4EFvDEhjUG0z5z9_S_QiaV2KjwzK48LMgLHMBMqBAnaCzu0MMyStMhLAjWJTUuNPUmjDAQvBb27VWXyZdjwSxaGILcyL084u0zGtQP3MVBKuAyRn16c-7oWFYUtKjjUYxmwplwOmO8nKN1KTMQDhrXMFDUTxtrCWawlS-JOQKSVJMdmYtxY2yccQe-FtzwiD35KezxfWDSqv5TCqVTKl8G7Qm0m9Y3wTHjulHtGwGVp_qFQbhOzRhIjetqChbZCJ6aGWTO5lacCt2aOoX1QP5KGgb1rnjbYPydPV5slG8bcr1DyaSN4zikTCbyEA1X7qoI5HykCYq07pKwkYaRir6-S81UrCHu0S-0o_QkNL0-6Ip8wpUcDH5c6AsMfdmqnHK55qH9eq3FGUtH9q13ybK7fFK1jFH9IEbMmZrLcq6Pg70Mqo4UuZh95mheJOEGi7Cz0jBkjTbGWG0__H4_RP3AQ2Pq0gXVaFOnaSNTHsR1GEyT8LtrSSCsBTX5WtMItUeGcqkt7eImxS_9GasawRkf690_3C9vd7rBUgTYKOML33-WG70ThLXVw2Fq0ODA37NWhJk1UzWR7jeolbghgNoaf6mBOBoUScQ7oQw2-E6W1dYtsrYXsaHlCtTc",
        "https://worker-shiny-darkness-7632.momisad139.workers.dev/e03d18cdc26632858fc53dc40e74544a46a89dc81b315f8dcaedb7d281f60796bc924499f5456a1933e3a1df5b35e0a2cf1015601dda65e0a42d152f0074be259fbafab5cfe9a197719ab10ef166b5eec7523f2f42d20e6fdbe832e6f0ce5f31d69f0852034526c11da450332649e8bbcd62a353125d4dd91901e1e993d1e712c87e0ce35f3a1c80301cb5b782f0db02cfc29d727f3e40404a363259f57a0bdb2be2ed36afb98c7b9ce68bcba564a0ee::e7cae72f674ab8cc1cda51abc8fb9776/Star%20Trek%20Strange%20New%20Worlds%20S03E06%202160p%20ATV%2010bit%20WEBDL%20SDR%20HEVC%20[Hindi%20AAC%202.0%20%20English%20DDP%205.1]%20H.265%20(FLUXUHDMovies.com).mkv",
        "https://worker-divine-shadow-a960.milodo8102.workers.dev/b17cfd401e9c18e5883d4dd36eb7ca7dd629eba8f12571cd4ead92c8af0bf130fde0326d4f6f1a86682d4a53cb9400ae086b9ca69ff79bfe2ff1b8b42f961bedd244ec5b17fefb5b931cd89f1c5f465ce3b0019197e3c15fa47d1e3c6a6e6e78515d50545bed74b5087bb670f7709f073b371d5583834241f27be0f2f84e243079c2a45f21f678e27c2c14a52a0175ba98cd07ce8b8ca5c6251ea50efc403365dd7acbfa87f84d53106434a59d6862d9::9c507b2e3fe503832c4adb8a07271749/Star%20Trek%20Strange%20New%20Worlds%20S03E05%202160p%20ATV%2010bit%20WEBDL%20SDR%20HEVC%20[Hindi%20AAC%202.0%20%20English%20DDP%205.1]%20H.265%20(FLUXUHDMovies.com).mkv",
        "https://worker-super-union-d948.dirif80372.workers.dev/8658ebecb90816c6b5b64c9f2176e3740f3fb5cdb8b4324723923338d74c305c8dc4b949bdd446a3fba87458cc1de236bc3d48142d099d6c11598870fd90559a9694c70dd6fabf0ad765093d03efd3cff9974454eeecf8d44165f145c9dd4c334f258eef98dbbdd4a872991a9de07c6802f7194c8eb4dd0190961e28b61fd15d8a5984c6db4d6ced329f4c7bb33b524d23fbbf9b0c70ce99861c5e479c188a5f4ce525e6aa407788dd76dcc1a90dc58b::d88259e98991062e34a7872ae0d0d1df/Star.Trek.Strange.New.Worlds.S03E02.Wedding.Bell.Blues.2160p.HS.WEBDL.MULTI.DDP5.1.H.265Telly.mkv",
    ]   

    down.download(url=urls)

