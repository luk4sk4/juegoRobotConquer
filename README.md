# CYBER DRONE: OVERDRIVE [AERIAL ARCADE]

es un frenético videojuego arcade aéreo de estilo retro *8-bit / 16-bit* desarrollado en Python con Pygame. Controlas a un pequeño dron de combate volador que debe sobrevivir a oleadas de enemigos mecánicos a lo largo de diferentes sectores.

---

## Rama con Integración en ROS

Este repositorio cuenta con una rama dedicada (`branch`) en la que el juego ha sido implementado e integrado con **ROS (Robot Operating System)**. Si deseas revisar la versión con arquitectura de nodos y topics, cámbiate de rama en Git.

---

## Controles del Juego

| Acción | Teclado / Ratón | Descripción |
| :--- | :--- | :--- |
| **Movimiento / Vuelo** | `W` `A` `S` `D` o **Flechas** | Control fluido y ágil del dron en pantalla. |
| **Disparo Láser Normal** | `Espacio` o **Clic Izquierdo** | Ráfaga continua en la dirección de vuelo. |
| **Girar / Disparo Trasero** | `A` / `Flecha Izq` / `Q` | Apunta hacia la izquierda para defenderte de enemigos traseros. |
| **Super-Disparo (Mega Beam)**| Mantener `E` *(1 segundo)* | Carga una descarga de energía devastadora *(Consume 45 de energía)*. |
| **Turbo Dash (Evasión)** | `Shift` o **Clic Derecho** | Impulso rápido de velocidad e invulnerabilidad breve *(Consume 20 de energía)*. |
| **Pausa / Menú** | `P` o `ESC` | Pausa la partida o abre las opciones. |
| **Pantalla Completa** | `F11` | Alterna entre ventana y pantalla completa. |

---

## Características Principales

* **Mecánica de 1 Sola Vida:** Desafío arcade clásico donde el daño reduce directamente tu barra de salud (HP).
* **Gestión de Energía:** La energía no se regenera sola; debes recoger los botes azules soltados por enemigos para usar el *Dash* y el *Mega Beam*.
* **Evolución del Dron:** Acumula experiencia (XP) destruyendo enemigos para subir de nivel y desbloquear nuevas armas y cañones orbitales (Hasta Nivel 3/4).
* **8 Sectores Dinámicos:**
  1. *Rooftops* (Azoteas lluviosas)
  2. *Bio-Lab*
  3. *Complex*
  4. *Ruins*
  5. *Fortress*
  6. *Warzone*
  7. *Stratosphere*
  8. *Boss Core* (Enfrentamiento final)
* **7 Niveles de Dificultad:** Desde *Very Easy* hasta *Dark Souls Difficulty*, modificando la velocidad, cadencia, vida y daño de los enemigos.
* **Audio Procedural de 8 bits:** Efectos de sonido sintéticos generados en tiempo real con `numpy` y soporte para banda sonora.

---

## Requisitos e Instalación

### Requisitos previos
* Python 3.8 o superior.
* Entorno Linux / WSL (Ubuntu) en Windows.
