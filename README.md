# Proyek Analisis Data: Air Quality Dataset (PRSA Beijing)

Analisis kualitas udara (PM2.5) dari 12 stasiun pemantauan di Beijing (Maret 2013 - Februari 2017) beserta dashboard interaktif Streamlit.

## Struktur Folder
```
submission
├── dashboard
│   ├── main_data.csv      # data harian bersih hasil notebook
│   └── dashboard.py       # aplikasi Streamlit
├── data                   # 12 file CSV asli (satu per stasiun)
├── notebook.ipynb         # proses analisis lengkap
├── README.md
├── requirements.txt
└── url.txt                # tautan dashboard
```

## Setup Environment
```
python -m venv venv
# Windows: venv\Scripts\activate  |  macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

## Menjalankan Dashboard
Dari folder `submission`:
```
streamlit run dashboard/dashboard.py
```
Dashboard terbuka di http://localhost:8501.

## Menjalankan Ulang Notebook
Jalankan `notebook.ipynb` dari folder `submission` (agar folder `data/` terbaca). Sel terakhir akan membuat ulang `dashboard/main_data.csv`.
