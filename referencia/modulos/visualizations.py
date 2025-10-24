# modulos/visualizations.py
import matplotlib.pyplot as plt


def guardar_grafico_como_imagen(df, nombre_imagen="variacion_criptos.png"):
    """Genera el gráfico de barras y lo guarda como un archivo de imagen."""
    if df is None or df.empty:
        return None

    plt.figure(figsize=(12, 7))
    colors = ["green" if x > 0 else "red" for x in df["Variacion % (24h)"]]
    bars = plt.bar(df["Activo"], df["Variacion % (24h)"], color=colors)
    plt.ylabel("Variación Porcentual (%) en 24h")
    plt.title("Variación Porcentual de Criptomonedas (24h)")
    plt.xticks(rotation=45, ha="right")

    for bar in bars:
        yval = bar.get_height()
        va_align = "bottom" if yval >= 0 else "top"
        plt.text(
            bar.get_x() + bar.get_width() / 2.0,
            yval,
            f"{yval:.2f}%",
            va=va_align,
            ha="center",
        )

    plt.grid(axis="y", linestyle="--", alpha=0.7)
    plt.tight_layout()
    plt.savefig(nombre_imagen)
    plt.close()
    print(f"\nGráfico guardado como '{nombre_imagen}'")
    return nombre_imagen
