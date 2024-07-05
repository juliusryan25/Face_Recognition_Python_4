from package import *

UNKNOWN_THRESHOLD = 0.5
data = {}
known_face_encodings = []
known_face_names = []
known_id = []
known_last_check_in = []
known_last_check_out = []
known_folder_image = []
fstore = []
data_absen_masuk = []
data_absen_pulang = []

#ambil data wajah
conn = None

class LoginForm(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Configure Database")
        self.parent = parent

       # Label dan Entry untuk Host
        self.host_label = ttk.Label(self, text="Host:", justify="left")
        self.host_label.grid(row=0, column=0, padx=5, pady=5)
        self.host_entry = ttk.Entry(self, width=45)
        self.host_entry.grid(row=0, column=1, padx=5, pady=5, columnspan=3)

        # Label dan Entry untuk Database
        self.database_label = ttk.Label(self, text="Database:", justify="left")
        self.database_label.grid(row=1, column=0, padx=5, pady=5)
        self.database_entry = ttk.Entry(self, width=45)
        self.database_entry.grid(row=1, column=1, padx=5, pady=5, columnspan=3)

        # Label dan Entry untuk Port
        self.port_label = ttk.Label(self, text="Port:", justify="left")
        self.port_label.grid(row=2, column=0, padx=5, pady=5)
        self.port_entry = ttk.Entry(self, width=45)
        self.port_entry.grid(row=2, column=1, padx=5, pady=5, columnspan=3)

        # Label dan Entry untuk User
        self.user_label = ttk.Label(self, text="User:", justify="left")
        self.user_label.grid(row=3, column=0, padx=5, pady=5)
        self.user_entry = ttk.Entry(self, width=45)
        self.user_entry.grid(row=3, column=1, padx=5, pady=5, columnspan=3)

        # Label dan Entry untuk Password
        self.password_label = ttk.Label(self, text="Password:", justify="left")
        self.password_label.grid(row=4, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(self, show="*", width=45)
        self.password_entry.grid(row=4, column=1, padx=5, pady=5, columnspan=3)
        
       
        
        def select_folder():
            folder_selected = askdirectory(title='Choose')  # Tampilkan dialog dan kembalikan path folder yang dipilih
            self.directory_image_entry.delete(0, tk.END)
            self.directory_image_entry.insert(0, folder_selected)
            self.deiconify()

        # self.withdraw()
        # Label dan Entry untuk Directory image
        self.directory_image_label = ttk.Label(self, text="Directory image:", justify="left")
        self.directory_image_label.grid(row=5, column=0, padx=5, pady=5)
        self.directory_image_entry = ttk.Entry(self, width=30)
        self.directory_image_entry.grid(row=5, column=1, padx=5, pady=5)
        self.directory_image_button = ttk.Button(self,text="Choose", command=select_folder)
        self.directory_image_button.grid(row=5, column=3, padx=5, pady=5)

        # Tombol Connect
        self.connect_button = ttk.Button(self, text="Connect", command=self.connect_database, width=60)
        self.connect_button.grid(row=6, column=0, columnspan=5, padx=1, pady=6)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=365)
        self.progress_bar.grid(row=7, column=0, columnspan=5, padx=1, pady=6)

        #loop Data
        self.known_faces_text = tk.Text(self, width=45, height=5)
        self.known_faces_text.grid(row=8, column=0, columnspan=5, padx=5, pady=5)

    def connect_database(self):
        global conn, known_face_encodings, known_face_names, known_id
        host = self.host_entry.get()
        database = self.database_entry.get()
        port = self.port_entry.get()
        user = self.user_entry.get()
        password = self.password_entry.get()
        directory_image = self.directory_image_entry.get()
        print(directory_image)

        try:
            global conn
            conn = psycopg2.connect(
                host=host,
                database=database,
                port=port,
                user=user,
                password=password
            )

            # return conn
            data[f"employee"] = []

            with conn.cursor() as cur:
                    cur.execute("""SELECT hr_employee.id, hr_employee.name, hr_employee.last_check_in, hr_employee.last_check_out, ir_attachment.store_fname
                                    FROM hr_employee
                                    LEFT JOIN ir_attachment ON hr_employee.id = ir_attachment.res_id
                                    AND ir_attachment.res_model = 'hr.employee'
                                    AND ir_attachment.res_field = 'image_1920';
                                    """)
                    rows = cur.fetchall()

            total_rows = len(rows)  # Total jumlah baris data
            current_row = 0  # Inisialisasi counter baris

            for row in rows:
                id, name, last_check_in, last_check_out, store_fname = row
                data[f"employee"].append({"id": id, "nama": name, "last_check_in": last_check_in, "last_check_out": last_check_out , "image": store_fname})
                
                # Ganti 'binary_file_path' dengan direktori filestore odoo anda 
                # binary_file_path = r'\\192.128.12.157\odoo-filestore'
                # binary_file_path = r'C:\Program Files\Odoo_16\sessions\filestore\db_odoo_16'
                binary_file_path = rf"{directory_image}"                
                image_employee  = store_fname 
                image_address = (f'{binary_file_path}/{image_employee}')

                face_encodings = []  # Inisialisasi variabel di sini
                try:
                    image_source = face_recognition.load_image_file(image_address)
                    face_encodings = face_recognition.face_encodings(image_source)
                except FileNotFoundError:
                    # Handle the case where the file is not found
                    pass
                except PIL.UnidentifiedImageError:
                    # Handle the case where the image cannot be identified
                    pass

                if face_encodings:
                    known_face_encodings.append(face_encodings[0])
                    known_face_names.append(name)
                    known_id.append(id)
                    known_last_check_in.append(last_check_in)
                    known_last_check_out.append(last_check_out)
                    fstore.append(binary_file_path)
                    known_folder_image.append(store_fname.split('/')[0])
                    print(known_face_names)
                else:
                    print(f"Tidak ada wajah yang ditemukan dalam gambar {image_address}.")
                
                # Update progress bar
                current_row += 1
                progress = int((current_row / total_rows) * 100)
                self.progress_bar["value"] = progress
                self.update_idletasks()  # Update GUI segera

                self.known_faces_text.delete(1.0, tk.END)  # Hapus isi widget teks
                for name in known_face_names:
                   self.known_faces_text.insert(tk.END, ', '.join(known_face_names[-10:]))  # Masukkan setiap nama ke dalam widget teks

            # Tampilkan progress bar
            self.progress_bar["value"] = 100


            messagebox.showinfo("Sukses", "Koneksi berhasil.")
            self.destroy()
            self.parent.show_webcam()
            
        except Exception as e:
            messagebox.showerror("Gagal", f"Koneksi gagal: {e}")
            self.deiconify()
        return conn

class WebcamApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Webcam Preview")

        self.mode = "IN"
        self.cap = cv2.VideoCapture(0)

        self.canvas = tk.Canvas(self, width=640, height=480)
        self.canvas.pack()

        self.btn_in = ttk.Button(self, text="IN", command=self.set_mode_in)
        self.btn_in.pack(side=tk.LEFT)

        self.btn_out = ttk.Button(self, text="OUT", command=self.set_mode_out)
        self.btn_out.pack(side=tk.RIGHT)

        self.absen_button = ttk.Button(self, text="ABSEN", command=self.capture_absen)
        self.absen_button.pack(pady=10)  # Tambah ruang di atas tombol

        self.show_login_form()
        self.lift()  # Membawa jendela ke depan
        self.focus_force()  # Memberikan fokus ke jendela ini

        #Mulai menampilkan webcam setelah login berhasil
        self.login_form.protocol("WM_DELETE_WINDOW", self.close_login_form)

    # Fungsi untuk menutup window login dan menampilkan webcam
    def close_login_form(self):
        self.login_form.destroy()
        self.destroy

    def show_login_form(self):
        # Tampilkan LoginForm di atas window WebcamApp
        self.login_form = LoginForm(self)
        self.login_form.grab_set()  # Pastikan LoginForm mendapat fokus

    def show_webcam(self):
        self.update_frame()

    def show_login_form(self):
        self.login_form = LoginForm(self)   

    def set_mode_in(self):
        self.mode = "IN"

    def set_mode_out(self):
        self.mode = "OUT"

    def capture_absen(self):
        global known_id
        global data_absen_masuk
        global data_absen_pulang
        global known_folder_image

        if self.mode == "IN":
            if self.face_data:  # Check if a face is detected
                id = self.face_data[0][0]
                last_check_in = self.face_data[0][2]
                
                if id in known_id:
                    index = known_id.index(id)
                    id = known_id[index]
                    name = known_face_names[index]
                    self.compress_and_save_image_masuk(id, self.current_frame, name, 'package/capture')
                   
                else:
                    messagebox.showinfo("Informasi", "Wajah tidak dikenal")
            else:
                messagebox.showinfo("Informasi", "Tidak ada wajah yang terdeteksi")


        elif self.mode == "OUT":
            if self.face_data:  # Check if a face is detected
                id = self.face_data[0][0]
                last_check_in = self.face_data[0][2]
                last_check_out = self.face_data[0][3]
                
                if id in known_id:
                    index = known_id.index(id)
                    id = known_id[index]
                    name = known_face_names[index]
                    self.compress_and_save_image_pulang(id, self.current_frame, name, 'package/capture')
                  
                else:
                    messagebox.showinfo("Informasi", "Wajah tidak dikenal")
            else:
                messagebox.showinfo("Informasi", "Tidak ada wajah yang terdeteksi")

    def process_frame(self, frame):
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
        rgb_small_frame = small_frame[:, :, ::-1]
        face_locations = face_recognition.face_locations(rgb_small_frame, model="hog",number_of_times_to_upsample=2)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_data = []
        for face_encoding in face_encodings:
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if face_distances[best_match_index] <= UNKNOWN_THRESHOLD:
                id = known_id[best_match_index]
                name = known_face_names[best_match_index]
                last_check_in = known_last_check_in[best_match_index]
                last_check_out = known_last_check_out[best_match_index]
            else:
                id = "Unknown"
                name = "Unknown"
                last_check_in = "Unknown"
                last_check_out = "Unknown"
            
            face_data.append([id, name, last_check_in,last_check_out])

        return face_locations, face_data

    def compress_and_save_image_masuk(self, id, image, name, folder_path, quality=70):
        nama_karyawan = name.replace(" ", "")
        id = id
        jam_masuk = datetime.now() - timedelta(hours=7)

        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2XYZ))
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=quality, optimize=True)
        image_data = buffer.getvalue()
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        face_filename = f'{nama_karyawan}_{timestamp}'
        file_path = folder_path+"/"+face_filename
        
        # Menyimpan gambar capture ke filestore
        # image_location = folder_path+"/"+face_filename
        # print(file_path)

        with open(file_path, 'wb') as f:
            f.write(image_data)

        # Buat jendela pop-up
        def show_capture_popup():
            popup = tk.Toplevel(self)
            popup.title(f"Capture {name}")

            # Load gambar ke dalam label
            img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2XYZ))
            imgtk = ImageTk.PhotoImage(image=img)
            label = tk.Label(popup, image=imgtk)
            label.image = imgtk  # Simpan referensi
            label.pack()

            # Tutup jendela setelah 1.1 detik
            popup.after(1100, popup.destroy)

        # Jalankan fungsi show_capture_popup di thread terpisah
        try :
            data_absen_masuk.append(id)
            upload_to_database(id, jam_masuk, file_path, conn)
            print(f"Gambar berhasil disimpan sebagai {face_filename}")
            print(f"Ini data absen masuk : {data_absen_masuk}")

            if id in data_absen_pulang :
                data_absen_pulang.remove(id) 
                print(f"ini data absen pulang : {data_absen_pulang}")
            else :
                print(f"ini data absen pulang : {data_absen_pulang}")
                pass
            
            threading.Thread(target=show_capture_popup).start()

        except Exception as e:
            messagebox.showinfo("Gagal Absen", f"Terjadi kesalahan: {e}")

    
    def compress_and_save_image_pulang(self, id, image, name, folder_path, quality=70):
        nama_karyawan = name.replace(" ", "")
        jam_pulang = datetime.now() - timedelta(hours=7)
       
        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2XYZ))
        buffer = io.BytesIO()
        pil_image.save(buffer, format="JPEG", quality=quality, optimize=True)
        image_data = buffer.getvalue()

        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
        face_filename = f'{nama_karyawan}_{timestamp}'
        file_path = os.path.join(folder_path, face_filename)

        with open(file_path, 'wb') as f:
            f.write(image_data)
        
         # Buat jendela pop-up
        def show_capture_popup():
            popup = tk.Toplevel(self)
            popup.title(f"Capture {name}")

            # Load gambar ke dalam label
            img = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_RGB2XYZ))
            imgtk = ImageTk.PhotoImage(image=img)
            label = tk.Label(popup, image=imgtk)
            label.image = imgtk  # Simpan referensi
            label.pack()

            # Tutup jendela setelah 3 detik
            popup.after(1200, popup.destroy)

        # Jalankan fungsi show_capture_popup di thread terpisah
        try :
            data_absen_pulang.append(id)
        
            upload_to_database_pulang(id, jam_pulang, conn)
            print(f"Gambar berhasil disimpan sebagai {face_filename}")
            if id in data_absen_masuk :
                data_absen_masuk.remove(id)  
                print(f"ini data absen masuk : {data_absen_masuk}")
            else :
                print(f"ini data absen masuk : {data_absen_masuk}")
                pass
            print(f"ini data absen pulang : {data_absen_pulang}")
            
            threading.Thread(target=show_capture_popup).start()

        except Exception as e:
            messagebox.showinfo("Gagal Absen", f"Terjadi kesalahan: {e}")
        
    
    def adjust_text_size(self, frame, text, max_width, min_font_size=0.5, max_font_size=1.5, step=0.1):
        for font_size in np.arange(max_font_size, min_font_size, -step):
            (text_width, text_height), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, font_size, 2)
            if text_width <= max_width:
                return font_size, (text_width, text_height)
        return min_font_size, cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, min_font_size, 1)[0]

    #PROSES FRAME / PREVIEW
    def update_frame(self):
        ret, frame = self.cap.read()
        frame = cv2.flip(frame, 1)
        if ret:
            # Convert the frame to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            self.face_locations, self.face_data = self.process_frame(frame)
            self.current_frame = frame  # Simpan frame untuk capture

            for (top, right, bottom, left), id in zip(self.face_locations, self.face_data):
                top *= 4
                right *= 4
                bottom *= 4
                left *= 4

                text_bottom = bottom + 25
                max_text_width = right - left
                font_size, (text_width, text_height) = self.adjust_text_size(frame, str(id[1]), max_text_width)

                if text_bottom > frame.shape[0]:
                        text_bottom = frame.shape[0] - 10
                
                if id[1] == "Unknown":
                    rectangle_color = (255, 0, 0) 
                   
                elif id[1] != "Unknown" :
                    rectangle_color = (0, 255, 0)

                cv2.rectangle(frame, (left, top), (right, bottom), rectangle_color, 2)
                cv2.putText(frame, str(id[1]), (left + 1, bottom + 40), cv2.FONT_HERSHEY_SIMPLEX, font_size, rectangle_color, 3)
                
                folder_path = 'package/capture'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
            
            # MENAMPILKAN MODE PADA FRAME / PREVIEW
            if self.mode == "IN": 
                cv2.putText(frame, f"MODE : {self.mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv2.LINE_AA)
            
            elif self.mode == "OUT": 
                cv2.putText(frame, f"MODE : {self.mode}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2, cv2.LINE_AA)

            # KONFERSI FRAME KE FORMAT IMAGE TK 
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=imgtk)
            self.canvas.image = imgtk

        self.after(10, self.update_frame)

    def on_closing(self):
        self.cap.release()
        self.destroy()

if __name__ == "__main__":
    app = WebcamApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()