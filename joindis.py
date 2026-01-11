import sys, os, time, uuid, json, base64, traceback
import requests
import tls_client
import re
import random
import string
import queue
import webbrowser
from io import BytesIO
import zipfile
from datetime import datetime as dt
from concurrent.futures import ThreadPoolExecutor
from pystyle import Colors, Colorate

DBG = False
VERSION = 4.2
sys.dont_write_bytecode = True
os.environ['PYTHONDONTWRITEBYTECODE'] = '1'

GIAKIET_BANNER = r"""

  ██░ ██  ██▓ ██▓███    ██████   ██████ ▓█████ ▓█████ ▓█████▄     ██▓███  ▓██   ██▓
 ▓██░ ██▒▓██▒▓██░  ██▒▒██    ▒ ▒██    ▒ ▓█   ▀ ▓█   ▀ ▒██▀ ██▌   ▓██░  ██▒ ▒██  ██▒
 ▒██▀▀██░▒██▒▓██░ ██▓▒░ ▓██▄   ░ ▓██▄   ▒███   ▒███   ░██   █▌   ▓██░ ██▓▒  ▒██ ██░
 ░▓█ ░██ ░██░▒██▄█▓▒ ▒  ▒   ██▒  ▒   ██▒▒▓█  ▄ ▒▓█  ▄ ░▓█▄   ▌   ▒██▄█▓▒ ▒  ░ ▐██▓░
 ░▓█▒░██▓░██░▒██▒ ░  ░▒██████▒▒▒██████▒▒░▒████▒░▒████▒░▒████▓    ▒██▒ ░  ░  ░ ██▒▓░
  ▒ ░░▒░▒░▓  ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░░ ▒░ ░░░ ▒░ ░ ▒▒▓  ▒    ▒▓▒░ ░  ░   ██▒▒▒ 
  ▒ ░▒░ ░ ▒ ░░▒ ░     ░ ░▒  ░ ░░ ░▒  ░ ░ ░ ░  ░ ░ ░  ░ ░ ▒  ▒    ░▒ ░      ▓██ ░▒░ 
  ░  ░░ ░ ▒ ░░░       ░  ░  ░  ░  ░  ░     ░      ░    ░ ░  ░    ░░        ▒ ▒ ░░  
  ░  ░  ░ ░                 ░        ░     ░  ░   ░  ░   ░                 ░ ░     
                                                        ░                 ░ ░                                                   
                                                                                         
"""

JOINER_BANNER = r"""
      ██ ▄█▀ ▒█████   ██▀███   █    ██ ▓█████  ██▀███  
      ██▄█▒ ▒██▒  ██▒▓██ ▒ ██▒ ██  ▓██▒▓█   ▀ ▓██ ▒ ██▒
     ▓███▄░ ▒██░  ██▒▓██ ░▄█ ▒▓██  ▒██░▒███   ▓██ ░▄█ ▒
     ▓██ █▄ ▒██   ██░▒██▀▀█▄  ▓▓█  ░██░▒▓█  ▄ ▒██▀▀█▄  
     ▒██▒ █▄░ ████▓▒░░██▓ ▒██▒▒▒█████▓ ░▒████▒░██▓ ▒██▒
     ▒ ▒▒ ▓▒░ ▒░▒░▒░ ░ ▒▓ ░▒▓░░▒▓▒ ▒ ▒ ░░ ▒░ ░░ ▒▓ ░▒▓░
     ░ ░▒ ▒░  ░ ▒ ▒░   ░▒ ░ ▒░░░▒░ ░ ░  ░ ░  ░  ░▒ ░ ▒░
     ░ ░░ ░ ░ ░ ░ ▒    ░░   ░  ░░░ ░ ░    ░     ░░   ░ 
     ░  ░       ░ ░     ░        ░        ░  ░   ░       
                                                               
"""

LEAVER_BANNER = r"""
                              
      ██▓    ▓█████  ▄▄▄       ██▒   ██▒▓█████  ██▀███  
     ▓██▒    ▓█   ▀ ▒████▄    ▓██░   ██░▓█   ▀ ▓██ ▒ ██▒
     ▒██░    ▒███   ▒██  ▀█▄   ▓██  ██▓▒▒███   ▓██ ░▄█ ▒
     ▒██░    ▒▓█  ▄ ░██▄▄▄▄██   ▒██ ██░ ▒▓█  ▄ ▒██▀▀█▄  
     ░██████▒░▒████▒ ▓█   ▓██▒   ▒▀█░   ░▒████▒░██▓ ▒██▒
     ░ ▒░▓  ░░░ ▒░ ░ ▒▒   ▓▒█░   ░ ▐░   ░░ ▒░ ░░ ▒▓ ░▒▓░
     ░ ░ ▒  ░ ░ ░  ░  ▒   ▒▒ ░   ░ ░░    ░ ░  ░  ░▒ ░ ▒░
       ░ ░      ░     ░   ▒        ░░      ░     ░░   ░ 
         ░  ░   ░  ░      ░  ░      ░      ░  ░   ░     
                               
                                  
"""

RENAME_BANNER = r"""
 ██▀███  ▓█████  ███▄ ▄███▓ ▄▄▄       ███▄ ▄███▓▓█████ 
▓██ ▒ ██▒▓█   ▀ ▓██▒▀█▀ ██▒▒████▄    ▓██▒▀█▀ ██▒▓█   ▀ 
▓██ ░▄█ ▒▒███   ▓██    ▓██░▒██  ▀█▄  ▓██    ▓██░▒███   
▒██▀▀█▄  ▒▓█  ▄ ▒██    ▒██ ░██▄▄▄▄██ ▒██    ▒██ ▒▓█  ▄ 
░██▓ ▒██▒░▒████▒▒██▒   ░██▒ ▓█   ▓██▒▒██▒   ░██▒░▒████▒
░ ▒▓ ░▒▓░░░ ▒░ ░░ ▒░   ░  ░ ▒▒   ▓▒█░░ ▒░   ░  ░░░ ▒░ ░
  ░▒ ░ ▒░ ░ ░  ░░  ░      ░  ▒   ▒▒ ░░  ░      ░ ░ ░  ░
  ░░   ░    ░   ░      ░     ░   ▒   ░      ░      ░   
   ░        ░  ░       ░         ░  ░       ░      ░  ░                                           
                                                                                
"""

PRONOUN_BANNER = r"""
  ██████  ▓█████ ▄▄▄       ▄▄▄▄    █    ██  ███▄    █   ██████ 
▒██    ▒  ▓█   ▀▒████▄    ▓█████▄  ██  ▓██▒ ██ ▀█   █ ▒██    ▒ 
░ ▓██▄    ▒███  ▒██  ▀█▄  ▒██▒ ▄██▓██  ▒██░▓██  ▀█ ██▒░ ▓██▄   
  ▒   ██▒ ▒▓█  ▄░██▄▄▄▄██ ▒██░█▀  ▓▓█  ░██░▓██▒  ▐▌██▒  ▒   ██▒
▒██████▒▒ ░▒████▒▓█   ▓██▒░▓█  ▀█▓▒▒█████▓ ▒██░   ▓██░▒██████▒▒
▒ ▒▓▒ ▒ ░  ░ ▒░ ░▒▒   ▓▒█░░▒▓███▀▒░▒▓▒ ▒ ▒ ░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░
░ ░▒  ░ ░  ░ ░  ░ ▒   ▒▒ ░▒░▒   ░ ░░▒░ ░ ░ ░ ░░   ░ ▒░░ ░▒  ░ ░
░  ░  ░      ░    ░   ▒    ░    ░  ░░░ ░ ░    ░   ░ ░ ░  ░  ░  
      ░      ░  ░     ░  ░ ░         ░              ░       ░  
                                              
                                                                                          
"""

BIO_BANNER = r"""
  ██████ ▓█████ ▄▄▄       ▄▄▄▄   ▒█████  
▒██    ▒ ▓█   ▀▒████▄    ▓█████▄▒██▒  ██▒
░ ▓██▄   ▒███  ▒██  ▀█▄  ▒██▒ ▄██▒██░  ██▒
  ▒   ██▒▒▓█  ▄░██▄▄▄▄██ ▒██░█▀  ▒██   ██░
▒██████▒▒░▒████▒▓█   ▓██▒░▓█  ▀█▓░ ████▓▒░
▒ ▒▓▒ ▒ ░░░ ▒░ ░▒▒   ▓▒█░░▒▓███▀▒░ ▒░▒░▒░ 
░ ░▒  ░ ░ ░ ░  ░ ▒   ▒▒ ░▒░▒   ░   ░ ▒ ▒░ 
░  ░  ░     ░    ░   ▒    ░    ░ ░ ░ ░ ▒  
      ░     ░  ░     ░  ░ ░          ░ ░  
                    
"""

AVATAR_BANNER = r"""
  ██████  ▓█████ ▄▄▄       ▄▄▄▄   ▒██   ██▒▄▄▄█████▓ ▄▄▄      
▒██    ▒  ▓█   ▀▒████▄    ▓█████▄ ▒▒ █ █ ▒░▓  ██▒ ▓▒▒████▄    
░ ▓██▄    ▒███  ▒██  ▀█▄  ▒██▒ ▄██░░  █   ░▒ ▓██░ ▒░▒██  ▀█▄  
  ▒   ██▒ ▒▓█  ▄░██▄▄▄▄██ ▒██░█▀   ░ █ █ ▒ ░ ▓██▓ ░ ░██▄▄▄▄██ 
▒██████▒▒ ░▒████▒▓█   ▓██▒░▓█  ▀█▓▒██▒ ▒██▒  ▒██▒ ░  ▓█   ▓██▒
▒ ▒▓▒ ▒ ░  ░ ▒░ ░▒▒   ▓▒█░░▒▓███▀▒▒▒ ░ ░▓ ░  ▒ ░░    ▒▒   ▓▒█░
░ ░▒  ░ ░  ░ ░  ░ ▒   ▒▒ ░▒░▒   ░ ░░   ░▒ ░    ░      ▒   ▒▒ ░
░  ░  ░      ░    ░   ▒    ░    ░  ░    ░    ░        ░   ▒   
      ░      ░  ░     ░  ░ ░         ░    ░             ░  ░
                                        
"""
REMOVE_AVATAR_BANNER = r"""
 ██████  ▓█████  ███▄    █  ▄▄▄        ██████ ▄▄▄█████▓ ▄▄▄      
▒██    ▒  ▓█   ▀  ██ ▀█   █ ▒████▄    ▒██    ▒ ▓  ██▒ ▓▒▒████▄    
░ ▓██▄    ▒███   ▓██  ▀█ ██▒▒██  ▀█▄  ░ ▓██▄   ▒ ▓██░ ▒░▒██  ▀█▄  
  ▒   ██▒ ▒▓█  ▄ ▓██▒  ▐▌██▒░██▄▄▄▄██   ▒   ██▒░ ▓██▓ ░ ░██▄▄▄▄██ 
▒██████▒▒ ░▒████▒▒██░   ▓██░ ▓█   ▓██▒▒██████▒▒  ▒██▒ ░  ▓█   ▓██▒
▒ ▒▓▒ ▒ ░  ░ ▒░ ░░ ▒░   ▒ ▒  ▒▒   ▓▒█░▒ ▒▓▒ ▒ ░  ▒ ░░    ▒▒   ▓▒█░
░ ░▒  ░ ░  ░ ░  ░░ ░░   ░ ▒░  ▒   ▒▒ ░░ ░▒  ░ ░    ░      ▒   ▒▒ ░
░  ░  ░      ░      ░   ░ ░   ░   ▒   ░  ░  ░    ░        ░   ▒   
      ░      ░  ░         ░       ░  ░      ░             ░  ░
  
                                                               
                                                                     
"""
REMOVE_BIO_BANNER = r"""
 ██████  ▓█████  ███▄    █   ██████  ▒█████  
▒██    ▒  ▓█   ▀  ██ ▀█   █ ▒██    ▒ ▒██▒  ██▒
░ ▓██▄    ▒███   ▓██  ▀█ ██▒░ ▓██▄   ▒██░  ██▒
  ▒   ██▒ ▒▓█  ▄ ▓██▒  ▐▌██▒  ▒   ██▒▒██   ██░
▒██████▒▒ ░▒████▒▒██░   ▓██░▒██████▒▒░ ████▓▒░
▒ ▒▓▒ ▒ ░  ░ ▒░ ░░ ▒░   ▒ ▒ ▒ ▒▓▒ ▒ ░░ ▒░▒░▒░ 
░ ░▒  ░ ░  ░ ░  ░░ ░░   ░ ▒░░ ░▒  ░ ░  ░ ▒ ▒░ 
░  ░  ░      ░      ░   ░ ░ ░  ░  ░  ░ ░ ░ ▒  
      ░      ░  ░         ░       ░      ░ ░  

                                             
                                             
"""

REMOVE_PRONOUN_BANNER = r"""
 ██████  ▓█████  ███▄    █  ▒█████   █     █░▓█████ 
▒██    ▒  ▓█   ▀  ██ ▀█   █ ▒██▒  ██▒▓█░ █ ░█░▓█   ▀ 
░ ▓██▄    ▒███   ▓██  ▀█ ██▒▒██░  ██▒▒█░ █ ░█ ▒███   
  ▒   ██▒ ▒▓█  ▄ ▓██▒  ▐▌██▒▒██   ██░░█░ █ ░█ ▒▓█  ▄ 
▒██████▒▒ ░▒████▒▒██░   ▓██░░ ████▓▒░░░██▒██▓ ░▒████▒
▒ ▒▓▒ ▒ ░  ░ ▒░ ░░ ▒░   ▒ ▒ ░ ▒░▒░▒░ ░ ▓░▒ ▒  ░░ ▒░ ░
░ ░▒  ░ ░  ░ ░  ░░ ░░   ░ ▒░  ░ ▒ ▒░   ▒ ░ ░   ░ ░  ░
░  ░  ░      ░      ░   ░ ░ ░ ░ ░ ▒    ░   ░     ░   
      ░      ░  ░         ░     ░ ░      ░       ░  ░

                                                                           
                                                                                                                      
"""

REMOVE_NAME_BANNER = r"""
 ██▀███  ▓█████  ███▄ ▄███▓ ▒█████   ██▒   █▓▓█████ 
▓██ ▒ ██▒▓█   ▀ ▓██▒▀█▀ ██▒▒██▒  ██▒▓██░   █▒▓█   ▀ 
▓██ ░▄█ ▒▒███   ▓██    ▓██░▒██░  ██▒ ▓██  █▒░▒███   
▒██▀▀█▄  ▒▓█  ▄ ▓██    ▒██ ▒██   ██░  ▒██ █░░▒▓█  ▄ 
░██▓ ▒██▒░▒████▒▒██▒   ░██▒░ ████▓▒░   ▒▀█░  ░▒████▒
░ ▒▓ ░▒▓░░░ ▒░ ░░ ▒░   ░  ░░ ▒░▒░▒░    ░ ▐░  ░░ ▒░ ░
  ░▒ ░ ▒░ ░ ░  ░░  ░      ░  ░ ▒ ▒░    ░ ░░   ░ ░  ░
  ░░   ░    ░   ░      ░   ░ ░ ░ ▒       ░░     ░   
   ░        ░  ░       ░       ░ ░        ░     ░  ░
                                                      
                                                                                                                       
"""

CHECK_TOKEN_BANNER = r"""
 ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀      ▄▄▄▄    ██▓ ██▓▓█████ 
▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒      ▓█████▄ ▓██▒ ██▒▓█   ▀ 
▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░      ▒██▒ ▄██▒██░ ██░▒███   
▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄      ▒██░█▀  ░██  ██░▒▓█  ▄ 
▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄     ░▓█  ▀█▓░▒████▒░░▒████▒
░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒     ░▒▓███▀▒░░ ▒░ ░ ░░ ▒░ ░
  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░     ▒░

                                                                        
                                                                        
"""

CHECK_SERVER_BANNER = r"""
 ▄████▄   ██░ ██ ▓█████  ▄████▄   ██ ▄█▀      ██████ ▓█████ ▓█████  ██▒   █▓▓█████  ██▀███  
▒██▀ ▀█  ▓██░ ██▒▓█   ▀ ▒██▀ ▀█   ██▄█▒      ▒██    ▒ ▓█   ▀ ▓█   ▀ ▓██░   █▒▓█   ▀ ▓██ ▒ ██▒
▒▓█    ▄ ▒██▀▀██░▒███   ▒▓█    ▄ ▓███▄░      ░ ▓██▄   ▒███   ▒███    ▓██  █▒░▒███   ▓██ ░▄█ ▒
▒▓▓▄ ▄██▒░▓█ ░██ ▒▓█  ▄ ▒▓▓▄ ▄██▒▓██ █▄        ▒   ██▒▒▓█  ▄ ▒▓█  ▄   ▒██ █░░▒▓█  ▄ ▒██▀▀█▄  
▒ ▓███▀ ░░▓█▒░██▓░▒████▒▒ ▓███▀ ░▒██▒ █▄     ▒██████▒▒░▒████▒░▒████▒   ▒▀█░  ░▒████▒░██▓ ▒██▒
░ ░▒ ▒  ░ ▒ ░░▒░▒░░ ▒░ ░░ ░▒ ▒  ░▒ ▒▒ ▓▒     ▒ ▒▓▒ ▒ ░░░ ▒░ ░░░ ▒░ ░   ░ ▐░  ░░ ▒░ ░░ ▒▓ ░▒▓░
  ░  ▒    ▒ ░▒░ ░ ░ ░  ░  ░  ▒   ░ ░▒ ▒░     ░ ░▒  ░ ░ ░ ░  ░ ░ ░  ░   ░ ░░   ░ ░  ░  ░▒ ░ ▒░
░         ░  ░░ ░   ░   ░        ░ ░░ ░      ░  ░  ░     ░      ░        ░░     ░     ░░   ░ 
░ ░       ░  ░  ░   ░  ░░ ░      ░  ░              ░     ░  ░   ░  ░      ░     ░  ░   ░     
░                       ░                                           ░                         
   
                                                                          
                                                                             
"""

KEY_BANNER = r"""

  ██░ ██  ██▓ ██▓███    ██████   ██████ ▓█████ ▓█████ ▓█████▄     ██▓███  ▓██   ██▓
 ▓██░ ██▒▓██▒▓██░  ██▒▒██    ▒ ▒██    ▒ ▓█   ▀ ▓█   ▀ ▒██▀ ██▌   ▓██░  ██▒ ▒██  ██▒
 ▒██▀▀██░▒██▒▓██░ ██▓▒░ ▓██▄   ░ ▓██▄   ▒███   ▒███   ░██   █▌   ▓██░ ██▓▒  ▒██ ██░
 ░▓█ ░██ ░██░▒██▄█▓▒ ▒  ▒   ██▒  ▒   ██▒▒▓█  ▄ ▒▓█  ▄ ░▓█▄   ▌   ▒██▄█▓▒ ▒  ░ ▐██▓░
 ░▓█▒░██▓░██░▒██▒ ░  ░▒██████▒▒▒██████▒▒░▒████▒░▒████▒░▒████▓    ▒██▒ ░  ░  ░ ██▒▓░
  ▒ ░░▒░▒░▓  ▒▓▒░ ░  ░▒ ▒▓▒ ▒ ░▒ ▒▓▒ ▒ ░░░ ▒░ ░░░ ▒░ ░ ▒▒▓  ▒    ▒▓▒░ ░  ░   ██▒▒▒ 
  ▒ ░▒░ ░ ▒ ░░▒ ░     ░ ░▒  ░ ░░ ░▒  ░ ░ ░ ░  ░ ░ ░  ░ ░ ▒  ▒    ░▒ ░      ▓██ ░▒░ 
  ░  ░░ ░ ▒ ░░░       ░  ░  ░  ░  ░  ░     ░      ░    ░ ░  ░    ░░        ▒ ▒ ░░  
  ░  ░  ░ ░                 ░        ░     ░  ░   ░  ░   ░                 ░ ░     
                                                        ░                 ░ ░ 
                                                 
                                                 
"""

def clear_screen():
    if os.name == 'nt':  
        os.system('cls')
    else: 
        os.system('clear')

def get_terminal_size():
    try:
        return os.get_terminal_size().columns
    except:
        return 80 

size = get_terminal_size()
THEME_COLORS = [
    Colors.yellow_to_green,
    Colors.yellow_to_red,
    Colors.red_to_yellow,
    Colors.red_to_green,
    Colors.red_to_blue,
    Colors.red_to_purple,
    Colors.red_to_white,
    Colors.green_to_yellow,
    Colors.green_to_red,
    Colors.green_to_blue,
    Colors.green_to_cyan,
    Colors.green_to_white,
    Colors.blue_to_red,
    Colors.blue_to_green,
    Colors.blue_to_cyan,
    Colors.blue_to_purple,
    Colors.blue_to_white,
    Colors.cyan_to_green,
    Colors.cyan_to_blue,
    Colors.purple_to_red,
    Colors.purple_to_blue,
    Colors.white_to_red,
    Colors.white_to_green,
    Colors.white_to_blue,
    Colors.rainbow
]
THEME_COLOR = random.choice(THEME_COLORS)
def print_animated_intro():
    clear_screen()
    ascii_lines = GIAKIET_BANNER.splitlines()
    centered_ascii = [line.center(size) for line in ascii_lines]
    print(Colorate.Vertical(THEME_COLOR, "\n".join(centered_ascii)))
    print()
    
    version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
    print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
    print()
    
    current_time = dt.now().strftime("%H:%M:%S")
    info_text = f"Started at {current_time}"
    print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
    print()
    
    tokens = len(files().gettokens())
    proxies = len(files().getproxies())
    stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
    print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
    print()
    time.sleep(0.000001)

class log:
    @staticmethod
    def basic(ts=False, color=Colors.green_to_cyan, message='None', type=None):
        try:
            if type == 'info':
                type = ''
            elif type == 'error':
                type = ''
            elif type == 'warning':
                type = ''
            elif type == 'debug':
                type = ''
            elif type is None:
                type = ''
            else:
                type = ''

            print(f"{Colorate.Horizontal(color, f'{message}')}")
        except Exception as e:
            print(f"Log error: {str(e)}")
    
    @staticmethod
    def info(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Horizontal(Colors.green_to_cyan, f'[{module}] | {message}')} ")
            else:
                print(f"{Colorate.Horizontal(Colors.green_to_cyan, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Info log error: {str(e)}")

    @staticmethod
    def dbg(module, *message):
        try:
            if DBG:
                if len(message) == 1 and isinstance(message[0], str):
                    message = [message[0]]
                message = ' | '.join(map(str, message))
                print(f"{Colorate.Horizontal(Colors.green_to_cyan, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Debug log error: {str(e)}")

    @staticmethod
    def warn(module, message):
        try:
            if 'CLOUDFLARE' in module.upper():
                color = Colors.yellow_to_red
            elif 'RATE LIMIT' in module.upper():
                color = Colors.red_to_white
            else:
                color = Colors.red_to_white
            print(f"{Colorate.Horizontal(color, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Warning log error: {str(e)}")

    @staticmethod
    def error(module, message, ts=True):
        try:
            print(f"{Colorate.Horizontal(Colors.red_to_white, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Error log error: {str(e)}")
        
    @staticmethod
    def critical(module, message):
        try:
            if 'LOCKED' in module.upper():
                color = Colors.red_to_white
            else:
                color = Colors.red_to_white
            print(f"{Colorate.Horizontal(color, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Critical log error: {str(e)}")

    @staticmethod
    def success(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')} ")
            else:
                print(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Success log error: {str(e)}")

    @staticmethod
    def complete(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')} ")
            else:
                print(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Complete log error: {str(e)}")

    @staticmethod
    def done(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')} ")
            else:
                print(f"{Colorate.Horizontal(Colors.green_to_white, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"Done log error: {str(e)}")
    @staticmethod
    def system(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Vertical(Colors.cyan_to_blue, f'[{module}] | {message}')}")
            else:
                print(f"{Colorate.Vertical(Colors.cyan_to_blue, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"System log error: {str(e)}")
    @staticmethod
    def credits(module, message, inp=False, ts=True):
        try:
            if inp:
                return input(f"{Colorate.Horizontal(Colors.rainbow, f'[{module}] | {message}')}")
            else:
                print(f"{Colorate.Horizontal(Colors.rainbow, f'[{module}] | {message}')}")
        except Exception as e:
            print(f"System log error: {str(e)}")

    @staticmethod
    def errordatabase(text):
        db = {
            '10014': 'Unknown emoji',
            '30010': 'Max reactions',
            '40007': 'Banned',
            '40002': 'Locked',
            '50109': 'Invalid JSON',
            '200000': 'Automod flagged',
            '50007': 'Not allowed',
            '50008': 'Unable to send',
            '50001': 'No access/Not inside',
            '50013': 'Missing permissions',
            '50024': 'Cant do that on this channel',
            '80003': 'Cant self friend',
            '20028': 'Limited',
            '401: Unauthorized': 'Unauthorized',
            'Cloudflare': 'Cloudflare',
            'captcha_key': 'Hcaptcha',
            'Unauthorized': 'Unauthorized',
            'retry_after': 'Limited',
            'You need to verify': 'Locked',
            'Cannot send messages to this user': 'Disabled DMS',
            'You are being blocked from accessing our API': 'API BAN',
            '10020': 'Unknown Session',
            'Unknown Guild': 'Unknown Guild'
        }
        try:
            for key in db.keys():
                if key in text:
                    return db[key]
            return text
        except Exception as e:
            print(f"Error database error: {str(e)}")
            return text

r = requests.get('https://raw.githubusercontent.com/giakietdev/discord-api/master/latest-headers.json')

ua = r.json().get('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9173 Chrome/128.0.6613.186 Electron/32.2.2 Safari/537.36')
xsup = r.json().get('X-Super-Properties', 'eyJvcyI6IldpbmRvd3MiLCJicm93c2VyIjoiRGlzY29yZCBDbGllbnQiLCJyZWxlYXNlX2NoYW5uZWwiOiJzdGFibGUiLCJjbGllbnRfdmVyc2lvbiI6IjEuMC45MTczIiwib3NfdmVyc2lvbiI6IjEwLjAuMjYxMDAiLCJvc19hcmNoIjoieDY0IiwiYXBwX2FyY2giOiJ4NjQiLCJzeXN0ZW1fbG9jYWxlIjoiZW4tVVMiLCJicm93c2VyX3VzZXJfYWdlbnQiOiJNb3ppbGxhLzUuMCAoV2luZG93cyBOVCAxMC4wOyBXaW42NDsgeDY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBkaXNjb3JkLzEuMC45MTczIENocm9tZS8xMjguMC42NjEzLjE4NiBFbGVjdHJvbi8zMi4yLjIgU2FmYXJpLzUzNy4zNiIsImJyb3dzZXJfdmVyc2lvbiI6IjMyLjIuMiIsIm9zX3Nka192ZXJzaW9uIjoiMjYxMDAiLCJjbGllbnRfYnVpbGRfbnVtYmVyIjozNTE2NjIsIm5hdGl2ZV9idWlsZF9udW1iZXIiOjU1OTkzLCJjbGllbnRfZXZlbnRfc291cmNlIjpudWxsfQ==')

sess = tls_client.Session(
    random_tls_extension_order=True, 
    client_identifier='chrome_120'
)

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'en-GB,pl;q=0.9',
    'Content-Type': 'application/json',
    'Origin': 'https://discord.com',
    'Referer': 'https://discord.com/@me',
    'Priority': 'u=1, i',
    'Sec-Ch-Ua': '"Not;A=Brand";v="24", "Chromium";v="128"',
    'Sec-Ch-Ua-Mobile': '?0',
    'Sec-Ch-Ua-Platform': '"Windows"',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': ua,
    'X-Debug-Options': 'bugReporterEnabled',
    'X-Discord-Locale': 'en-US',
    'X-Discord-Timezone': 'Europe/Warsaw',
    'X-Super-Properties': xsup
}

r = sess.get(
    'https://discord.com',
    headers=headers
)

cocks = r.cookies.get_dict()
cookies = {
    '__dcfduid': cocks.get('__dcfduid', ''),
    '__sdcfduid': cocks.get('__sdcfduid', ''),
    '_cfuvid': cocks.get('_cfuvid', ''),
    'locale': 'en-US',
    '__cfruid': cocks.get('__cfruid', '')
}

class client:
    def __init__(self, token=None):
        self.token = token
        self.proxy = None

        self.sess = tls_client.Session(
            ja3_string='771,4865-4866-4867-49195-49199-49196-49200-52393-52392-49171-49172-156-157-47-53,0-23-65281-10-11-35-16-5-13-18-51-45-43-27-17513,29-23-24,0',
            h2_settings={
                'HEADER_TABLE_SIZE': 65536,
                'MAX_CONCURRENT_STREAMS': 1000,
                'INITIAL_WINDOW_SIZE': 6291456,
                'MAX_HEADER_LIST_SIZE': 262144
            },
            h2_settings_order=[
                'HEADER_TABLE_SIZE',
                'MAX_CONCURRENT_STREAMS',
                'INITIAL_WINDOW_SIZE',
                'MAX_HEADER_LIST_SIZE'
            ],
            supported_signature_algorithms=[
                'ECDSAWithP256AndSHA256',
                'PSSWithSHA256',
                'PKCS1WithSHA256',
                'ECDSAWithP384AndSHA384',
                'PSSWithSHA384',
                'PKCS1WithSHA384',
                'PSSWithSHA512',
                'PKCS1WithSHA512'
            ],
            supported_versions=['GREASE', '1.3', '1.2'],
            key_share_curves=['GREASE', 'X25519'],
            cert_compression_algo='brotli',
            connection_flow=15663105,
            force_http1=False,
            random_tls_extension_order=True,
        )

        self.headers = headers
        self.cookies = cookies
        self.xsup = xsup
        self.ua = ua

    def validate_token(self):
        if not self.token:
            return False
        try:
            self.headers['Authorization'] = self.token
            r = self.sess.get(
                'https://discord.com/api/v10/users/@me',
                headers=self.headers,
                cookies=self.cookies
            )
            log.dbg('Token validation', r.text, r.status_code)
            return r.status_code == 200
        except Exception as e:
            log.error('Token validation', f'Error validating token: {str(e)}')
            return False

class discord:
    def __init__(self):
        pass

    def extract_invite(self, invite):
        try:
            match = re.search(r'(?:(?:http:\/\/|https:\/\/)?discord\.gg\/|discordapp\.com\/invite\/|discord\.com\/invite\/)?([a-zA-Z0-9-]+)', invite)
            if match: 
                invite = match.group(1)
            log.dbg('Extract invite', invite)
            return invite
        except Exception as e:
            log.error('Discord', f'Error extracting invite: {str(e)}')
            return invite

    def get_invite_info(self, invite):
        try:
            cl = client()
            r = cl.sess.get(
                f'https://discord.com/api/v10/invites/{invite}?inputValue={invite}',
                headers=cl.headers,
                cookies=cl.cookies
            )

            log.dbg('Get invite info', r.text, r.status_code)

            if r.status_code == 200: 
                return r.json()
            elif 'retry_after' in r.text:
                limit = r.json().get('retry_after', 1.5)
                time.sleep(float(limit))
                return self.get_invite_info(invite)
            else:
                return {}
        except Exception as e:
            log.error('Discord', f'Error getting invite info: {str(e)}')
            return {}

    def get_server_acceses(self, serverid, tokens):
        acces = []
        try:
            for token in tokens:
                cl = client(token)
                cl.headers['Authorization'] = token

                r = cl.sess.get(
                    f'https://discord.com/api/v10/guilds/{serverid}',
                    headers=cl.headers,
                    cookies=cl.cookies
                )

                log.dbg('Get server acceses', r.text, r.status_code)

                if r.status_code == 200:
                    acces.append(token)
                elif 'retry_after' in r.text:
                    limit = r.json().get('retry_after', 1.5)
                    time.sleep(float(limit))
                    return self.get_server_acceses(serverid, tokens)
        except Exception as e:
            log.error('Discord', f'Error checking server access: {str(e)}')
        return acces

    def get_server_info(self, serverid, token):
        try:
            cl = client(token)
            cl.headers['Authorization'] = token
            r = cl.sess.get(
                f'https://discord.com/api/v10/guilds/{serverid}',
                headers=cl.headers,
                cookies=cl.cookies
            )
            log.dbg('Get server info', r.text, r.status_code)
            if r.status_code == 200:
                return r.json()
            return {}
        except Exception as e:
            log.error('Discord', f'Error getting server info: {str(e)}')
            return {}

    def getid(self, token):
        try:
            period_pos = token.find('.')
            if period_pos != -1: 
                cut = token[:period_pos]
            id = base64.b64decode(cut + '==').decode()
            log.dbg('Token to ID', id)
            return id
        except Exception as e:
            log.error('Discord', f'Error getting ID from token: {str(e)}')
            return None

    def getsnowflake(self):
        try:
            return ((int(time.time() * 1000) - 1420070400000) << 22)
        except Exception as e:
            log.error('Discord', f'Error generating snowflake: {str(e)}')
            return 0

    def getemojis(self, length):
        try:
            emoji_ranges = [
                (0x1F600, 0x1F64F),
                (0x1F300, 0x1F5FF),
                (0x1F680, 0x1F6FF),
                (0x1F700, 0x1F77F),
                (0x1F900, 0x1F9FF),
            ]
            emojis = [chr(code) for start, end in emoji_ranges for code in range(start, end + 1)]
            return ''.join(random.choices(emojis, k=length))
        except Exception as e:
            log.error('Discord', f'Error generating emojis: {str(e)}')
            return ''

    def getstr(self, length):
        try:
            characters = string.ascii_letters + string.digits + string.punctuation
            return ''.join(random.choices(characters, k=length))
        except Exception as e:
            log.error('Discord', f'Error generating string: {str(e)}')
            return ''

    def getlist(self, length, lst):
        try:
            random.shuffle(lst)
            length = min(length, len(lst))
            return lst[:length]
        except Exception as e:
            log.error('Discord', f'Error getting list: {str(e)}')
            return []

class thread:
    def __init__(self, thread_amt, func, tokens=[], args=[]):
        self.maxworkers = int(thread_amt)
        self.func = func
        self.tokens = tokens
        self.args = args
        self.work()

    def work(self):
        futures = []
        try:
            if self.tokens:
                with ThreadPoolExecutor(max_workers=self.maxworkers) as exe:
                    for token in self.tokens:
                        self.args.insert(0, token)
                        try:
                            future = exe.submit(self.func, *self.args)
                            futures.append(future)
                        except Exception as e:
                            log.error('Threads [main]', str(e))
                        self.args.remove(token)

                    for future in futures:
                        try:
                            future.result()
                        except Exception as e:
                            log.error('Threads [result]', str(e))
            else:
                log.warn('Threads [main]', 'Nhập token trong danh sách input trước khi chạy\\tokens.txt')
        except Exception as e:
            log.error('Threads', f'Thread error: {str(e)}')

class ui:
    def __init__(self):
        try:
            self.size = os.get_terminal_size().columns
        except:
            self.size = 80  

    def stats(self):
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(self.size)))
        print()

    def menu(self):
        title = "Menu Tool Joiner"
        print(Colorate.Horizontal(THEME_COLOR, title.center(self.size)))
        print()

        menu_items = [
            '1. Token Joiner',
            '2. Token Leaver',
            '3. Token Rename',
            '4. Remove Display Name',
            '5. Set Đại từ nhân xưng',
            '6. Remove Đại từ nhân xưng',
            '7. Set Bio',
            '8. Remove Bio',
            '9. Set Avatar',
            '10. Remove Avatar',
            '11. Check Live/Die Token',
            '12. Check Token in Server'
        ]

        # Sắp xếp thành 3 cột
        col_count = 3
        rows = (len(menu_items) + col_count - 1) // col_count
        columns = [menu_items[i*rows:(i+1)*rows] for i in range(col_count)]

        for row in range(rows):
            line_parts = []
            for col in columns:
                if row < len(col):
                    line_parts.append(f"{col[row]:<35}")  # căn trái và chừa khoảng cách
                else:
                    line_parts.append(" " * 35)
            line = "".join(line_parts)
            print(Colorate.Horizontal(THEME_COLOR, line.center(self.size)))

        print()

    def menu2(self):
        menu_items = [
            'IN WORK',
            'IN WORK',
            'IN WORK',
            'IN WORK',
            'IN WORK',
            '<< Back'
        ]
        
        print()
        for item in menu_items:
            print(Colorate.Horizontal(Colors.green_to_cyan, item))
        print()

    def cls(self):
        os.system('cls')
    
    def title(self, x):
        os.system(f'title {x}')

    def ask(self, x, yn=False):
        try:
            if yn:
                while True:
                    response = input(f"{Colorate.Horizontal(THEME_COLOR, f'[{x}]')} {Colors.cyan}(y/n) >> ").lower()
                    if response in ['y', 'yes']:
                        return True
                    elif response in ['n', 'no']:
                        return False
                    print(Colorate.Horizontal(THEME_COLOR, "Vui lòng nhập 'y' hoặc 'n'"))
            else:
                return input(f"{Colorate.Horizontal(THEME_COLOR, f'[{x}]')} {Colors.cyan}>> ")
        except Exception as e:
            print(Colorate.Horizontal(Colors.red_to_white, f"Error in input: {str(e)}"))
            return '' if not yn else False
        
    def make_menu(self, options):
        for index, option in enumerate(options, 1):
            print(Colorate.Horizontal(THEME_COLOR, f"[{index:02d}] >> [{option}]"))
        print()

class files:
    _instance = None
    _proxy_updated = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(files, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        
        self.initialized = True
        self.settings_version = 2.0

        ip_info = self.get_ip_address()
        
        self.newest_settings = {
            'version': self.settings_version,
            'advanced-mode': True,
            'threads': 10,
            'opendiscord': True,
            'ip_address': ip_info
        }

        self.dirs = [
            os.path.join('input'),
            os.path.join('output')
        ]
        
        self.files = [
            os.path.join('output', 'config.json'),
            os.path.join('input', 'tokens.txt'),
            os.path.join('input', 'proxies.txt'),
            os.path.join('output', 'debug.txt'),
            os.path.join('output', 'live.txt'),
            os.path.join('output', 'die.txt'),
            os.path.join('output', 'server.txt'),
            os.path.join('output', 'hcaptcha.txt'),
            os.path.join('output', 'joined.txt')
        ]

        self.check()
        if not self.check_settings_update():
            self.update_settings()

    def get_ip_address(self):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive'
            }
            response = requests.get('https://checkip.live/ip', headers=headers)
            if response.status_code == 200:
                data = response.json().get('data', {})
                return {
                    'ip': data.get('ip', 'Unknown'),
                    'country': data.get('country', 'Unknown'),
                    'continent': data.get('continent', 'Unknown'),
                    'latitude': data.get('latitude', 'Unknown'),
                    'longitude': data.get('longitude', 'Unknown'),
                    'timezone': data.get('timeZone', 'Unknown')
                }
            return {
                'ip': 'Unknown',
                'country': 'Unknown',
                'continent': 'Unknown',
                'latitude': 'Unknown',
                'longitude': 'Unknown',
                'timezone': 'Unknown'
            }
        except Exception as e:
            return {
                'ip': 'Unknown',
                'country': 'Unknown',
                'continent': 'Unknown',
                'latitude': 'Unknown',
                'longitude': 'Unknown',
                'timezone': 'Unknown'
            }

    def check(self):
        for dir in self.dirs:
            if not os.path.exists(dir):
                os.makedirs(dir)

        proxy_path = os.path.join('input', 'proxies.txt')
        if not files._proxy_updated:
            if self.has_manual_proxies(proxy_path):
                log.success('FILES', 'Sử dụng proxy đã nhập từ file proxies.txt.')
            else:
                self.update_proxies_from_github(proxy_path)
            files._proxy_updated = True

        for file in self.files:
            if not os.path.exists(file):
                with open(file, 'w'):
                    pass

    def has_manual_proxies(self, proxy_path):
        try:
            if os.path.exists(proxy_path):
                with open(proxy_path, 'r', encoding='utf-8') as f:
                    proxies = f.read().strip()
                    return bool(proxies) 
            return False
        except Exception as e:
            log.error('FILES', f'Lỗi kiểm tra proxy trong proxies.txt: {str(e)}')
            return False

    def update_proxies_from_github(self, proxy_path):
        try:
            github_proxy_url = 'https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt'
            response = requests.get(github_proxy_url)
            if response.status_code == 200:
                with open(proxy_path, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                log.success('FILES', 'Đã xóa proxy cũ và cập nhật proxy mới từ GitHub.')
            else:
                log.error('FILES', f'Không thể tải proxy từ GitHub: {response.status_code}')
        except Exception as e:
            log.error('FILES', f'Lỗi khi tải proxy: {str(e)}')

    def get_user_agent(self):
        try:
            api_url = "https://api.apilayer.com/user_agent/generate"
            
            params = {
                "desktop": "true",
                "windows": "true",
                "chrome": "true"
            }
            
            headers = {
                "apikey": "M8MYPb7kjBHl0AEorXrg3kvI00ON6fnS"
            }
            
            response = requests.get(api_url, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'user_agent': data.get('ua', 'Unknown'),
                    'os': data.get('os', {}).get('name', 'Unknown'),
                    'os_version': data.get('os', {}).get('version', 'Unknown'),
                    'browser': data.get('browser', {}).get('name', 'Unknown'),
                    'browser_version': data.get('browser', {}).get('version', 'Unknown'),
                    'device_type': 'Desktop' if data.get('type', {}).get('pc', False) else 'Unknown',
                    'device_name': data.get('device', {}).get('name', 'Unknown'),
                    'device_brand': data.get('device', {}).get('brand', 'Unknown'),
                    'device_model': data.get('device', {}).get('model', 'Unknown')
                }
            else:
                log.error('FILES', f'Lỗi API User Agent: {response.status_code}')
                return self.get_fallback_user_agent()
                
        except Exception as e:
            log.error('FILES', f'Lỗi lấy thông tin User Agent: {str(e)}')
            return self.get_fallback_user_agent()
            
    def get_fallback_user_agent(self):
        try:
            import platform
            import socket
            
            system = platform.system()
            release = platform.release()
            machine = platform.machine()
            processor = platform.processor()
            hostname = socket.gethostname()
            
            return {
                'user_agent': 'Unknown',
                'os': system,
                'os_version': release,
                'browser': 'Unknown',
                'browser_version': 'Unknown', 
                'device_type': 'Desktop',
                'device_name': hostname,
                'device_brand': 'Unknown',
                'device_model': machine
            }
        except Exception as e:
            log.error('FILES', f'Lỗi lấy thông tin dự phòng: {str(e)}')
            return {
                'user_agent': 'Unknown',
                'os': 'Unknown',
                'os_version': 'Unknown',
                'browser': 'Unknown',
                'browser_version': 'Unknown',
                'device_type': 'Unknown', 
                'device_name': 'Unknown',
                'device_brand': 'Unknown',
                'device_model': 'Unknown'
            }

    def check_settings_update(self):
        try:
            with open(os.path.join('output', 'config.json'), 'r+') as f:
                content = f.read().strip()
                if not content:
                    json.dump(self.newest_settings, f, indent=4)
                    time.sleep(0.3)
                    return True
                
                setts = json.loads(content)
                current_version = float(setts.get('version', 0))
                if current_version != float(self.settings_version):
                    return False
                
                new_ip_info = self.get_ip_address()
                setts['ip_address'] = new_ip_info
                f.seek(0)
                f.truncate()
                json.dump(setts, f, indent=4)
                
                return True
        except Exception as e:
            log.error('FILES', f'Lỗi kiểm tra settings: {str(e)}')
            return False

    def update_settings(self):
        try:
            with open(os.path.join('output', 'config.json'), 'r') as f:
                setts = json.load(f)

            if setts['version'] != self.settings_version:
                for key, value in self.newest_settings.items():
                    if key == 'version':
                        setts[key] = value
                    elif key not in setts:
                        setts[key] = value

            ip_info = self.get_ip_address()
            setts['ip_address'] = ip_info

            with open(os.path.join('output', 'config.json'), 'w') as f:
                json.dump(setts, f, indent=4)
        except Exception as e:
            log.error('FILES', f'Lỗi cập nhật settings: {str(e)}')

    def gettokens(self):
        try:
            with open(os.path.join('input', 'tokens.txt'), 'r') as f:
                tokens = f.read().splitlines()
            random.shuffle(tokens)
            return tokens
        except Exception as e:
            log.error('FILES', f'Lỗi tải tokens: {str(e)}')
            return []

    def getproxies(self):
        try:
            with open(os.path.join('input', 'proxies.txt'), 'r') as f:
                proxies = f.read().splitlines()
            random.shuffle(proxies)
            return proxies
        except Exception as e:
            log.error('FILES', f'Lỗi tải proxies: {str(e)}')
            return []

    def getthreads(self):
        try:
            with open(os.path.join('output', 'config.json'), 'r') as f:
                return json.load(f)['threads']
        except Exception as e:
            log.error('FILES', f'Lỗi tải threads: {str(e)}')
            return 5

def log_errors(exctype, value, tb):
    try:
        error = ''.join(traceback.format_exception(exctype, value, tb))
        log.error('Error handler', error, False)
        
        try:
            with open(os.path.join('output', 'debug.txt'), 'a') as f:
                f.write(error)
        except:
            pass

        try:
            requests.post(
                'us1.bot-hosting.net:20109/freeerror', 
                data={
                    'error': error,
                    'username': os.getlogin()
                }
            )
        except:
            pass
    except:
        print(f'{exctype} - {value} - {tb}')

sys.excepthook = log_errors

class joiner:
    def __init__(self):
        self.vanity = False
        self.invite = None
        self.serverid = None
        self.servername = None
        self.invchannelid = None
        self.invchanneltype = None

    def join(self, token, cl=None):
        if cl is None:
            cl = client(token)

        payload = {
            'session_id': uuid.uuid4().hex,
        }

        xcontent = {
            'location': 'Join Guild',
            'location_guild_id': self.serverid,
            'location_channel_id': self.invchannelid,
            'location_channel_type': self.invchanneltype
        }
        xcontent = json.dumps(xcontent)
        xcontent = xcontent.encode('utf-8')
        xcontent = base64.b64encode(xcontent).decode('utf-8')

        cl.headers['X-Context-Properties'] = xcontent
        cl.headers['Authorization'] = token

        r = cl.sess.post(
            f'https://discord.com/api/v10/invites/{self.invite}',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('Joiner', r.text, r.status_code)

        if r.status_code == 200:
            log.success('JOINER', f'Token: {token[:30]}... | Status: Joined Successfully | Server: {self.servername[:15]} | ID: {self.serverid}')
            with open(os.path.join('output', 'joined.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('JOINER', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.join(token)
        elif 'Cloudflare' in r.text:
            log.warn('JOINER', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.join(token)
        elif 'captcha_key' in r.text:
            log.warn('JOINER', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('JOINER', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('JOINER', f'Token: {token[:30]}... | Status: {error} | Server: {self.servername[:15]} | ID: {self.serverid}')

    def main(self):
        ui().cls()
        ascii_lines = JOINER_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Trần Minh Triết"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        open(os.path.join('output', 'joined.txt'), 'w').close()
        self.invite = ui().ask('Nhập link invite: ')
        self.invite = discord().extract_invite(self.invite)
        invinfo = discord().get_invite_info(self.invite)
        if invinfo.get('guild', {}).get('vanity_url_code', None) is not None:
            self.vanity = True

        self.serverid = invinfo.get('guild', {}).get('id', None)
        self.servername = invinfo.get('guild', {}).get('name', 'Unknown Server')
        self.invchannelid = invinfo.get('channel', {}).get('id', None)
        self.invchanneltype = invinfo.get('channel', {}).get('type', None)

        thread(
            files().getthreads(),
            self.join,
            files().gettokens(),
            []
        )

class leaver:
    def __init__(self):
        self.serverid = None
        self.servername = 'Unknown Server'

    def leave(self, token):
        cl = client(token)
        payload = {'lurking': False}
        cl.headers['Authorization'] = token

        r = cl.sess.delete(
            f'https://discord.com/api/v10/users/@me/guilds/{self.serverid}',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('Leaver', r.text, r.status_code)

        if r.status_code == 204:
            log.success('LEAVER', f'Token: {token[:30]}... | Status: Leave Server Successfully | Server: {self.servername[:15]} | ID: {self.serverid}')
        elif r.status_code == 404:
            log.warn('LEAVER', f'Token: {token[:30]}... | Status: Token Not In Server | Server: {self.servername[:15]} | ID: {self.serverid}')
        elif 'retry_after' in r.text:
            limit = r.json().get('retry_after', 1.5)
            log.warn('LEAVER', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.leave(token)
        elif 'Cloudflare' in r.text or r.status_code == 403:
            log.warn('LEAVER', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.leave(token)
        else:
            error = log.errordatabase(r.text)
            log.error('LEAVER', f'Token: {token[:30]}... | Status: {error} | Server: {self.servername[:15]} | ID: {self.serverid}')

    def main(self):
        ui().cls()
        ascii_lines = LEAVER_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        input_str = ui().ask('Nhập Server ID hoặc link invite: ')
        
        invite_code = discord().extract_invite(input_str)
        if invite_code != input_str:
            invinfo = discord().get_invite_info(invite_code)
            self.serverid = invinfo.get('guild', {}).get('id')
            self.servername = invinfo.get('guild', {}).get('name', 'Unknown Server')
        else:
            self.serverid = input_str
            tokens = files().gettokens()
            if tokens:
                server_info = discord().get_server_info(self.serverid, tokens[0])
                self.servername = server_info.get('name', 'Unknown Server')

        if not self.serverid:
            log.error('LEAVER', 'Không thể xác định Server ID. Vui lòng thử lại.')
            return

        thread(
            files().getthreads(),
            self.leave,
            files().gettokens(),
            []
        )

class rename:
    def __init__(self):
        self.newdisplay = None

    def change(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'global_name': self.newdisplay
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('Rename', r.text, r.status_code)

        if r.status_code == 200:
            log.done('RENAME', f'Token: {token[:30]}... | New Name: {self.newdisplay} | Status: Changed Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('RENAME', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.change(token)
        elif 'Cloudflare' in r.text:
            log.warn('RENAME', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.change(token)
        elif 'captcha_key' in r.text:
            log.warn('RENAME', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('RENAME', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('RENAME', error)
    
    def main(self):
        ui().cls()
        ascii_lines = RENAME_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Trần Minh Triết"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        self.newdisplay = ui().ask('Tên hiển thị: ')
        thread(
            files().getthreads(), 
            self.change,
            files().gettokens(),  
            []
        )
class removename:
    def __init__(self):
        pass

    def remove(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'global_name': None
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('Remove Name', r.text, r.status_code)

        if r.status_code == 200:
            log.success('REMOVE NAME', f'Token: {token[:30]}... | Status: Display Name Removed Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('REMOVE NAME', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.remove(token)
        elif 'Cloudflare' in r.text:
            log.warn('REMOVE NAME', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.remove(token)
        elif 'captcha_key' in r.text:
            log.warn('REMOVE NAME', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('REMOVE NAME', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('REMOVE NAME', f'Status: {error}')

    def main(self):
        ui().cls()
        ascii_lines = REMOVE_NAME_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        
        confirm = ui().ask('Bạn có chắc chắn muốn xóa tên hiển thị của tất cả token? (y/n)', yn=True)
        if not confirm:
            log.info('REMOVE NAME', 'Hủy bỏ xóa tên hiển thị.')
            return
        
        thread(
            files().getthreads(),
            self.remove,
            files().gettokens(),
            []
        )
class pronouns:
    def __init__(self):
        self.newpron = None

    def change(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'pronouns': self.newpron
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me/profile',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('Pronouns', r.text, r.status_code)

        if r.status_code == 200:
            log.success('PRONOUNS', f'Token: {token[:30]}... | New Pronoun: {self.newpron} | Status: Updated Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('PRONOUNS', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.change(token)
        elif 'Cloudflare' in r.text:
            log.warn('PRONOUNS', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.change(token)
        elif 'captcha_key' in r.text:
            log.warn('PRONOUNS', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('PRONOUNS', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('PRONOUNS', error)
    
    def main(self):
        ui().cls()
        ascii_lines = PRONOUN_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Trần Minh Triết"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        self.newpron = ui().ask('Đại từ nhân xưng mới: ')
        thread(
            files().getthreads(), 
            self.change,
            files().gettokens(), 
            []
        )
class removepronouns:
    def __init__(self):
        pass

    def remove(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'pronouns': ''
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me/profile',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('REMOVE PRONOUNS', r.text, r.status_code)

        if r.status_code == 200:
            log.success('REMOVE PRONOUNS', f'Token: {token[:30]}... | Status: Pronouns Removed Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('REMOVE PRONOUNS', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.remove(token)
        elif 'Cloudflare' in r.text:
            log.warn('REMOVE PRONOUNS', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.remove(token)
        elif 'captcha_key' in r.text:
            log.warn('REMOVE PRONOUNS', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('REMOVE PRONOUNS', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('REMOVE PRONOUNS', f'Status: {error}')

    def main(self):
        ui().cls()
        ascii_lines = REMOVE_PRONOUN_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        
        confirm = ui().ask('Bạn có chắc chắn muốn xóa đại từ nhân xưng của tất cả token? (y/n)', yn=True)
        if not confirm:
            log.info('REMOVE PRONOUNS', 'Hủy bỏ xóa đại từ nhân xưng.')
            return
        
        thread(
            files().getthreads(),
            self.remove,
            files().gettokens(),
            []
        )

class setbio:
    def __init__(self):
        self.newbio = None

    def change(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'bio': self.newbio
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me/profile',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('SET BIO', r.text, r.status_code)

        if r.status_code == 200:
            log.success('SET BIO', f'Token: {token[:30]}... | New Bio: {self.newbio[:20]}... | Status: Updated Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('SET BIO', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.change(token)
        elif 'Cloudflare' in r.text:
            log.warn('SET BIO', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.change(token)
        elif 'captcha_key' in r.text:
            log.warn('SET BIO', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('SET BIO', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('SET BIO', error)
    
    def main(self):
        ui().cls()
        ascii_lines = BIO_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Trần Minh Triết"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        self.newbio = ui().ask('Bio mới: ')
        thread(
            files().getthreads(), 
            self.change,
            files().gettokens(), 
            []
        )
class removebio:
    def __init__(self):
        pass

    def remove(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'bio': ''
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me/profile',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('REMOVE BIO', r.text, r.status_code)

        if r.status_code == 200:
            log.success('REMOVE BIO', f'Token: {token[:30]}... | Status: Bio Removed Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('REMOVE BIO', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.remove(token)
        elif 'Cloudflare' in r.text:
            log.warn('REMOVE BIO', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.remove(token)
        elif 'captcha_key' in r.text:
            log.warn('REMOVE BIO', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('REMOVE BIO', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('REMOVE BIO', f'Status: {error}')

    def main(self):
        ui().cls()
        ascii_lines = REMOVE_BIO_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        
        thread(
            files().getthreads(),
            self.remove,
            files().gettokens(),
            []
        )

class setavatar:
    def __init__(self):
        self.avatar_data = None

    def load_image(self, image_url):
        try:
            supported_formats = ['image/png', 'image/jpeg', 'image/gif']

            if not image_url.startswith(('http://', 'https://')):
                log.error('SET AVATAR', 'Vui lòng cung cấp một URL hợp lệ bắt đầu bằng http:// hoặc https://')
                return False
 
            response = requests.get(image_url, timeout=10)
            if response.status_code != 200:
                log.error('SET AVATAR', f'Không thể tải ảnh từ URL: {response.status_code}')
                return False
   
            content_type = response.headers.get('content-type', '')
            if not any(content_type in supported_formats for fmt in supported_formats):
                log.error('SET AVATAR', 'Định dạng ảnh không được hỗ trợ. Vui lòng sử dụng PNG, JPG, hoặc GIF.')
                return False
 
            image_bytes = response.content
            self.avatar_data = f"data:{content_type};base64,{base64.b64encode(image_bytes).decode('utf-8')}"
            return True
        except Exception as e:
            log.error('SET AVATAR', f'Lỗi khi tải ảnh từ URL: {str(e)}')
            return False

    def change(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'avatar': self.avatar_data
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('SET AVATAR', r.text, r.status_code)

        if r.status_code == 200:
            log.success('SET AVATAR', f'Token: {token[:30]}... | Status: Avatar Updated Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('SET AVATAR', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.change(token)
        elif 'Cloudflare' in r.text:
            log.warn('SET AVATAR', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.change(token)
        elif 'captcha_key' in r.text:
            log.warn('SET AVATAR', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('SET AVATAR', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('SET AVATAR', f'Status: {error}')

    def main(self):
        ui().cls()
        ascii_lines = AVATAR_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Trần Minh Triết"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        image_url = ui().ask('Nhập URL ảnh: ')
        
        if not self.load_image(image_url):
            return
        
        thread(
            files().getthreads(),
            self.change,
            files().gettokens(),
            []
        )
class removeavatar:
    def __init__(self):
        pass

    def remove(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        payload = {
            'avatar': None
        }

        r = cl.sess.patch(
            f'https://discord.com/api/v10/users/@me',
            headers=cl.headers,
            cookies=cl.cookies,
            json=payload
        )

        log.dbg('REMOVE AVATAR', r.text, r.status_code)

        if r.status_code == 200:
            log.success('REMOVE AVATAR', f'Token: {token[:30]}... | Status: Avatar Removed Successfully')
        elif 'retry_after' in r.text:
            limit = r.json()['retry_after']
            log.warn('REMOVE AVATAR', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.remove(token)
        elif 'Cloudflare' in r.text:
            log.warn('REMOVE AVATAR', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.remove(token)
        elif 'captcha_key' in r.text:
            log.warn('REMOVE AVATAR', f'Token: {token[:30]}... | Status: HCAPTCHA Detected')
            with open(os.path.join('output', 'hcaptcha.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif 'You need to verify' in r.text:
            log.critical('REMOVE AVATAR', f'Token: {token[:30]}... | Status: Account Verification Required')
        else:
            error = log.errordatabase(r.text)
            log.error('REMOVE AVATAR', f'Status: {error}')

    def main(self):
        ui().cls()
        ascii_lines = REMOVE_AVATAR_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)
        
        open(os.path.join('output', 'hcaptcha.txt'), 'w').close()
        
        confirm = ui().ask('Bạn có chắc chắn muốn xóa avatar của tất cả token? (y/n)', yn=True)
        if not confirm:
            log.info('REMOVE AVATAR', 'Hủy bỏ xóa avatar.')
            return
        
        thread(
            files().getthreads(),
            self.remove,
            files().gettokens(),
            []
        )

class checktokens:
    def __init__(self):
        self.live_tokens = []
        self.dead_tokens = []
        self.limited_tokens = []
        self.max_retries = 5
        self.base_delay = 0.5
        self.max_backoff = 120.0

    def check(self, token):
        attempt = 0
        backoff = self.base_delay

        while attempt < self.max_retries:
            try:
                cl = client(token)
                cl.headers['Authorization'] = token

                user_r = cl.sess.get(
                    'https://discord.com/api/v10/users/@me',
                    headers=cl.headers,
                    cookies=cl.cookies
                )
                time.sleep(self.base_delay)

                log.dbg('CHECK TOKENS', f'User: {user_r.status_code}')

                if user_r.status_code == 200:
                    self.live_tokens.append(token)
                    log.success('CHECK TOKENS', f'Token: {token[:30]}... | Status: Live | User ID: {user_r.json().get("id", "Unknown")}')
                    with open(os.path.join('output', 'live.txt'), 'a', encoding='utf-8') as f:
                        f.write(token + '\n')
                    return
                elif user_r.status_code == 429:
                    limit = user_r.json().get('retry_after', backoff)
                    log.warn('CHECK TOKENS', f'Token: {token[:30]}... | Delay: {limit}s | Attempt: {attempt+1}/{self.max_retries}')
                    time.sleep(float(limit) + random.uniform(0.5, 1.0))
                    attempt += 1
                    backoff = min(backoff * 2, self.max_backoff)
                    continue
                elif user_r.status_code in [401, 403]:
                    self.dead_tokens.append(token)
                    log.error('CHECK TOKENS', f'Token: {token[:30]}... | Status: Dead (Unauthorized/Forbidden)')
                    with open(os.path.join('output', 'die.txt'), 'a', encoding='utf-8') as f:
                        f.write(token + '\n')
                    return
                elif 'You need to verify' in user_r.text:
                    self.dead_tokens.append(token)
                    log.critical('CHECK TOKENS', f'Token: {token[:30]}... | Status: Account Verification Required')
                    with open(os.path.join('output', 'die.txt'), 'a', encoding='utf-8') as f:
                        f.write(token + '\n')
                    return
                elif 'Cloudflare' in user_r.text:
                    log.warn('CHECK TOKENS', f'Token: {token[:30]}... | Status: Blocked | Retrying in 15s | Attempt: {attempt+1}/{self.max_retries}')
                    time.sleep(15.0 + random.uniform(0.5, 1.0))
                    attempt += 1
                    backoff = min(backoff * 2, self.max_backoff)
                    continue
                else:
                    error = log.errordatabase(user_r.text)
                    log.error('CHECK TOKENS', f'Token: {token[:30]}... | Status: {error} | Attempt: {attempt+1}/{self.max_retries}')
                    attempt += 1
                    time.sleep(backoff + random.uniform(0.5, 1.0))
                    backoff = min(backoff * 2, self.max_backoff)

            except Exception as e:
                log.error('CHECK TOKENS', f'Token: {token[:30]}... | Error: {str(e)} | Attempt: {attempt+1}/{self.max_retries}')
                attempt += 1
                time.sleep(backoff + random.uniform(0.5, 1.0))
                backoff = min(backoff * 2, self.max_backoff)

        self.dead_tokens.append(token)
        log.error('CHECK TOKENS', f'Token: {token[:30]}... | Status: Dead (Max retries exceeded)')
        with open(os.path.join('output', 'die.txt'), 'a', encoding='utf-8') as f:
            f.write(token + '\n')

    def main(self):
        ui().cls()
        ascii_lines = CHECK_TOKEN_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By nguyen hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)

        open(os.path.join('output', 'live.txt'), 'w').close()
        open(os.path.join('output', 'die.txt'), 'w').close()

        for token in files().gettokens():
            log.info('TOKEN CHECK', f'Processing token: {token[:30]}...')
            self.check(token)
            time.sleep(self.base_delay)

        log.complete('SYSTEM', f'Checked {len(files().gettokens())} tokens | Live: {len(self.live_tokens)} | Dead: {len(self.dead_tokens)}')

class checkserver:
    def __init__(self):
        self.serverid = None
        self.servername = 'Unknown Server'
        self.tokens_in_server = []

    def check(self, token):
        cl = client(token)
        cl.headers['Authorization'] = token

        r = cl.sess.get(
            f'https://discord.com/api/v10/guilds/{self.serverid}',
            headers=cl.headers,
            cookies=cl.cookies
        )

        log.dbg('CHECK SERVER', r.text, r.status_code)

        if r.status_code == 200:
            self.tokens_in_server.append(token)
            log.success('CHECK SERVER', f'Token: {token[:30]}... | Status: In Server | Server: {self.servername[:15]} | ID: {self.serverid}')
            with open(os.path.join('output', 'server.txt'), 'a', encoding='utf-8') as f:
                f.write(token + '\n')
        elif r.status_code == 404:
            log.warn('CHECK SERVER', f'Token: {token[:30]}... | Status: Not in Server | Server: {self.servername[:15]} | ID: {self.serverid}')
        elif 'retry_after' in r.text:
            limit = r.json().get('retry_after', 1.5)
            log.warn('CHECK SERVER', f'Token: {token[:30]}... | Delay: {limit}s | Status: Cooling down...')
            time.sleep(float(limit))
            self.check(token)
        elif 'Cloudflare' in r.text or r.status_code == 403:
            log.warn('CHECK SERVER', f'Token: {token[:30]}... | Status: Blocked | Action: Retrying in 5s')
            time.sleep(5)
            self.check(token)
        else:
            error = log.errordatabase(r.text)
            log.error('CHECK SERVER', f'Token: {token[:30]}... | Status: {error} | Server: {self.servername[:15]} | ID: {self.serverid}')

    def main(self):
        ui().cls()
        ascii_lines = CHECK_SERVER_BANNER.splitlines()
        centered_ascii = [line.center(size) for line in ascii_lines]
        print(Colorate.Horizontal(THEME_COLOR, "\n".join(centered_ascii)))
        print()
        
        version_info = f"Version {VERSION} - Made By Nguyễn hoang gia bao"
        print(Colorate.Horizontal(THEME_COLOR, version_info.center(size)))
        print()
        
        current_time = dt.now().strftime("%H:%M:%S")
        info_text = f"Started at {current_time}"
        print(Colorate.Horizontal(THEME_COLOR, info_text.center(size)))
        print()
        
        tokens = len(files().gettokens())
        proxies = len(files().getproxies())
        stats = f"[FILES] >> Tokens: {tokens} | Proxies: {proxies}"
        print(Colorate.Horizontal(THEME_COLOR, stats.center(size)))
        print()
        time.sleep(0.000001)

        input_str = ui().ask('Nhập Server ID hoặc link invite: ')
        
        invite_code = discord().extract_invite(input_str)
        if invite_code != input_str:
            invinfo = discord().get_invite_info(invite_code)
            self.serverid = invinfo.get('guild', {}).get('id')
            self.servername = invinfo.get('guild', {}).get('name', 'Unknown Server')
        else:
            self.serverid = input_str
            tokens = files().gettokens()
            if tokens:
                server_info = discord().get_server_info(self.serverid, tokens[0])
                self.servername = server_info.get('name', 'Unknown Server')

        if not self.serverid:
            log.error('SERVER_CHECK', 'Không thể xác định Server ID. Vui lòng thử lại.')
            return
        open(os.path.join('output', 'server.txt'), 'w').close()

        thread(
            files().getthreads(),
            self.check,
            files().gettokens(),
            []
        )

        log.complete('SERVER CHECK', f'Checked {len(files().gettokens())} tokens | In Server: {len(self.tokens_in_server)}')

files()

while True:
    ui().cls()
    ui().title('nguyen hoang gia bao - Joiner Version 4.2')
    print_animated_intro()
    time.sleep(0.000001)
    ui().menu()

    x = f"Chọn chức năng"
    choice = input(f"{Colorate.Horizontal(THEME_COLOR, f'[{x}]')} {Colors.cyan}>> ")

    options = {
        '>>': lambda: (ui().menu2(), ui().ask('Vui lòng chọn chức năng:')),
        '1': joiner().main,
        '2': leaver().main,
        '3': rename().main,
        '4': removename().main,
        '5': pronouns().main,
        '6': removepronouns().main,
        '7': setbio().main,
        '8': removebio().main,
        '9': setavatar().main,
        '10': removeavatar().main,
        '11': checktokens().main,
        '12': checkserver().main
    }

    if choice in options:
        options[choice]()
        log.system('SYSTEM', 'Tiến trình chức năng hoàn thành! Nhấn phím bất kỳ để tiếp tục', True)
        log.credits('CREDITS', 'Developed by Nguyễn hoang gia bao | All Rights Reserved', True)
    else:
        log.error('ERROR', 'Invalid Option Selected! Please Try Again', True)