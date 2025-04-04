import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use("TkAgg")
np.random.seed(42)
array = np.random.choice([0, 1, -1], size=(30, 30, 100), p=[0.99, 0.005, 0.005])

# Создание булевых масок для кубов
filled = array != 0
colors = np.empty(array.shape, dtype=object)
colors[array == 1] = "green"
colors[array == -1] = "red"

# Визуализация
fig = plt.figure(figsize=(10, 10))
ax = fig.add_subplot(111, projection='3d')

ax.voxels(filled, facecolors=colors, edgecolor="k", linewidth=0.1)

# Установка начального угла
ax.view_init(elev=30, azim=45)

# Функция для обработки нажатий клавиш
def on_key(event):
    if event.key == 'r':  # Reset
        ax.view_init(elev=30, azim=45)
        plt.draw()
    elif event.key == 'up':  # Поднять камеру
        ax.view_init(elev=ax.elev + 5, azim=ax.azim)
        plt.draw()
    elif event.key == 'down':  # Опустить камеру
        ax.view_init(elev=ax.elev - 5, azim=ax.azim)
        plt.draw()
    elif event.key == 'left':  # Повернуть влево
        ax.view_init(elev=ax.elev, azim=ax.azim - 5)
        plt.draw()
    elif event.key == 'right':  # Повернуть вправо
        ax.view_init(elev=ax.elev, azim=ax.azim + 5)
        plt.draw()

fig.canvas.mpl_connect('key_press_event', on_key)

plt.ion()  # Включаем интерактивный режим
plt.show()
input()
