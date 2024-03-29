# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.3
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import geopandas as gpd
from shapely.geometry import LineString
from utils import map_shapely_objects

# %% [markdown]
# ## Reading in Master Plan Land use

# %%
MP14 = gpd.read_file("shapefiles/G_MP14_LAND_USE_PL.shp")
MP14.LU_DESC.unique()

# %%
# Getting the roads and waterbody
sg_roads = MP14[MP14["LU_DESC"].isin(["ROAD"])]
waterbody = MP14[MP14["LU_DESC"].isin(["WATERBODY"])]
# Converting them to local coordinate (Suppose to be in local coordinate but converting just in case)
sg_roads = sg_roads.to_crs(epsg=3414)
sg_roads = sg_roads.loc[:, ["OBJECTID", "geometry"]]
waterbody = waterbody.to_crs(epsg=3414)
waterbody = waterbody.loc[:, ["OBJECTID", "geometry"]]

# %% [markdown]
# ## Joining the waterbody into a Multipolygon and saving in local coordinate!

# %%
# doing a buffer of 3 first is super slow... doing it after merging is faster
water = (
    waterbody.buffer(0).unary_union.buffer(3).buffer(-3)
)  # Some of the polygons will not be join together without buffering
tmp = gpd.GeoSeries([water], crs={"init": "epsg:3414"})
tmp.to_file("data/waterbody.json", driver="GeoJSON")

# %% [markdown]
# ## Joining the road into a Multipolygon and saving in local coordinate!

# %%
# doing a buffer of 3 first is super slow... doing it after merging is faster
road = (
    sg_roads.buffer(0).unary_union.buffer(3).buffer(-3)
)  # Some of the polygons will not be join together without buffering
tmp = gpd.GeoSeries([road], crs={"init": "epsg:3414"})
tmp.to_file("data/road.json", driver="GeoJSON")

# %% [markdown]
# Visualising a subset of it!

# %%
map_shapely_objects(*[sg_roads[:100].buffer(0).unary_union], center=(1.294138, 103.630232), zoom_start=14)

# %% [markdown]
# ## Reading in the road

# %%
road = gpd.read_file("data/road.json")

# %% [markdown]
# ## Testing the number of roads crossed

# %%
line = LineString([(103.8378901, 1.4307489), (103.8072645, 1.4307641)])
tmp2 = gpd.GeoSeries(
    [line],
    crs={"init": "epsg:4326"},
).to_crs(epsg=3414)
area_of_interest = road.intersection(tmp2.buffer(1000))

area_of_interest_gj = area_of_interest.to_crs(epsg=4326)

tmp2.intersection(road).apply(len)

# %%
map_shapely_objects(line, area_of_interest_gj[0], epsg=4326)
