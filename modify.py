import numpy as np
import csv

# 边界
BOUNDARY_MIN = 0.0
BOUNDARY_MAX = 9260.0

def compute_boundary_intersection(p1, p2, boundary_min=BOUNDARY_MIN, boundary_max=BOUNDARY_MAX):
    x1, y1 = p1
    x2, y2 = p2

    dx = x1 - x2
    dy = y1 - y2

    if abs(dx) < 1e-8 and abs(dy) < 1e-8:
        return None

    intersections = []

    # 左边界
    if dx != 0:
        y_at_left = y2 + (boundary_min - x2) * dy / dx
        if boundary_min <= y_at_left <= boundary_max:
            intersections.append((boundary_min, y_at_left))

    # 右边界
    if dx != 0:
        y_at_right = y2 + (boundary_max - x2) * dy / dx
        if boundary_min <= y_at_right <= boundary_max:
            intersections.append((boundary_max, y_at_right))

    # 下边界
    if dy != 0:
        x_at_bottom = x2 + (boundary_min - y2) * dx / dy
        if boundary_min <= x_at_bottom <= boundary_max:
            intersections.append((x_at_bottom, boundary_min))

    # 上边界
    if dy != 0:
        x_at_top = x2 + (boundary_max - y2) * dx / dy
        if boundary_min <= x_at_top <= boundary_max:
            intersections.append((x_at_top, boundary_max))

    if not intersections:
        return None

    # print(intersections, x2, y2)
    
    closest_point = min(intersections, key=lambda pt: np.hypot(pt[0] - x2, pt[1] - y2))
    return closest_point

processed_trajectories = []

with open('region_trajectories_mapped.csv', 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        coords = np.array(row, dtype=float)
        x_points = coords[::2]
        y_points = coords[1::2]

        N = len(x_points)
        if N < 2:
            continue

        # 判断是否所有点都在区域内，全部都在区域内则跳过该轨迹
        all_in_region = np.all((BOUNDARY_MIN <= x_points) & (x_points <= BOUNDARY_MAX) &
                               (BOUNDARY_MIN <= y_points) & (y_points <= BOUNDARY_MAX))
        if all_in_region:
            continue  # 丢弃此轨迹，不处理

        # 找第一个进入区域的点
        first_enter_idx = None
        for i in range(1, N):
            xi, yi = x_points[i], y_points[i]
            if (BOUNDARY_MIN <= xi <= BOUNDARY_MAX) and (BOUNDARY_MIN <= yi <= BOUNDARY_MAX):
                first_enter_idx = i
                break

        if first_enter_idx is None:
            # 轨迹完全在区域外，不处理
            continue

        p1 = (x_points[first_enter_idx - 1], y_points[first_enter_idx - 1])  # 区域外点
        p2 = (x_points[first_enter_idx], y_points[first_enter_idx])          # 区域内点

        new_start = compute_boundary_intersection(p2, p1)
        if new_start is None:
            # 计算交点失败，跳过轨迹
            continue

        # 构造新轨迹：
        # 用边界交点作为起点 + 第一个进入区域点 + 从该点开始到轨迹结束的所有点（无论是否在区域内）
        clipped_traj = [new_start, p2]
        for j in range(first_enter_idx + 1, N):
            clipped_traj.append((x_points[j], y_points[j]))

        if len(clipped_traj) >= 2:
            processed_trajectories.append(clipped_traj)

# 保存结果
with open('region_trajectories_start_modified.csv', 'w', newline='') as f_out:
    writer = csv.writer(f_out)
    for traj in processed_trajectories:
        row = []
        for x, y in traj:
            row.extend([x, y])
        writer.writerow(row)

print(f"✅ 已处理 {len(processed_trajectories)} 条轨迹，并保存为 region_trajectories_start_modified.csv")
