import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

# 读取轨迹数据
ds = xr.open_zarr("trajectory_total.zarr")
lon = ds['lon'].values  # shape: (particle, time)
lat = ds['lat'].values

num_particles = lon.shape[0]

# 设置 colormap
cmap = plt.colormaps.get_cmap('hsv')  # 连续色带

# 创建图像
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_xlim(np.nanmin(lon) - 0.01, np.nanmax(lon) + 0.01)
ax.set_ylim(np.nanmin(lat) - 0.01, np.nanmax(lat) + 0.01)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title('Particle Trajectories with Unique Colors')

# 绘制每个粒子的轨迹、起点、终点
for i in range(num_particles):
    lon_track = lon[i, :]
    lat_track = lat[i, :]

    if np.isnan(lon_track).all() or np.isnan(lat_track).all():
        continue

    color = cmap(i % cmap.N)  # 取不同颜色
    # color = cmap(i / num_particles)
    ax.plot(lon_track, lat_track, '-', lw=0.8, alpha=0.8, color=color)         # 轨迹线
    ax.plot(lon_track[0], lat_track[0], 'o', color='green', markersize=3)      # 起点
    ax.plot(lon_track[-1], lat_track[-1], 'o', color='red', markersize=3)      # 终点

plt.grid(True)
plt.tight_layout()
plt.show()
