import cv2
import face_recognition
import numpy as np

from datetime import datetime, timedelta,date
import time
from time import gmtime, strftime

import psycopg2
import os
import io
from io import BytesIO

# from package.database.koneksi import get_connection
# from package.database.query import rows,conn,cur, upload_to_database , upload_to_database_pulang
from package.database.query import  upload_to_database , upload_to_database_pulang

import tkinter as tk
from tkinter import ttk, messagebox, Tk
from tkinter.filedialog import askdirectory
from PIL import Image, ImageTk
import PIL 

import threading
import dlib
import pandas as pd


