# Notebook workflow

Create the following notebooks when you begin working with real geospatial data:

## 01_data_exploration.ipynb

- Load the master CSV.
- Inspect shape and data types.
- Check missing values.
- Check coordinate ranges.
- Check class balance.
- Plot rainfall, slope and soil moisture distributions.

## 02_geospatial_processing.ipynb

- Load DEM and rainfall rasters.
- Confirm CRS.
- Clip layers to Sikkim.
- Resample or aggregate layers to a common grid.

## 03_feature_engineering.ipynb

- Join rainfall, terrain, soil moisture and land-cover features.
- Encode categorical land-cover values.
- Create the final training table.
- Save to data/processed/.

## 04_model_training.ipynb

- Train Logistic Regression baseline.
- Train Random Forest.
- Compare precision, recall, F1 and ROC-AUC.
- Save the final model to models/.