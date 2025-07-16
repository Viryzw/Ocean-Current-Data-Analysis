import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import random
import csv

# 读取轨迹数据
ds = xr.open_zarr("trajectory_part.zarr")
lon = ds['lon'].values
lat = ds['lat'].values

num_particles, num_times = lon.shape
region_half_size = 0.05  # ±0.05度

# 提取所有非 NaN 的轨迹点
valid_points = [(lon[i, t], lat[i, t]) 
                for i in range(num_particles) 
                for t in range(num_times) 
                if not np.isnan(lon[i, t]) and not np.isnan(lat[i, t])]
valid_points = np.array(valid_points)

print(f"所有轨迹点总数: {len(valid_points)}")

# 设定约束
min_points_in_region = 800
max_points_in_region = 1500
min_trajectories_in_region = 60

def points_in_region(center_lon, center_lat, lon_arr, lat_arr, half_size):
    return ((lon_arr >= center_lon - half_size) & (lon_arr <= center_lon + half_size) &
            (lat_arr >= center_lat - half_size) & (lat_arr <= center_lat + half_size))

# 随机选区域
for attempt in range(1000):
    center_idx = random.randint(0, len(valid_points) - 1)
    center_lon, center_lat = valid_points[center_idx]

    trajectory_count = 0
    point_count = 0
    for i in range(num_particles):
        mask = points_in_region(center_lon, center_lat, lon[i, :], lat[i, :], region_half_size)
        if np.sum(mask) > 0:
            trajectory_count += 1
            point_count += np.sum(mask)

    if (min_points_in_region <= point_count <= max_points_in_region) and trajectory_count >= min_trajectories_in_region:
        print(f"✅ 找到区域: 中心=({center_lon:.4f}, {center_lat:.4f}), 点数={point_count}, 轨迹数={trajectory_count}")
        break
else:
    print("⚠️ 未找到满足条件的区域，使用最后选点")

# 区域边界，用于线性映射
lon_min, lon_max = center_lon - region_half_size, center_lon + region_half_size
lat_min, lat_max = center_lat - region_half_size, center_lat + region_half_size

# 线性映射函数
def map_to_rect(lon_val, lat_val):
    target_min = -1000
    target_max = 10260
    scale = target_max - target_min

    x_mapped = target_min + scale * (lon_val - lon_min) / (lon_max - lon_min)
    y_mapped = target_min + scale * (lat_val - lat_min) / (lat_max - lat_min)
    return x_mapped, y_mapped

# ========== 绘图并保存数据 ==========
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_xlim(center_lon - region_half_size, center_lon + region_half_size)
ax.set_ylim(center_lat - region_half_size, center_lat + region_half_size)
ax.set_xlabel('Longitude')
ax.set_ylabel('Latitude')
ax.set_title(f'Trajectories in region around ({center_lon:.3f}, {center_lat:.3f})')

with open("region_trajectories_mapped.csv", mode="w", newline="") as f:
    writer = csv.writer(f)
    kept_trajectory_count = 0

    for i in range(num_particles):
        lon_track = lon[i, :]
        lat_track = lat[i, :]

        in_region = points_in_region(center_lon, center_lat, lon_track, lat_track, region_half_size)

        if np.sum(in_region) == 0:
            continue

        # 绘制原始轨迹
        ax.plot(lon_track, lat_track, '-', color='gray', alpha=0.3, lw=0.5)
        ax.plot(lon_track[in_region], lat_track[in_region], 'o', markersize=3, alpha=0.8)

        # 保存该轨迹映射后的坐标到 CSV
        row = []
        for x_orig, y_orig in zip(lon_track[in_region], lat_track[in_region]):
            if not np.isnan(x_orig) and not np.isnan(y_orig):
                x_mapped, y_mapped = map_to_rect(x_orig, y_orig)
                row.extend([x_mapped, y_mapped])
        if row:
            writer.writerow(row)
            kept_trajectory_count += 1

    print(f"✅ 最终保存轨迹数（映射后）: {kept_trajectory_count}")

plt.grid(True)
plt.tight_layout()
plt.show()
