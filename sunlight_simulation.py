import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# --- 1. 参数设置 (Parameters) ---
LATITUDE = 27.1  # 洪江古商城纬度
TILT = -23.44  # 冬至日太阳赤纬
WALL_HEIGHT = 8.0  # 墙高 (米)
WELL_WIDTH = 4.0  # 天井宽 (东西向)
WELL_LENGTH = 6.0  # 天井长 (南北向)

# 时间范围：早上 9:00 到 下午 15:00
hours = np.linspace(9, 15, 100)


# --- 2. 天文学计算函数 (Astronomy Math) ---
def get_solar_position(hour, lat, declination):
    # 将角度转为弧度
    phi = np.radians(lat)
    delta = np.radians(declination)
    omega = np.radians((hour - 12) * 15)  # 时角

    # 高度角 (Elevation/Altitude) alpha
    sin_alpha = (
        np.sin(phi) * np.sin(delta) + np.cos(phi) * np.cos(delta) * np.cos(omega)
    )
    alpha = np.arcsin(sin_alpha)

    # 方位角 (Azimuth) A (这里简化计算，以正南为0)
    cos_A = (np.sin(alpha) * np.sin(phi) - np.sin(delta)) / (
        np.cos(alpha) * np.cos(phi)
    )
    # 修正数值误差导致的 domain error
    cos_A = np.clip(cos_A, -1.0, 1.0)
    A = np.arccos(cos_A)
    # 上午方位角为负(东)，下午为正(西)
    if hour < 12:
        A = -A

    return alpha, A


# --- 3. 射线追踪 (Ray Tracing) ---
# 坐标系：天井中心为原点(0,0,0)，Z轴向上。
# 墙壁范围：X: [-W/2, W/2], Y: [-L/2, L/2], Z: [0, H]
# 光源出发点：天井顶部中心 (0, 0, H)

points_x, points_y, points_z = [], [], []

for h in hours:
    alpha, A = get_solar_position(h, LATITUDE, TILT)

    # 阳光向量 (指向光线传播方向)
    # 注意：方位角A是相对于正南的。X轴朝东，Y轴朝北。
    # 太阳在东(A<0)时，光线向西(dx<0)。太阳在南，光线向北(dy>0)。
    # 太阳向量 S = (sin A cos alpha, cos A cos alpha, sin alpha)
    # 光线向量 Ray = -S

    dx = -np.sin(A) * np.cos(alpha)
    dy = -np.cos(A) * np.cos(alpha)  # 修正坐标系方向
    dz = -np.sin(alpha)

    # 参数方程: P = P0 + t * vec
    # x = 0 + t * dx
    # y = 0 + t * dy
    # z = H + t * dz

    # 我们需要求 t，使得点 P 落在墙壁或地板上。
    # 只有 z < H 的方向才是有效的（向下射入）

    candidates = []

    # A. 检查地板 (z=0)
    if dz != 0:
        t_floor = (0 - WALL_HEIGHT) / dz
        if t_floor > 0:
            x = t_floor * dx
            y = t_floor * dy
            if (
                -WELL_WIDTH / 2 <= x <= WELL_WIDTH / 2
                and -WELL_LENGTH / 2 <= y <= WELL_LENGTH / 2
            ):
                candidates.append((x, y, 0))

    # B. 检查四周墙壁
    # 西墙 (x = -W/2) & 东墙 (x = W/2)
    for x_wall in [-WELL_WIDTH / 2, WELL_WIDTH / 2]:
        if dx != 0:
            t_wall = (x_wall - 0) / dx
            if t_wall > 0:
                y = t_wall * dy
                z = WALL_HEIGHT + t_wall * dz
                if (
                    0 <= z <= WALL_HEIGHT
                    and -WELL_LENGTH / 2 <= y <= WELL_LENGTH / 2
                ):
                    candidates.append((x_wall, y, z))

    # 北墙 (y = L/2) (南墙通常照不到，除非夏天)
    if dy != 0:
        t_wall = (WELL_LENGTH / 2 - 0) / dy
        if t_wall > 0:
            x = t_wall * dx
            z = WALL_HEIGHT + t_wall * dz
            if (
                0 <= z <= WALL_HEIGHT
                and -WELL_WIDTH / 2 <= x <= WELL_WIDTH / 2
            ):
                candidates.append((x, WELL_LENGTH / 2, z))

    # 取最近的交点 (t最小)
    if candidates:
        # 这里简化处理，直接取第一个有效交点，实际物理场景通常只有一个解
        pt = candidates[0]
        points_x.append(pt[0])
        points_y.append(pt[1])
        points_z.append(pt[2])

# --- 4. 3D 可视化 ---
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection="3d")

# 画出光斑轨迹
ax.plot(
    points_x,
    points_y,
    points_z,
    "r-o",
    markersize=4,
    label="Sunlight Path (Winter Solstice)",
)

# 画出窨子屋轮廓 (线框)
w, l, h = WELL_WIDTH / 2, WELL_LENGTH / 2, WALL_HEIGHT
# 地板
ax.plot([-w, w, w, -w, -w], [-l, -l, l, l, -l], [0, 0, 0, 0, 0], "k-", alpha=0.3)
# 墙角柱
ax.plot([-w, -w], [-l, -l], [0, h], "k--", alpha=0.3)
ax.plot([w, w], [-l, -l], [0, h], "k--", alpha=0.3)
ax.plot([w, w], [l, l], [0, h], "k--", alpha=0.3)
ax.plot([-w, -w], [l, l], [0, h], "k--", alpha=0.3)
# 顶框
ax.plot([-w, w, w, -w, -w], [-l, -l, l, l, -l], [h, h, h, h, h], "k-", alpha=0.3)

ax.set_title("Sunlight Trajectory in Hongjiang Yinziwu (Winter Solstice)")
ax.set_xlabel("East-West (m)")
ax.set_ylabel("North-South (m)")
ax.set_zlabel("Height (m)")
ax.legend()

plt.show()
