from datetime import date, timedelta

import ee


def initialize_earth_engine(project_id: str):
    try:
        ee.Initialize(project=project_id)
        return True
    except Exception:
        try:
            ee.Authenticate()
            ee.Initialize(project=project_id)
            return True
        except Exception as error:
            raise RuntimeError(
                "Earth Engine initialization failed. "
                "Check authentication and project ID."
            ) from error


def get_srtm_terrain(latitude: float, longitude: float) -> dict:
    point = ee.Geometry.Point([longitude, latitude])

    dem = ee.Image("USGS/SRTMGL1_003")
    slope = ee.Terrain.slope(dem)

    values = (
        dem.addBands(slope)
        .sample(
            region=point,
            scale=30,
            numPixels=1,
            geometries=False,
        )
        .first()
        .getInfo()
    )

    if not values or "properties" not in values:
        raise ValueError("No terrain values were returned.")

    properties = values["properties"]

    return {
        "elevation": properties.get("elevation"),
        "slope": properties.get("slope"),
    }


def get_soil_moisture(
    latitude: float,
    longitude: float,
    start_date: str | None = None,
    end_date: str | None = None,
) -> float | None:
    point = ee.Geometry.Point([longitude, latitude])

    if end_date is None:
        end = date.today()
        end_date = end.isoformat()

    if start_date is None:
        start = date.today() - timedelta(days=7)
        start_date = start.isoformat()

    collection = (
        ee.ImageCollection("NASA/SMAP/SPL4SMGP/008")
        .filterBounds(point)
        .filterDate(start_date, end_date)
        .select("sm_surface")
    )

    image = collection.mean()

    value = (
        image.sample(
            region=point,
            scale=11000,
            numPixels=1,
            geometries=False,
        )
        .first()
        .getInfo()
    )

    if not value or "properties" not in value:
        return None

    return value["properties"].get("sm_surface")


def get_dynamic_features(
    latitude: float,
    longitude: float,
    project_id: str,
) -> dict:
    initialize_earth_engine(project_id)

    terrain = get_srtm_terrain(latitude, longitude)
    soil_moisture = get_soil_moisture(latitude, longitude)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "elevation": terrain["elevation"],
        "slope": terrain["slope"],
        "soil_moisture": soil_moisture,
    }