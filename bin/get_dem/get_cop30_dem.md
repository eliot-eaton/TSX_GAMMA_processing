# Preparing a Copernicus GLO-30 DEM for GAMMA

This guide describes how to obtain a Copernicus GLO-30 (COP30) Digital Elevation Model (DEM), convert it into a format compatible with GAMMA, and prepare it for NISAR processing.

## 1. Download a COP30 DEM

Visit the OpenTopography portal:

https://portal.opentopography.org/datasets

1. Search for your area of interest.
2. Select **Copernicus GLO-30** as the DEM source.
3. Draw or upload your area of interest.
4. Submit the request.
5. Copy the download URL for the generated archive.

Download the archive using `wget`:

```bash
wget "<download_url>" -O rasters_COP30.tar.gz
```

Replace `<download_url>` with the URL provided by OpenTopography.

---

## 2. Extract the archive

Extract the downloaded archive:

```bash
tar -xf rasters_COP30.tar.gz
```

This produces a GeoTIFF named:

```text
output.tif
```

---

## 3. Rename the GeoTIFF

Rename the file to something informative describing the study area.

For example:

```bash
mv output.tif galapagos_cop30.tif
```

Other examples:

```text
wolf_cop30.tif
hawaii_cop30.tif
andes_cop30.tif
```

Using descriptive names makes it much easier to manage multiple DEMs.

---

## 4. Convert the GeoTIFF to GAMMA format

Use the following script to convert the GeoTIFF into an ERS-format DEM suitable for subsequent GAMMA processing.

Save the script as `convert_dem.sh`:

```bash
#!/bin/bash

# Check if a TIFF file is provided as an argument
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <tiff_file>"
    exit 1
fi

tiff_file=$1

# Check if the file exists
if [ ! -f "$tiff_file" ]; then
    echo "Error: File '$tiff_file' not found!"
    exit 1
fi

# Convert GeoTIFF to ERS Float32 format
output_file="${tiff_file%.tif}.dem"
gdal_translate -ot Float32 -of ERS "$tiff_file" "$output_file"

if [ $? -eq 0 ]; then
    echo "Conversion successful: $output_file"
else
    echo "Error during conversion."
    exit 1
fi
```

Make the script executable:

```bash
chmod +x convert_dem.sh
```

Run the conversion:

```bash
./convert_dem.sh galapagos_cop30.tif
```

This produces:

```text
galapagos_cop30.dem
galapagos_cop30.ers
```

---

## 5. Use the DEM with GAMMA

The generated `.dem` and `.ers` files can now be used as input to the GAMMA DEM import and geocoding workflow (e.g. `pg.dem_import`) as part of the NISAR processing chain.

## Summary

```bash
# Download
wget "<download_url>" -O rasters_COP30.tar.gz

# Extract
tar -xf rasters_COP30.tar.gz

# Rename
mv output.tif galapagos_cop30.tif

# Convert
chmod +x convert_dem.sh
./convert_dem.sh galapagos_cop30.tif
```
