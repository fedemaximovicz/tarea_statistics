import pandas as pd
import sqlite3 as sqlt

print(pd.__version__)

datos = pd.read_csv('student_performance_factors.csv')

# vemos un resumen de los tipos de datos de cada columna y la cantidad de valores no nulos
print(datos.info())
""" Hours_Studied, Attendance, Sleep_hours, Exam_score, son de tipo entero 
    Por otro lado, Distance_from_home, Parental_Education_Level, y Parental_Involvement son
    del tipo object y tienen valores nulos"""

print(datos['Distance_from_Home'].unique())
print(datos['Parental_Education_Level'].unique())
print(datos['Parental_Involvement'].unique())

""" Podemos ver que las variables categóricas tienen los valores 
['Near' 'Moderate' 'Far' nan]
['High School' 'College' 'Postgraduate' nan]
['Low' 'Medium' 'High']

"""
orden_distance = ['Near', 'Moderate', 'Far']
orden_education = ['High School', 'College', 'Postgraduate']
orden_involvement = ['Low', 'Medium', 'High']

"""
convierto las columnas al tipo categorical de pandas para poder codificar los valores de
las columnas para que sea más facil obtener la mediana usando esos códigos
por ejemplo, en la columna Parental_Involvement 'Low' : 0, 'Medium': 1, 'High': 2
"""
distance_type = pd.CategoricalDtype(categories=orden_distance, ordered=True)
datos['Distance_from_Home'] = datos['Distance_from_Home'].astype(distance_type)

education_type = pd.CategoricalDtype(categories=orden_education, ordered=True)
datos['Parental_Education_Level'] = datos['Parental_Education_Level'].astype(education_type)

involvement_type = pd.CategoricalDtype(categories=orden_involvement, ordered=True)
datos['Parental_Involvement'] = datos['Parental_Involvement'].astype(involvement_type)

def get_mediana(col_name: str):
    #se obtienen los codes
    codes = datos[col_name].cat.codes
    #no se agregan los -1, los -1 son NaN
    codes = codes[codes!=-1]

    mediana_code = int(codes.median())
    if col_name == 'Distance_from_Home':
        return orden_distance[mediana_code]
    elif col_name == 'Parental_Education_Level':
        return orden_education[mediana_code]
    else:
        return orden_involvement[mediana_code]

print(get_mediana('Parental_Education_Level'))


# se conecta a la base de datos y se cargan los datos
conn = sqlt.connect('EstadisticasDescriptivas.db')

print('conexion exitosa')

conn.execute('''CREATE TABLE IF NOT EXISTS EstadisticaDescriptiva 
    (id INTEGER PRIMARY KEY AUTOINCREMENT, 
    NombreVariable TEXT NOT NULL, 
    TipoVariable TEXT NOT NULL, 
    Media REAL NOT NULL, 
    MEDIANA TEXT NOT NULL,  
    MODA TEXT NOT NULL);''')

# #guardo mediana como string, asi puedo guardar las de datos categoricos tambien
cur = conn.cursor()
columnas = ['Hours_Studied', 'Attendance', 'Sleep_Hours', 
            'Exam_Score', 'Distance_from_Home', 'Parental_Education_Level',
            'Parental_Involvement']

for col in columnas:
    tipo_variable = "cuantitativa" if pd.api.types.is_numeric_dtype(datos[col]) else "categórica"
    #guarda la media si es un dato numerico, si es categórico guarda -1
    media = datos[col].mean() if pd.api.types.is_numeric_dtype(datos[col]) else -1
    mediana = datos[col].median() if pd.api.types.is_numeric_dtype(datos[col]) else get_mediana(col)
    moda = str(datos[col].mode().iloc[0])

    print(f"Nombre: {col}")
    print(f"Tipo de variable: {tipo_variable}")
    print(f"Media: {media}")
    print(f"Mediana: {mediana}")
    print(f"Moda: {moda}")
    
    cur.execute('''INSERT INTO EstadisticaDescriptiva (NombreVariable, TipoVariable, Media, Mediana, Moda)
                VALUES(?,?,?,?,?)''', (col, tipo_variable, media, mediana, moda))

    conn.commit()





