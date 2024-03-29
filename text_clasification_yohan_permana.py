# -*- coding: utf-8 -*-
"""Text Clasification Yohan Permana.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1bU7sd63CjdqpQxL_8X38omAnCGgRGt-L

**Nama : Yohan Permana**
"""

!pip install -q kaggle
#digunakan untuk menginstal paket Python bernama "kaggle" menggunakan perintah pip dari dalam lingkungan Jupyter Notebook atau notebook berbasis Python lainnya.

# digunakan untuk mengunggah file
from google.colab import files
files.upload()

#digunakan untuk membuat dan mengonfigurasi direktori .kaggle serta mengelola file kaggle.json
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json
!ls ~/.kaggle

!kaggle datasets list

#erintah ini digunakan untuk mengunduh dataset dengan nama bbcnewsarchive dari Kaggle menggunakan perintah kaggle datasets download.
!kaggle datasets download -d hgultekin/bbcnewsarchive

# digunakan untuk membuat direktori baru bernama bbcnewsarchive, mengekstrak isi dari file bbcnewsarchive.zip ke dalam direktori tersebut, dan menampilkan daftar file yang telah diekstrak.
!mkdir bbcnewsarchive
!unzip bbcnewsarchive.zip -d bbcnewsarchive
!ls bbcnewsarchive

# Import library
import pandas as pd
from tabulate import tabulate

# Load dataset
file_path = 'bbcnewsarchive/bbc-news-data.csv'
df = pd.read_csv(file_path, sep='\t')

# Menampilkan 10 baris pertama dataset dalam format tabel
print("Top 10 rows of the dataset:")
print(tabulate(df.head(10), headers='keys', tablefmt='fancy_grid'))

df.info()
df.category.value_counts()

# hapus kolom (kolom yang tidak digunakan) menggunakan metode pop
df_new = df.copy()
df_new.pop('filename')

df_new

"""*Proses cleansing data*"""

# mengimpor berbagai pustaka yang diperlukan untuk membangun model Pemrosesan Bahasa Alamiah (NLP) menggunakan Keras. Beberapa pustaka tersebut melibatkan pemrosesan teks, pembangunan model jaringan saraf, dan sumber daya bahasa seperti WordNet dan stopwords dari NLTK. Unduhan data tambahan seperti WordNet dan stopwords juga dilakukan.
import nltk, os, re, string
from keras.layers import Input, LSTM, Bidirectional, SpatialDropout1D, Dropout, Flatten, Dense, Embedding, BatchNormalization
from keras.models import Model
from keras.callbacks import EarlyStopping
from keras.preprocessing.text import Tokenizer, text_to_word_sequence
from keras.preprocessing.sequence import pad_sequences
from keras.utils import to_categorical
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn

nltk.download('wordnet')
nltk.download('stopwords')

# proses lowercase / merubah huruf kapital menjadi kecil
df_new.title = df_new.title.apply(lambda x: x.lower())
df_new.content = df_new.content.apply(lambda x: x.lower())

# Fungsi cleaner menghapus tanda baca dari data teks, dan kemudian diterapkan pada kolom 'title' dan 'content' dari DataFrame df_new menggunakan fungsi apply, diikuti oleh pemanggilan fungsi lem untuk lemmatisasi pada kolom 'content'.
def cleaner(data):
    return(data.translate(str.maketrans('','', string.punctuation)))
    df_new.title = df_new.title.apply(lambda x: cleaner(x))
    df_new.content = df_new.content.apply(lambda x: lem(x))

# Inisialisasi objek lemmatizer menggunakan kelas WordNetLemmatizer dari pustaka NLTK untuk digunakan dalam proses lemmatisasi teks selanjutnya.
lemmatizer = WordNetLemmatizer()

# Fungsi lem melakukan lemmatisasi pada teks yang diberikan dengan mengonversi kata-kata ke bentuk dasarnya, menggunakan informasi pos (part-of-speech) yang diberikan oleh modul nltk.pos_tag. Kemudian, fungsi ini diterapkan pada kolom 'title' dan 'content' dari DataFrame df_new menggunakan fungsi apply
def lem(data):
    pos_dict = {'N': wn.NOUN, 'V': wn.VERB, 'J': wn.ADJ, 'R': wn.ADV}
    return(' '.join([lemmatizer.lemmatize(w,pos_dict.get(t, wn.NOUN)) for w,t in nltk.pos_tag(data.split())]))
    df_new.title = df_new.title.apply(lambda x: lem(x))
    df_new.content = df_new.content.apply(lambda x: lem(x))

# Fungsi rem_numbers menghapus semua angka dari teks yang diberikan dengan menggunakan ekspresi reguler. Namun, pemanggilan fungsi ini pada kolom 'title' dan 'content' dari DataFrame df_new tidak memodifikasi DataFrame itu sendiri, karena perlu menggunakan df_new['title'] = df_new['title'].apply(rem_numbers) dan df_new['content'] = df_new['content'].apply(rem_numbers) untuk menyimpan hasil perubahan.
def rem_numbers(data):
    return re.sub('[0-9]+','',data)
    df_new['title'].apply(rem_numbers)
    df_new['content'].apply(rem_numbers)

# Fungsi stopword digunakan untuk menghapus kata-kata umum (stopwords) dari teks yang diberikan, dan kemudian diterapkan pada kolom 'title' dari DataFrame df_new menggunakan fungsi apply
st_words = stopwords.words()
def stopword(data):
    return ' '.join([w for w in data.split() if w not in st_words])
df_new.title = df_new.title.apply(lambda x: stopword(x))
df_new.content = df_new.content.apply(lambda x: stopword(x))

# menampilkan data hasil cleansing
df_new

"""*Proses Modeling & Plot*"""

#  membuat variabel dummy untuk kolom kategori menggunakan pd.get_dummies pada DataFrame df_new. Selanjutnya, DataFrame baru df_new_cat dibuat dengan menggabungkan DataFrame df_new dan variabel dummy menggunakan pd.concat, dan kemudian kolom 'category' dihapus untuk menghindari multicollinearity.
category = pd.get_dummies(df_new.category)
df_new_cat = pd.concat([df_new, category], axis=1)
df_new_cat = df_new_cat.drop(columns='category')

df_new_cat

#menggabungkan teks dari kolom 'title' dan 'content' dalam DataFrame df_new_cat ke dalam variabel news, dan menyimpan label kategori dalam variabel label sebagai array nilai untuk kategori bisnis, hiburan, politik, olahraga, dan teknologi.
news = df_new_cat['title'].values + '' + df_new_cat['content'].values
label = df_new_cat[['business', 'entertainment', 'politics', 'sport', 'tech']].values

# melihat 5 elemen pertama dari array label
print(label[:5])

# melihat 5 elemen pertama dari susunan berita
print(news[:5])

"""*Proses Splitting Data*"""

# train_test_split dari modul sklearn.model_selection untuk membagi data menjadi set pelatihan dan validasi. Variabel news_train dan label_train akan berisi data pelatihan, sedangkan news_test dan label_test berisi data validasi. Parameter test_size=0.2 menunjukkan bahwa 20% dari data akan digunakan sebagai data validasi, dan shuffle=True mengindikasikan pengacakan data sebelum pembagian.
# Split data into training and validation
from sklearn.model_selection import train_test_split
news_train, news_test, label_train, label_test = train_test_split(news, label, test_size=0.2, shuffle=True)

# Tokenizer dari Keras untuk mengonversi teks menjadi urutan angka dan melaksanakan padding. Objek Tokenizer dibuat dengan membatasi jumlah kata, menetapkan token untuk kata di luar vocab, dan menghapus beberapa karakter. Kemudian, data pelatihan dan validasi digunakan untuk membentuk vocabularies dan mengonversi teks ke urutan angka menggunakan texts_to_sequences
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
tokenizer = Tokenizer(num_words=5000, oov_token='x', filters='!"#$%&()*+,-./:;<=>@[\]^_`{|}~ ')
tokenizer.fit_on_texts(news_train)
tokenizer.fit_on_texts(news_test)
sekuens_train = tokenizer.texts_to_sequences(news_train)
sekuens_test = tokenizer.texts_to_sequences(news_test)
padded_train = pad_sequences(sekuens_train)
padded_test = pad_sequences(sekuens_test)

"""*Proses Modeling Tensor Flow (LSTM)*"""

#Import TensorFlow:
import tensorflow as tf

# Membuat Model Sequential
model = tf.keras.Sequential([
    tf.keras.layers.Embedding(input_dim=5000, output_dim=64),
    tf.keras.layers.LSTM(128),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.5),
    tf.keras.layers.Dense(5, activation='softmax')
])

#Mengompilasi Model:
model.compile(optimizer='adam', metrics=['accuracy'], loss='categorical_crossentropy',)

# Menampilkan Ringkasan Model:
model.summary()

"""*Proses Callback*"""

import tensorflow as tf

# Mendefinisikan kelas callback khusus
class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        # Memeriksa akurasi pelatihan dan validasi
        if logs.get('accuracy') > 0.9 and logs.get('val_accuracy') > 0.9:
            # Menghentikan pelatihan jika kriteria terpenuhi
            self.model.stop_training = True
            # Mencetak pesan jika pelatihan dihentikan
            print("\nThe accuracy of the training set and the validation set has reached > 90%!")

# Membuat objek callback
callbacks = myCallback()

# Melatih model dengan metode fit
history = model.fit(
    padded_train,         # Data pelatihan
    label_train,          # Label pelatihan
    epochs=20,            # Jumlah epoch pelatihan
    validation_data=(padded_test, label_test),  # Data validasi
    verbose=2,            # Tingkat verbositas (2 untuk mencetak setiap epoch)
    callbacks=[callbacks],  # Menggunakan callback yang telah didefinisikan sebelumnya
    validation_steps=30    # Jumlah langkah validasi setiap epoch
)

"""*Visualisasi Grafik hasil Loss*


"""

import matplotlib.pyplot as plt

# Dengan asumsi sejarah adalah variabel yang berisi sejarah pelatihan
plt.figure(figsize=(10, 6))  # Sesuaikan ukuran gambar

# Pelatihan plot & nilai kerugian validasi
plt.plot(history.history['loss'], label='Training Loss', color='red', marker='o')
plt.plot(history.history['val_loss'], label='Validation Loss', color='purple', marker='s')

plt.title('Model Loss')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend(loc='upper right')

# Tambahkan garis kisi untuk keterbacaan yang lebih baik
plt.grid(True, linestyle='--', alpha=0.7)

# Sesuaikan tanda centang sumbu x agar lebih mudah dibaca
plt.xticks(range(0, len(history.history['loss'])+1, 2))

# Show plot
plt.show()

"""*Visualisasi Grafik hasil akurasi*"""

import matplotlib.pyplot as plt

# Dengan asumsi sejarah adalah variabel yang berisi sejarah pelatihan
plt.figure(figsize=(10, 6))  # Adjust the figure size

# Pelatihan plot & nilai kerugian validasi
plt.plot(history.history['accuracy'], label='Training Accuracy', color='blue', marker='o')
plt.plot(history.history['val_accuracy'], label='Validation Accuracy', color='green', marker='s')

plt.title('Model Accuracy')
plt.xlabel('Epoch')
plt.ylabel('Accuracy')
plt.legend(loc='upper left')

# Tambahkan garis kisi untuk keterbacaan yang lebih baik
plt.grid(True, linestyle='--', alpha=0.7)

# Sesuaikan tanda centang sumbu x agar lebih mudah dibaca
plt.xticks(range(0, len(history.history['accuracy'])+1, 2))

# Show plot
plt.show()