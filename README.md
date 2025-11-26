# 🧩 ZIP Master: LinkedIn Game Replica & AI Solver

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-FF5722?style=for-the-badge&logo=python&logoColor=white)
![Status](https://img.shields.io/badge/Status-Completed-success?style=for-the-badge)

**ZIP Master** es una recreación de escritorio completa del popular juego de lógica "Zip" de LinkedIn. 

Esta herramienta no solo permite **jugar** niveles personalizados con mecánicas idénticas a la web original, sino que incluye un **motor de Inteligencia Artificial** capaz de resolver cualquier configuración válida en milisegundos.

---

## ✨ Características Principales

### 🎮 Modo Juego (Play Mode)
- **Mecánica Drag & Drop:** Conecta los puntos arrastrando el ratón, igual que en la versión web.
- **Validación en Tiempo Real:** El juego impide movimientos ilegales (cruzar muros, saltarse números).
- **Cronómetro:** Mide tu tiempo de resolución.
- **Feedback Visual:** Gradiente de color dinámico (Azul $\to$ Cian) para visualizar el progreso del camino.

### 🎨 Editor de Niveles (Sandbox)
- **Diseño Libre:** Crea cualquier configuración de tablero.
- **Gestión de Muros:** Haz clic en los espacios entre celdas para levantar o derribar barreras.
- **Renumeración Inteligente:** Si borras un número intermedio, la secuencia se reajusta automáticamente.

### 🧠 Solver IA (El Cerebro)
- **Algoritmo Híbrido:** Combina **Flood Fill (BFS)** para detectar la topología del nivel y **Backtracking (DFS)** para encontrar el camino Hamiltoniano.
- **Detección Automática:** La IA calcula el área jugable real, ignorando las zonas del tablero que quedan aisladas por muros.
- **Visualización:** Observa cómo la IA resuelve el puzzle instantáneamente sobre tu tablero.

---

## 🚀 Instalación y Ejecución

Este proyecto está construido en **Python nativo**, por lo que es extremadamente ligero y no requiere dependencias pesadas.

### Prerrequisitos
* Python 3.x instalado.

### Pasos
1. **Clona el repositorio** (o descarga el archivo):
   ```bash
   git clone [https://github.com/tu-usuario/zip-master.git](https://github.com/tu-usuario/zip-master.git)
   cd zip-master

2. **Ejecutar la Aplicación**
   ```bash
   python zip.py


---

## 📖 Manual de Uso

### 1. Fase de Edición (Setup)
Al iniciar, estarás en **Modo Editor**. Úsalo para replicar el nivel diario de LinkedIn:
* **Clic en Celda:** Coloca el siguiente número de la secuencia ($1, 2, 3\dots$).
* **Clic en Número:** Lo borra y reajusta la secuencia.
* **Clic en Bordes (Gris):** Crea un muro negro (obstáculo).

### 2. Jugar (Play)
Pulsa el botón verde **`▶ JUGAR`**:
1. El editor se bloquea y el cronómetro inicia.
2. Haz clic en el número **1** (punto de partida).
3. Mantén el clic y **arrastra** el ratón hacia las celdas adyacentes para dibujar tu camino.
4. ¡Conecta todos los números y llena todas las casillas para ganar!

### 3. Resolver con IA
Si te atascas, pulsa el botón morado **`🤖 RESOLVER CON IA`**. El algoritmo calculará la ruta óptima y la dibujará por ti.

---

## 🤓 ¿Cómo funciona el Algoritmo?

El núcleo del solver (`thread_ia`) resuelve el problema en dos fases:

1.  **Análisis de Topología (BFS):** Antes de buscar caminos, el programa lanza una "inundación" desde el número 1. Esto permite contar cuántas casillas son realmente accesibles respetando los muros que has colocado, permitiendo que el solver funcione en tableros irregulares o más pequeños que el grid de 7x7.

2.  **Pathfinding (Backtracking Recursivo):**
    Explora recursivamente los movimientos (Arriba, Abajo, Izq, Der) con poda lógica:
    * *Restricción de Visita:* Solo puede pisar celdas vacías o el siguiente número objetivo.
    * *Condición de Victoria:* Longitud del camino == Área detectada en paso 1 **Y** posición actual == Último número.

---

## 🤝 Contribuciones

¡Las Pull Requests son bienvenidas! Si tienes ideas para mejorar la heurística del solver o embellecer la interfaz `Tkinter`, no dudes en contribuir.

---

<p align="center">
  Hecho con 🐍 y ☕
  <br>
  <i>Disclaimer: Este proyecto es una herramienta educativa y no está afiliado a LinkedIn.</i>
</p>
