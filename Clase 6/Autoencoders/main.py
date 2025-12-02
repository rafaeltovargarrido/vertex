import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Configuración del archivo
INPUT_FILE = 'bquxjob_d0666c3_19adabf5036.csv' # Asegúrate de que el nombre coincida
OUTPUT_IMAGE = 'resultado_anomalias.png'

def generar_grafico():
    print(f"📂 Leyendo datos de {INPUT_FILE}...")
    try:
        df = pd.read_csv(INPUT_FILE)
    except FileNotFoundError:
        print("❌ Error: No se encuentra el archivo CSV. Asegúrate de descargarlo primero.")
        return

    # 2. Configurar el estilo del gráfico
    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(12, 8))

    # 3. Crear el Gráfico de Dispersión (Scatter Plot)
    # Eje X: Duración (Tiempo)
    # Eje Y: Bytes Enviados (Upload - La clave del ataque)
    # Color (Hue): ¿Es anomalía? (Rojo/Verde)
    # Tamaño (Size): Error cuadrático (Cuanto más raro, más grande el punto)
    print("📊 Generando visualización...")
    
    scatter = sns.scatterplot(
        data=df,
        x='duration_sec',
        y='bytes_sent',
        hue='is_anomaly',
        palette={False: 'forestgreen', True: 'red'}, # Verde para normal, Rojo para ataque
        style='is_anomaly',    # Círculos para normal, X para anomalía (si hay pocas variaciones)
        size='mean_squared_error',
        sizes=(50, 500),       # Rango de tamaños de los puntos
        alpha=0.7,             # Transparencia para ver si se solapan
        edgecolor='black'
    )

    # 4. Etiquetas y Títulos
    plt.title('Detección de Exfiltración de Datos (Autoencoder)', fontsize=16, fontweight='bold')
    plt.xlabel('Duración de la Conexión (segundos)', fontsize=12)
    plt.ylabel('Bytes Enviados (Upload)', fontsize=12)
    
    # Mejorar la leyenda
    plt.legend(title='Detección IA', loc='upper right', frameon=True)

    # 5. Etiquetar los ataques (Para saber quiénes son)
    # Filtramos solo las anomalías para ponerles nombre en el gráfico
    anomalies = df[df['is_anomaly'] == True]
    
    for _, row in anomalies.iterrows():
        plt.text(
            x=row['duration_sec'] + 2,  # Un poco a la derecha del punto
            y=row['bytes_sent'], 
            s=f"{row['connection_id']}\n(Error: {row['mean_squared_error']:.0f})", 
            color='darkred',
            fontsize=9,
            weight='bold'
        )

    # 6. Guardar
    plt.tight_layout()
    plt.savefig(OUTPUT_IMAGE, dpi=300)
    print(f"✅ ¡Éxito! Gráfico guardado como: {OUTPUT_IMAGE}")
    print("   Ábrelo para ver cómo la IA separó los ataques del tráfico normal.")

if __name__ == "__main__":
    generar_grafico()