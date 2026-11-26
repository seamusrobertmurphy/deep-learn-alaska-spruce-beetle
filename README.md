# Mapping stand susceptibility to spruce beetle outbreaks across Alaska using Sentinel-1 radar backscatter

## Abstract

In Alaska, the spruce beetle, *Dendroctonus rufipennis* (Kirby), killed the large, dominant spruce of a stand first. The United States Forest Service rated a stand’s hazard, its susceptibility to attack, from the tree diameter, basal area and spruce proportion measured in its field inventories. In 2012, the agency mapped this hazard across Alaska at a resolution of 240 m. Remote sensing studies of spruce beetle outbreaks mostly mapped the damage from optical imagery. Few studies assessed stand susceptibility before an outbreak arrived, and no studies were found that assessed it using radar. Sentinel-1 C-band backscatter from October 2014 to December 2016, recorded largely before the outbreak, was used to map stand susceptibility across Alaska at 90 m. The map was validated against mortality data of spruce crowns killed in the Susitna valley by 2021 and against beetle attack mapped by the Forest Service’s annual aerial detection survey. Before the outbreak, the backscatter coefficient (σ0) was higher in stands the beetle later attacked than in unattacked stands, -7.72 against -9.08 dB. On inventory plots in the Matanuska-Susitna Borough, dead white spruce were taller than live white spruce, 14.6 against 10.4 m, suggesting the radar recorded stand height before attack. Of the stands the beetle later attacked in the Susitna valley, the map had rated 88% susceptible. In the Susitna valley and in all three survey regions, it ranked stands better than the Forest Service hazard map. The map rated 18% of Alaska’s 446 963 km² of forest susceptible, showing managers which stands not yet attacked to protect first.

## Figures

<img src="03.outputs/figures/figure1.png" width="100%" alt="Figure 1">

**Figure 1** Study area. Main map, Alaska over shaded relief (EPSG:3338). Red, spruce beetle damage of the aerial detection survey, 2016 to 2024. Solid black, the three survey regions. Dashed black, the Copper River basin. Blue, the Susitna valley validation strip. A, Cook Inlet, the Kenai Peninsula and the Susitna valley. B, the Interior along the Nenana River.

<img src="03.outputs/figures/figure2.png" width="100%" alt="Figure 2">

**Figure 2** The five steps of the study, in the order of the Methods. Blue, radar. Dark blue, training. Green, prediction. Dark green, validation. Grey, comparison data. τ, the backscatter threshold.

<img src="03.outputs/figures/figure3.png" width="100%" alt="Figure 3">

**Figure 3** Share of forest rated susceptible in each 1 km cell, from grey for none to dark blue for all, at the threshold of -8.24 dB. Pale grey, land under one fifth forest. Darker grey, southeast Alaska, unmapped. Solid black, the three survey regions. Dashed black, the Copper River basin. Black frame, the validation strip.

<img src="03.outputs/figures/figureS1.png" width="100%" alt="Figure S1">

**Figure S1.** Processing chain of each Sentinel-1 GRD scene, in the order applied, from the orbit file to the temporal mean backscatter.

## Tables

**Table 1.** Measures entered and the hazard rating attribute each represents. VV and HV, radar polarizations. PALSAR, Phased Array L-band Synthetic Aperture Radar. ALOS, Advanced Land Observing Satellite.

| Measure | Indicator | Assumption | Basis |
|---|---|---|---|
| Canopy height before the outbreak, from two surface models | Large dominant spruce | Taller | The beetle takes large, slowly growing dominants and codominants first (Massey and Wygant 1954, Werner and Holsten 1983, Hard and Holsten 1985, Doak 2004), and an outbreak left stands with smaller average and maximum heights (Veblen et al. 1991) |
| Sentinel-1 C-band VV mean backscatter before the outbreak | Stand structure and biomass | Higher | Backscatter rises with forest biomass until it saturates, C-band being much less sensitive than L-band (Dobson et al. 1992, Santoro and Cartus 2018) |
| ALOS PALSAR L-band HV mean backscatter | Stand structure and biomass | Higher | Backscatter rises with biomass to a saturation near 100 tons per hectare at L-band (Dobson et al. 1992) |
| Change in VV through the outbreak | Mortality | A difference of either sign, if the radar recorded the mortality | Radar was proposed for bark beetle damage, although detection before the crowns fade has had limited success (Hollaus and Vreugdenhil 2019, Hechtl et al. 2025) |
| Diameter and height of dead and live white spruce on inventory plots | Tree size | Dead trees larger and taller where the outbreak has run | Killed trees were larger and grew more slowly than survivors in the same stands (Werner and Holsten 1983, Hard 1985, Doak 2004) |

**Table 2.** Satellite and survey data. VV, VH, HV and HH, radar polarizations, sent then received, vertical (V) or horizontal (H). γ0, terrain-corrected backscatter. MSI, Multispectral Instrument. PALSAR-2, Phased Array L-band Synthetic Aperture Radar 2. ALOS-2, Advanced Land Observing Satellite 2. 3DEP, the 3D Elevation Program. GLO-30, Copernicus 30 m elevation model.

| Dataset | Signal or band | Orbit / path | Period | Resolution | Images | Processing | Cloud | Role |
|---|---|---|---|---|---|---|---|---|
| Sentinel-1 | C-band radar, VV (VH for the stand series) | ascending 65, descending 131 | Oct 2014 to Dec 2016 | 10 m, read at 90 m | 57 per cell, median | slope-corrected γ0, border-noise mask, scene mean | sees through cloud | the susceptibility map |
| ALOS-2 PALSAR-2 | L-band radar, HV and HH | annual mosaic | 2015 to 2016 | 25 m, read at 90 m | two yearly mosaics | γ0 mosaic | sees through cloud | radar comparison |
| Sentinel-2 MSI | optical, shortwave infrared band 12 and others | fixed swath | Jun to Aug 2016 | 10 to 20 m, read at 90 m | clear-day mean | cloud-masked, clear-day mean | clear days only | optical comparison |
| Elevation models (GLO-30, 3DEP, ArcticDEM) | surface and ground height, canopy height their difference | mosaic | 2024 build | 2 to 30 m, read at 90 m | mosaics | surface minus ground | not affected | height comparison, and the radar slope correction |
| WorldView-2 (severity map) | optical, dead-crown share | fixed swath | 2 Aug 2021 | about 0.5 m, read at 90 m | one image | crown delineation (Zwieback 2024) | clear scene | reference labels, 34 175 attacked and 6 747 unattacked cells |
| Aerial detection survey | damage mapped by eye | from an aircraft | 2016 to 2024 | mapped polygons | yearly | field survey | not affected | validation |

**Table 3.** AUC of each sensor for ranking attacked above unattacked stands. Severity map, the 90 m map of 2021 (Zwieback et al. 2024b). Survey, the aerial detection survey of 2016 to 2024 in the Matanuska-Susitna Borough. AUC, area under the receiver operating characteristic curve. VV and HV, radar polarizations. PALSAR-2, an L-band radar.

| Sensor | Severity map | Matanuska-Susitna survey |
|---|---|---|
| Sentinel-1 VV, statewide map | 0.87 |  |
| Sentinel-1 VV, ascending orbit 65 | 0.87 | 0.65 |
| Sentinel-1 VV, descending orbit 131 | 0.84 | 0.63 |
| PALSAR L-band HV | 0.86 | 0.72 |

**Table 4.** Mean and standard deviation of each sensor in the 34 175 attacked and 6 747 unattacked cells of the severity map. Radar in decibels (dB), Sentinel-2 in reflectance. Wilcoxon rank-sum test, \* p ≤ 0.05, \*\* p ≤ 0.01, \*\*\* p ≤ 0.001, \*\*\*\* p ≤ 0.0001. VV, HV and HH, radar polarizations. PALSAR-2, an L-band radar. NDVI, normalized difference vegetation index.

| Sensor | Attacked, M (SD) | Unattacked, M (SD) |
|---|---|---|
| Sentinel-1 VV, statewide map | -7.72 (0.52)\*\*\*\* | -9.08 (1.14) |
| Sentinel-1 VV, ascending orbit 65 | -7.71 (0.58)\*\*\*\* | -9.24 (1.26) |
| Sentinel-1 VV, descending orbit 131 | -7.76 (0.59)\*\*\*\* | -8.92 (1.11) |
| PALSAR-2 L-band HV | -12.83 (1.43)\*\*\*\* | -16.80 (3.27) |
| PALSAR-2 L-band HH | -7.54 (1.14)\*\*\*\* | -9.72 (2.20) |
| Sentinel-2 red | 0.043 (0.007)\*\*\*\* | 0.061 (0.012) |
| Sentinel-2 NDVI | 0.704 (0.054)\*\*\*\* | 0.609 (0.096) |

**Table 5.** Confusion matrices of the threshold map and three models, in 90 m cells. UA, user’s accuracy. PA, producer’s accuracy.

|  | Reference |  |  |  |  |
|---|---|---|---|---|---|
|  |  |  | Attacked | Unattacked | UA (%) |
| Threshold map | Detection | Susceptible | 30 219 | 1 488 | 95.3 |
|  |  | Not susceptible | 3 956 | 5 259 | 57.1 |
|  |  | PA (%) | 88.4 | 77.9 |  |
| Random forest | Detection | Susceptible | 32 924 | 2 865 | 92.0 |
|  |  | Not susceptible | 1 251 | 3 882 | 75.6 |
|  |  | PA (%) | 96.3 | 57.5 |  |
| Support vector machine | Detection | Susceptible | 33 195 | 3 391 | 90.7 |
|  |  | Not susceptible | 980 | 3 356 | 77.4 |
|  |  | PA (%) | 97.1 | 49.7 |  |
| Gradient boosting | Detection | Susceptible | 32 972 | 2 889 | 91.9 |
|  |  | Not susceptible | 1 203 | 3 858 | 76.2 |
|  |  | PA (%) | 96.5 | 57.2 |  |

**Table 6.** Separability, accuracy and logistic fit of each sensor. M, separability index. AUC, area under the receiver operating characteristic curve. R², Nagelkerke’s. RMSE, root mean square error. MAE, mean absolute error. Moran’s I, spatial autocorrelation of the residuals. VV, HV and HH, radar polarizations. PALSAR-2, an L-band radar. NDVI, normalized difference vegetation index.

| Sensor | M | AUC | Overall accuracy (%) | R² | RMSE | MAE | Moran's I |
|---|---|---|---|---|---|---|---|
| Sentinel-1 VV, statewide map | 0.82 | 0.87 | 87 | 0.48 | 0.27 | 0.16 | 0.43 |
| Sentinel-1 VV, ascending orbit 65 | 0.83 | 0.87 | 87 | 0.50 | 0.27 | 0.15 | 0.43 |
| Sentinel-1 VV, descending orbit 131 | 0.68 | 0.84 | 86 | 0.37 | 0.30 | 0.18 | 0.43 |
| PALSAR-2 L-band HV | 0.84 | 0.86 | 86 | 0.46 | 0.28 | 0.16 | 0.35 |
| PALSAR-2 L-band HH | 0.65 | 0.82 | 86 |  |  |  |  |
| Sentinel-2 red | 0.95 | 0.91 | 85 |  |  |  |  |
| Sentinel-2 NDVI | 0.64 | 0.88 | 77 |  |  |  |  |

**Table 7.** Model diagnostics. RMSE, root mean square error, full for the model fitted to every cell and cross-validated for the test folds. Theil’s U bias, systematic bias. MAE, mean absolute error. OA, overall accuracy. PA, producer’s accuracy.

| Model | Hyperparameters | Full RMSE | Cross-validated RMSE | RMSE ratio | Theil's U bias | MAE | OA (%) | PA, attacked (%) | PA, unattacked (%) |
|---|---|---|---|---|---|---|---|---|---|
| Logistic regression | None | 0.275 | 0.280 | 1.02 | 0.0003 | 0.166 | 89.1 | 97.2 | 48.1 |
| Random forest | Minimum node size 1000, 2 predictors a split | 0.259 | 0.273 | 1.05 | 0.0005 | 0.150 | 89.9 | 96.3 | 57.5 |
| Support vector machine | Cost 1, gamma 0.01 | 0.272 | 0.278 | 1.02 | 0.0001 | 0.160 | 89.3 | 97.1 | 49.7 |
| Gradient boosting | Depth 4, learning rate 0.05, 200 trees | 0.261 | 0.273 | 1.05 | 0.0005 | 0.149 | 90.0 | 96.5 | 57.2 |
| Random forest, untuned | Minimum node size 1, 1 predictor a split | 0.104 | 0.289 | 2.78 | 0.0006 | 0.148 | 89.2 | 95.8 | 55.5 |

**Table 8.** Forest and susceptible forest by region. Forest, conifer top cover of 5% or more in 2015, or a LANDFIRE spruce type where that layer held no data. Susceptible, pre-outbreak mean VV backscatter of -8.24 dB or more. Scenes, median Sentinel-1 scenes per forest cell. VV, vertical polarization. LANDFIRE, a United States wildland fire data programme. dB, decibels.

| Region | Forest (km²) | Susceptible (km²) | Susceptible (%) | Scenes |
|---|---|---|---|---|
| Kenai Peninsula | 9 347 | 5 603 | 60 | 49 |
| Matanuska-Susitna | 17 750 | 8 381 | 47 | 57 |
| Interior | 70 639 | 10 105 | 14 | 69 |
| Alaska | 446 963 | 81 945 | 18 | 55 |

**Table 9.** The statewide map against the aerial detection survey. Attacked, cells inside a spruce beetle polygon of 2016 to 2024. Unattacked, surveyed forest within 10 km of a polygon, never inside one. AUC, area under the curve. VV, vertical polarization. dB, decibels.

| Region | Rated susceptible (%)<br>Attacked | Rated susceptible (%)<br>Unattacked | AUC | Mean VV backscatter (dB)<br>Attacked | Mean VV backscatter (dB)<br>Unattacked | Cells sampled<br>Attacked | Cells sampled<br>Unattacked |
|---|---|---|---|---|---|---|---|
| Kenai Peninsula | 79 | 47 | 0.71 | -7.9 | -8.4 | 4 998 | 4 900 |
| Matanuska-Susitna | 75 | 40 | 0.72 | -7.8 | -8.7 | 5 000 | 4 995 |
| Interior | 30 | 19 | 0.60 | -8.7 | -9.0 | 5 000 | 4 147 |

**Table S1.** Survey coverage and scores of the three survey regions and the Copper River basin. Years flown, median years of 2016 to 2024 the survey flew over a sampled cell. AUC, area under the curve, with Sentinel-2 red scored on cells with a clear day. VV, vertical polarization.

| Region | Attacked | Unattacked | Years flown, attacked | Years flown, unattacked | AUC, VV | AUC, red | AUC, hazard map |
|---|---|---|---|---|---|---|---|
| Kenai Peninsula | 4 998 | 4 900 | 4 | 4 | 0.71 | 0.51 | 0.58 |
| Matanuska-Susitna Borough | 5 000 | 4 995 | 4 | 3 | 0.72 | 0.62 | 0.66 |
| Interior | 5 000 | 4 147 | 4 | 4 | 0.60 | 0.65 | 0.52 |
| Copper River basin, set apart | 2 323 | 4 999 | 1 | 2 | 0.37 | 0.52 | 0.37 |

**Table S2.** Fit and overfitting diagnostics of the logistic fits, and of the temporal network on the crown labels. R², Nagelkerke’s, starred by the likelihood ratio test. Hosmer-Lemeshow, statistic over ten groups, starred by its test. Brier, mean squared error of the fitted probability. RMSE, its root. rRMSE, RMSE over the label mean (%). MAE, mean absolute error. RMSE ratio, cross-validated over full RMSE, overfitted above 1.1 (Valbuena et al. 2017; Murphy et al. 2026). Theil’s U bias, share of the test error due to bias. Moran’s I, clustering of residuals over the eight nearest cells, starred by its test. Durbin-Watson, statistic of residuals in cell order. VV, HV and HH, radar polarizations. PALSAR-2, an L-band radar. \* p ≤ 0.05, \*\* p ≤ 0.01, \*\*\* p ≤ 0.001, \*\*\*\* p ≤ 0.0001.

| Model | n | R² | Hosmer-Lemeshow | Brier | RMSE | rRMSE (%) | MAE | RMSE ratio | Theil's U bias | Moran's I | Durbin-Watson |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sentinel-1 VV, statewide product | 40 922 | 0.477\*\*\*\* | 1144\*\*\*\* | 0.076 | 0.275 | 32.9 | 0.157 | 1.02 | 0.000 | 0.430\*\*\*\* | 1.26 |
| Sentinel-1 VV, ascending orbit 65 | 40 922 | 0.498\*\*\*\* | 1038\*\*\*\* | 0.073 | 0.270 | 32.3 | 0.151 | 1.02 | 0.000 | 0.429\*\*\*\* | 1.24 |
| Sentinel-1 VV, descending orbit 131 | 40 922 | 0.373\*\*\*\* | 1240\*\*\*\* | 0.090 | 0.299 | 35.8 | 0.185 | 1.01 | 0.000 | 0.428\*\*\*\* | 1.31 |
| GLO-30 surface minus terrain | 40 922 | 0.294\*\*\*\* | 3543\*\*\*\* | 0.101 | 0.318 | 38.0 | 0.211 | 1.04 | 0.000 | 0.519\*\*\*\* | 1.09 |
| PALSAR L-band HV | 40 922 | 0.464\*\*\*\* | 368\*\*\*\* | 0.081 | 0.285 | 34.1 | 0.163 | 1.00 | 0.000 | 0.355\*\*\*\* | 1.38 |
| Two C-band orbits | 40 922 | 0.498\*\*\*\* | 1047\*\*\*\* | 0.073 | 0.270 | 32.3 | 0.151 | 1.02 | 0.000 | 0.429\*\*\*\* | 1.24 |
| L-band HV and HH | 40 922 | 0.474\*\*\*\* | 272\*\*\*\* | 0.081 | 0.284 | 34.0 | 0.161 | 1.00 | 0.000 | 0.336\*\*\*\* | 1.42 |
| C-band and height | 40 922 | 0.515\*\*\*\* | 1339\*\*\*\* | 0.070 | 0.265 | 31.7 | 0.147 | 1.02 | 0.000 | 0.434\*\*\*\* | 1.24 |
| L-band and height | 40 922 | 0.501\*\*\*\* | 1177\*\*\*\* | 0.075 | 0.273 | 32.7 | 0.153 | 1.00 | 0.000 | 0.342\*\*\*\* | 1.41 |
| All five sources | 40 922 | 0.556\*\*\*\* | 662\*\*\*\* | 0.067 | 0.259 | 31.0 | 0.138 | 1.01 | 0.000 | 0.368\*\*\*\* | 1.34 |
| Temp network, blind crown folds | 510 |  |  | 0.092 | 0.303 | 41.9 | 0.138 | 2.13 | 0.012 | 0.269\*\*\*\* | 1.35 |

**Table S3.** Data, dates, operation and output of each step. VV, HV and HH, radar polarizations. PALSAR-2, an L-band radar. NDVI, normalized difference vegetation index. M, separability index. LANDFIRE, a United States wildland fire data programme. dB, decibels.

| Step | Data | Dates | Operation | Output |
|---|---|---|---|---|
| 1. Mean backscatter | Sentinel-1 C-band VV backscatter, every interferometric wide swath scene over Alaska | October 2014 to December 2016 | Border noise masked, slope corrected, normalized to 38° incidence, aggregated to 90 m, averaged in linear power | Mean backscatter of every 90 m forest cell of Alaska |
| 2. Training | Reference data, the severity map of Zwieback et al. (2024), 34 175 attacked and 6 747 unattacked cells of 90 m | WorldView-2 image of 2 August 2021 | Attacked ranked against unattacked cells by the area under the receiver operating characteristic curve and separated by M; threshold set by Youden's index; spatial 5-fold cross-validation of four tuned models; 1 000 draws of 5 000 cells of each class | Test of the first hypothesis; threshold of -8.24 dB, with overall accuracy, kappa and commission and omission errors |
| 3. Prediction | Mean backscatter; conifer top cover of 5% or more, or a LANDFIRE spruce type where it held no data west of 141° W | October 2014 to December 2016; 2015 | Forest cells at or above the threshold rated susceptible | Susceptibility map of Alaska; susceptible forest by region and outside the outbreak |
| 4. Validation | Validation data, the aerial detection survey in three regions, the Copper River basin set apart, and 708 inventory plots with white spruce in the same regions | 2016 to 2024; plots measured 1999 to 2025 | Area under the curve and area-weighted accuracy; paired Wilcoxon signed-rank test of dead against live white spruce | Test of the second hypothesis |
| 5. Comparison | PALSAR-2 L-band HV and HH; change in Sentinel-1 VV; Sentinel-2 red, band 12 and NDVI; Forest Service hazard map | 2015 and 2016; October 2014 to December 2016 against June 2019 to August 2021; summer 2016, with 2015 for clear days; 2012 | Scored as the mean backscatter, on the same cells | Benchmarks of the mean backscatter |

**Table S4.** Separability and classification accuracy of each sensor at its Youden threshold. M, separability index (Kaufman and Remer 1994), starred by the Wilcoxon rank-sum test. AUC, area under the receiver operating characteristic curve, with the 95% confidence interval (CI) of DeLong et al. (1988). Threshold, in decibels (dB) for radar and reflectance for red. Kappa, Cohen’s kappa. Overall accuracy with its exact binomial 95% CI. VV, HV and HH, radar polarizations. PALSAR-2, an L-band radar. NDVI, normalized difference vegetation index. \* p ≤ 0.05, \*\* p ≤ 0.01, \*\*\* p ≤ 0.001, \*\*\*\* p ≤ 0.0001.

| Source | Attacked cells | Unattacked cells | M | AUC (95% CI) | Threshold | Kappa | Commission, attacked | Commission, unattacked | Omission, attacked | Omission, unattacked | Overall accuracy (95% CI) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Sentinel-1 VV, statewide product | 34 175 | 6 747 | 0.82\*\*\*\* | 0.87 (0.86, 0.87) | -8.24 | 0.58 | 0.05 | 0.43 | 0.12 | 0.22 | 0.87 (0.86, 0.87) |
| Sentinel-1 VV, ascending orbit 65 | 34 990 | 6 774 | 0.83\*\*\*\* | 0.87 (0.87, 0.88) | -8.32 | 0.59 | 0.05 | 0.41 | 0.11 | 0.22 | 0.87 (0.87, 0.88) |
| Sentinel-1 VV, descending orbit 131 | 34 990 | 6 774 | 0.68\*\*\*\* | 0.84 (0.83, 0.84) | -8.34 | 0.53 | 0.06 | 0.45 | 0.11 | 0.29 | 0.86 (0.85, 0.86) |
| PALSAR L-band HV | 34 990 | 6 774 | 0.84\*\*\*\* | 0.86 (0.86, 0.87) | -14.08 | 0.56 | 0.05 | 0.44 | 0.11 | 0.25 | 0.86 (0.86, 0.87) |
| PALSAR L-band HH | 34 990 | 6 774 | 0.65\*\*\*\* | 0.82 (0.81, 0.83) | -8.68 | 0.53 | 0.06 | 0.45 | 0.11 | 0.32 | 0.86 (0.86, 0.86) |
| Sentinel-2 red summer 2016 | 34 175 | 6 747 | 0.95\*\*\*\* | 0.91 (0.90, 0.91) | 0.05 | 0.55 | 0.04 | 0.48 | 0.15 | 0.17 | 0.85 (0.84, 0.85) |
| Sentinel-2 NDVI summer 2016 | 34 175 | 6 747 | 0.64\*\*\*\* | 0.88 (0.87, 0.88) | 0.68 | 0.42 | 0.04 | 0.59 | 0.24 | 0.16 | 0.77 (0.77, 0.78) |
