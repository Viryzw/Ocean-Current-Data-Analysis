import xarray as xr
ds = xr.open_dataset("20160505000000-GLOBCURRENT-L4-CUReul_15m-ALT_MED_SUM-v03.0-fv01.0.nc", engine="h5netcdf")
print(ds)