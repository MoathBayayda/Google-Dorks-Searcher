# import ctypes
import os
import os.path
import platform
import re
import subprocess
import sys
import threading
import time
import requests
from colorama import init, Fore, Style



init(autoreset=True)
ascii_art = """

        ┏┓      ┓    ┳┓    ┓    ┏┓       ┓     
        ┃┓┏┓┏┓┏┓┃┏┓  ┃┃┏┓┏┓┃┏┏  ┗┓┏┓┏┓┏┓┏┣┓┏┓┏┓
        ┗┛┗┛┗┛┗┫┗┗   ┻┛┗┛┛ ┛┗┛  ┗┛┗ ┗┻┛ ┗┛┗┗ ┛ 
               ┛                               
       
                                                                                                   
"""

made_by = """





"""
lock = threading.Lock()
dorks_dir = ''
max_number_of_threads = 0
dorks_files_paths = []
total_dorks = 0
working_threads = 0
loaded_dorks = 0
total_urls = 0
urls_file_counter = 0
max_limit_url_file = 100000
search_engines = ['google']
dorks_with_no_result = 0
urls_in_current_file = 0
url_per_m = 0
progress = 0
is_stopped = False
failed_dorks = 0
finished_threads = 0


def searcherThread(dorks, search_engine):
    global total_urls, urls_file_counter, finished_threads, max_limit_url_file, working_threads, dorks_with_no_result, urls_in_current_file, failed_dorks, loaded_dorks

    for dork in dorks:
        lock.acquire()
        loaded_dorks += 1
        lock.release()

        try:
            response = requests.post(url='https://instance.qparser.cloud/659a81a15ea8a062aa638a80a36ba89f6fa869/google',
                                     json={"google": dork})

            data = response.json()
            encoded_links = data['message']
            ascii_links = [int(encoded_links[i:i + 3]) for i in range(0, len(encoded_links), 3)]
            decoded_links = ''.join(chr(value) for value in ascii_links)

            if decoded_links == "Failed to parse":
                lock.acquire()
                dorks_with_no_result += 1
                lock.release()

            else:
                links = re.findall(r'https?://[^\s]+', decoded_links)

                if len(links) == 0:
                    lock.acquire()

                    dorks_with_no_result += 1
                    lock.release()
                lock.acquire()
                total_urls += len(links)

                urls_in_current_file += len(links)
                lock.release()
                with open(f"./result/urls_{search_engine}_{urls_file_counter}.txt", 'a') as urls_file:
                    for link in links:
                        urls_file.write(link + "\n")
                    urls_file.close()

                if urls_in_current_file >= max_limit_url_file:
                    lock.acquire()
                    urls_in_current_file = 0
                    urls_file_counter += 1
                    lock.release()
                time.sleep(0.5)

        except ValueError as ve:
            # print(f"{Fore.RED} Bad request: {ve}")
            lock.acquire()
            failed_dorks += 1

            with open(f"./failed_dorks/dorks_{search_engine}_{urls_file_counter}.txt", 'a') as failed_dorks_file:
                failed_dorks_file.write(dork + "\n")
                failed_dorks_file.close()

            lock.release()
            continue

        except Exception as e:
            print(f"An error occurred: {e}")
            lock.acquire()

            failed_dorks += 1

            with open(f"./failed_dorks/dorks_{search_engine}_{urls_file_counter}.txt", 'a') as failed_dorks_file:
                failed_dorks_file.write(dork + "\n")
                failed_dorks_file.close()

            lock.release()

            continue
    lock.acquire()
    finished_threads += 1
    working_threads -= 1
    lock.release()


def clear_terminal():
    # Determine the command based on the platform
    try:
        if platform.system() == "Windows":
            command = "cls"
        else:
            command = "clear"

        # Use subprocess to call the appropriate command
        subprocess.call(command, shell=True)
        if sys.platform.startswith("win"):
            # For Windows
            _ = sys.stdout.write("\033[H\033[2J")
        else:
            # For Linux and Mac
            _ = sys.stdout.write("\033c")
        sys.stdout.flush()
    except:
        sys.stdout.write(Fore.RED + Style.BRIGHT + "\n>Stopping ...\n")
        sys.stdout.write(Fore.RED + Style.BRIGHT + "Check files paths\n")
        is_aborted = True
        exit()


def totalDorksCalc():
    global dorks_files_paths, total_dorks

    try:
        for dork_file_path in dorks_files_paths:
            with open(dork_file_path, 'r') as dork_file:
                lock.acquire()
                total_dorks += len(dork_file.read().split("\n"))
                lock.release()

            dork_file.close()

    except Exception as e:
        print(f"{Fore.RED}\nError opening dorks{e}")


def loggerThread():
    global working_threads, loaded_dorks, max_number_of_threads, total_urls, dorks_with_no_result
    global total_dorks, failed_dorks, progress, finished_threads, finished_threads, is_stopped, url_per_m

    loading_symbols = ["/", "-", "\\", "|"]
    loading_symbol_counter = 0
    clear_terminal()

    while not is_stopped and finished_threads != max_number_of_threads:
        lock.acquire()
        clear_terminal()

        progress = ((loaded_dorks / total_dorks) * 100) // 1

        print(f"{Fore.GREEN}{ascii_art}")
        print(f"{Fore.GREEN}{made_by}")
        print(f"{Fore.GREEN}    [{Fore.BLUE}{loading_symbols[loading_symbol_counter]}{Fore.GREEN}] Generating urls ...")
        print(f"{Fore.GREEN}    Total dorks : {Fore.BLUE}{total_dorks}")
        print(f"{Fore.GREEN}    Working threads : {Fore.BLUE}{working_threads}")
        print(f"{Fore.GREEN}    Progress : {Fore.BLUE}{progress}%")
        print(f"{Fore.GREEN}    Loaded dorks : {Fore.BLUE}{loaded_dorks}")
        print(f"{Fore.GREEN}    Total generated urls : {Fore.YELLOW}{total_urls}")
        print(f"{Fore.GREEN}    Dorks with no result : {Fore.RED}{dorks_with_no_result}")
        print(f"{Fore.GREEN}    Failed dorks : {Fore.RED}{failed_dorks}")
        print(f"{Fore.GREEN}    Finished threads : {Fore.RED}{finished_threads}")
        print(f"{Fore.GREEN}    Url per minute : {Fore.BLUE}{url_per_m}")

        lock.release()

        time.sleep(1)

        move_up = "\033[F" * 27
        print(move_up, end='\r')

        loading_symbol_counter += 1

        if loading_symbol_counter >= len(loading_symbols):
            loading_symbol_counter = 0
    else:
        # move_up = "\033[F" * 23
        # print(move_up, end='\r')
        clear_terminal()
        lock.acquire()
        progress = ((loaded_dorks / total_dorks) * 100) // 1

        # progress = 100//1
        is_stopped = True
        print(f"{Fore.GREEN}{ascii_art}")
        print(f"{Fore.GREEN}{made_by}")
        print(f"{Fore.GREEN}    Finished  ...")
        print(f"{Fore.GREEN}    Total dorks : {Fore.BLUE}{total_dorks}")
        print(f"{Fore.GREEN}    Working threads : {Fore.BLUE}{working_threads}")
        print(f"{Fore.GREEN}    Progress : {Fore.BLUE}{progress}%")
        print(f"{Fore.GREEN}    Loaded dorks : {Fore.BLUE}{loaded_dorks}")
        print(f"{Fore.GREEN}    Total generated urls : {Fore.YELLOW}{total_urls}")
        print(f"{Fore.GREEN}    Dorks with no result : {Fore.RED}{dorks_with_no_result}")
        print(f"{Fore.GREEN}    Failed dorks : {Fore.RED}{failed_dorks}")
        print(f"{Fore.GREEN}    Finished threads : {Fore.RED}{finished_threads}")

        lock.release()

        # move_up = "\033[F" * 23
        # print(move_up, end='\r')

        loading_symbol_counter += 1

        if loading_symbol_counter >= len(loading_symbols):
            loading_symbol_counter = 0
        sys.exit()


def urlPerMCalc():
    global total_urls, url_per_m, is_stopped, max_number_of_threads, finished_threads

    while not is_stopped and max_number_of_threads != finished_threads:
        current_urls = total_urls
        time.sleep(60)
        lock.acquire()

        url_per_m = total_urls - current_urls

        lock.release()


def searchEnginesHandler():
    global search_engines, total_dorks, max_number_of_threads, working_threads, dorks_files_paths

    dorks_per_thread = total_dorks // max_number_of_threads

    try:
        if max_number_of_threads > total_dorks:
            lock.acquire()

            max_number_of_threads = total_dorks

            lock.release()

        for search_engine in search_engines:

            for dork_file_path in dorks_files_paths:

                read_dorks_lines = 0

                with open(dork_file_path, 'r') as dork_file:

                    dorks = dork_file.read().split("\n")

                    while read_dorks_lines <= len(dorks) and read_dorks_lines + dorks_per_thread <= len(dorks):
                        dorks_thread = threading.Thread(target=searcherThread, args=(
                            dorks[read_dorks_lines:read_dorks_lines + dorks_per_thread], search_engine))
                        time.sleep(0.5)
                        dorks_thread.start()
                        lock.acquire()

                        working_threads += 1

                        lock.release()

                        if working_threads > max_number_of_threads:
                            dorks_thread.join()

                        read_dorks_lines += dorks_per_thread
                    else:
                        if read_dorks_lines < len(dorks):
                            dorks_thread = threading.Thread(target=searcherThread,
                                                            args=(dorks[read_dorks_lines:], search_engine))

                            dorks_thread.start()

                            lock.acquire()

                            working_threads += 1

                            lock.release()

                            if working_threads > max_number_of_threads:
                                dorks_thread.join()

    except Exception as e:
        print(f"{Fore.RED}\nError opening dorks {e}")


def main():
    global dorks_dir, max_number_of_threads, total_dorks, working_threads, loaded_dorks, is_stopped

    print(f"{Fore.GREEN}{ascii_art}\n")
    print(f"{Fore.GREEN}{made_by}\n")
    print(f"{Fore.GREEN}> Enter the dorks folder path, example : c\\users\\dorks")
    print(f"{Fore.GREEN}> Note only .txt are supported")

    dorks_dir = input(f"{Fore.GREEN}> ")

    print(f"{Fore.GREEN}> Enter number of threads")
    max_number_of_threads = int(input(f"{Fore.GREEN}> "))

    try:
        for dork_file_path in os.listdir(dorks_dir):
            if dork_file_path.split('.')[1] == 'txt':
                dorks_files_paths.append(os.path.join(dorks_dir, dork_file_path))

        if len(dorks_files_paths) == 0:
            print(f"{Fore.RED}\nFolder is empty")
            return None

        if max_number_of_threads <= 0:
            print(f"{Fore.RED}\nNumber of thread must be greater than 0")
            return None

        total_dorks_thread = threading.Thread(target=totalDorksCalc)
        total_dorks_thread.start()
        total_dorks_thread.join()

        if total_dorks == 0:
            print(f"{Fore.RED}\nAll Dorks files are empty")
            return None

        logger_thread = threading.Thread(target=loggerThread)
        url_per_m = threading.Thread(target=urlPerMCalc)

        logger_thread.start()
        url_per_m.start()


        searchEnginesHandler()

        logger_thread.join()
        url_per_m.join()

    except Exception as e:
        print(f"{Fore.RED}\nError opening dorks{e}")
        is_stopped = True


main()