import matplotlib.pyplot as plt
import matplotlib.animation as animation
import xarray as xr
import numpy as np

# 读取轨迹数据
ds = xr.open_zarr("trajectory_part.zarr")
lon = ds['lon'].values  # shape: (particle, time)
lat = ds['lat'].values

num_particles = lon.shape[0]
num_frames = lon.shape[1]

# 创建图像
fig, ax = plt.subplots()
ax.set_xlim(np.min(lon) - 0.01, np.max(lon) + 0.01)
ax.set_ylim(np.min(lat) - 0.01, np.max(lat) + 0.01)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Multi-Particle Ekman + Geostrophic Trajectory Animation')

# 为每个粒子创建 line（轨迹线）和 scatter（当前点）
lines = [ax.plot([], [], '-', lw=1)[0] for _ in range(num_particles)]
dots = [ax.plot([], [], 'o')[0] for _ in range(num_particles)]
starts = [ax.plot([], [], 'go', markersize=5)[0] for _ in range(num_particles)]

def init():
    for line, dot, start in zip(lines, dots, starts):
        line.set_data([], [])
        dot.set_data([], [])
        start.set_data([], [])
    return lines + dots + starts

def update(frame):
    for i in range(num_particles):
        lines[i].set_data(lon[i, :frame+1], lat[i, :frame+1])      # 轨迹线
        dots[i].set_data(lon[i, frame], lat[i, frame])             # 当前点
        starts[i].set_data(lon[i, 0], lat[i, 0])                   # 起点
    return lines + dots + starts

ani = animation.FuncAnimation(fig, update, frames=num_frames, init_func=init,
                              interval=100, blit=True, repeat=False)

plt.show()
