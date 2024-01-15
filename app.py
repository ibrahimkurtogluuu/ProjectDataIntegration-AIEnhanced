import pandas as pd
from openai import OpenAI
import time
import numpy as np
import os

client = OpenAI(
    api_key = os.environ.get('OPENAI_KEY')
    )

# If your Excel file is named 'data.xlsx' and you want to read the first sheet

#ŞABLON
df1 = pd.read_excel(r'C:\O_D\OneDrive\NormOfis\PROJELERİMİZ\DEVAM EDEN PROJELERİMİZ\ÜSKÜDAR BELEDİYESİ KVKK REVİZYON + BİGR\ÜSKÜDAR BİGR\ÜSKÜDAR BİGR EKC-4 İŞ PAKETİ ÇALIŞMASI\tedbir maddeleri şablon.xlsx')
#YAZILIM
df2 = pd.read_excel(r'C:\O_D\OneDrive\NormOfis\PROJELERİMİZ\DEVAM EDEN PROJELERİMİZ\ÜSKÜDAR BELEDİYESİ KVKK REVİZYON + BİGR\ÜSKÜDAR BİGR\ÜSKÜDAR BİGR EKC-4 İŞ PAKETİ ÇALIŞMASI\üsküdarbigryazılım.xlsx')

# Merging values from df1 into df2 based on 'tedbir_no'
df2 = df2.merge(df1[['tedbir_no', 'iş_paketi_no', 'iş_paketi_adı', 'iş_paketinin_kapsadığı_faaliyet', 'iş_paketi_hedefi']], on='tedbir_no', how='left')

print(df2.columns)
def generate_text_for_bigr(prompt):
        messages = [

            {"role": "system", "content": prompt},
        ]
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=1000,
        )
        return response.choices[0].message.content.strip()

# Function to calculate "bulgu kritiklik seviyesi"
def calculate_bulgu_kritiklik_seviyesi(row):
    uygulanma_durumu_values = {'H': 4, 'K': 3, 'Ç': 2, 'T': 1}
    try:
        uygulanma_value = uygulanma_durumu_values.get(row['uygulanma_durumu'], np.nan)
        if np.isnan(uygulanma_value):
            return "ERROR"
        return row['tedbir_seviyesi'] * uygulanma_value * row['varlık_grubu_kritiklik_derecesi']
    except:
        return "ERROR"

result = df2.apply(lambda row: generate_text_for_bigr(f"Burada güncel duruma ilişkin bir açıklama ve yapılması gereken çalışma ifade edilmiştir. Açıklama:{row['açıklama']}, Gereken Çalışma: {row['hedeflenen_çalışma']}. Bu ifadeleri göz önünde bulundurarak yapılması gerekeni kısa bir cümle ile özetler misin?"), axis=1)

df2['iş_paketinin_kapsadığı_faaliyet'] += ' ' + result

# Applying the function to create the new column
df2['bulgu_kritiklik_seviyesi'] = df2.apply(calculate_bulgu_kritiklik_seviyesi, axis=1)

df2['varlık_grubu_no'] = df2['varlık_grubu_no'].apply(lambda x: f"{x:.1f}")
df2.to_excel(r'C:\O_D\OneDrive\NormOfis\PROJELERİMİZ\DEVAM EDEN PROJELERİMİZ\ÜSKÜDAR BELEDİYESİ KVKK REVİZYON + BİGR\ÜSKÜDAR BİGR\ÜSKÜDAR BİGR EKC-4 İŞ PAKETİ ÇALIŞMASI\sonuçüsküdar.xlsx')