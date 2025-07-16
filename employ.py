import numpy as np
import matplotlib.pyplot as plt
import csv
from scipy.interpolate import make_interp_spline

# 读取 CSV 数据
trajectories = []
with open('region_trajectories_start_modified.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        coords = np.array(row, dtype=float)
        x_points = coords[::2]
        y_points = coords[1::2]
        trajectories.append((x_points, y_points))

# 绘图
plt.figure(figsize=(8, 8))

for x_points, y_points in trajectories:
    # 只要有一个点在[0,9260]范围内就绘制
    in_region = ((x_points >= 0) & (x_points <= 9260) & (y_points >= 0) & (y_points <= 9260)).any()

    if in_region:
        if len(x_points) < 4:
            plt.plot(x_points, y_points, '-', color='gray', lw=0.5, alpha=0.5)
            continue

        t = np.linspace(0, 1, len(x_points))
        spline_x = make_interp_spline(t, x_points, k=3)
        spline_y = make_interp_spline(t, y_points, k=3)
        t_smooth = np.linspace(0, 1, 200)

        smooth_x = spline_x(t_smooth)
        smooth_y = spline_y(t_smooth)

        plt.plot(smooth_x, smooth_y, '-', color='gray', lw=1.0, alpha=0.8)

plt.xlim(0, 9260)
plt.ylim(0, 9260)
plt.xlabel('X (Mapped)')
plt.ylabel('Y (Mapped)')
plt.title('Smoothed Trajectories (Visible in [0,5]x[0,5])')
plt.grid(True)
plt.tight_layout()
plt.show()
