import xarray as xr
import numpy as np
from datetime import timedelta
from parcels import FieldSet, ParticleSet, JITParticle, AdvectionRK4

# 1. 读取 NetCDF 文件
filename = "20160505000000-GLOBCURRENT-L4-CUReul_15m-ALT_MED_SUM-v03.0-fv01.0.nc"
ds = xr.open_dataset(filename)

# 2. 提取 Ekman + Geostrophic 流速分量
u = ds['eastward_eulerian_current_velocity'][0, :, :]
v = ds['northward_eulerian_current_velocity'][0, :, :]

# 3. 找出同时 u 和 v 不为 NaN 的点
mask = (~np.isnan(u)) & (~np.isnan(v))

lat_vals = ds['lat'].values
lon_vals = ds['lon'].values
lat_grid, lon_grid = np.meshgrid(lat_vals, lon_vals, indexing='ij')

valid_lats = lat_grid[mask]
valid_lons = lon_grid[mask]

# 4. 限制在数据边界范围内
lat_min, lat_max = 30, 45
# lon_min, lon_max = -5, 36
lon_min, lon_max = 15, 36

inside_mask = (valid_lats >= lat_min) & (valid_lats <= lat_max) & \
              (valid_lons >= lon_min) & (valid_lons <= lon_max)

valid_lats = valid_lats[inside_mask]
valid_lons = valid_lons[inside_mask]

# 控制粒子数量
max_points = 10000
if len(valid_lons) > max_points:
    idx = np.random.choice(len(valid_lons), size=max_points, replace=False)
    valid_lons = valid_lons[idx]
    valid_lats = valid_lats[idx]

# 5. 构造 FieldSet
filenames = {'U': filename, 'V': filename}
variables = {
    'U': 'eastward_eulerian_current_velocity',
    'V': 'northward_eulerian_current_velocity'
}
dimensions = {'lon': 'lon', 'lat': 'lat', 'time': 'time'}

fieldset = FieldSet.from_netcdf(filenames, variables, dimensions, allow_time_extrapolation=True)

# 6. 构造粒子集合
pset = ParticleSet(fieldset=fieldset, pclass=JITParticle,
                   lon=valid_lons, lat=valid_lats)

# 7. 执行仿真
pset.execute(AdvectionRK4,
             runtime=timedelta(days=100),
             dt=timedelta(minutes=30),
             output_file=pset.ParticleFile(name="trajectory_part.zarr", outputdt=timedelta(hours=1)))
