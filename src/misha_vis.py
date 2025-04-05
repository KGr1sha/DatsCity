import numpy as np
import matplotlib.pyplot as plt


# Генерация большого 3D массива
np.random.seed(42)
array = viz_map.copy()

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

