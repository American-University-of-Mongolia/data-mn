# ebarilga raw-pull tracker (not datasets, not published)

Staging: `raw/` (gitignored). Legend: G = geometries, A = attributes.
`--` = not applicable (empty or geometry-only layer).

Status 2026-09-16: geometries done for ALL 75 layers (401,034 features,
audit-clean; 12 poison ids skipped, see meta.json files). Attribute backfill
for all 70 eligible layers finished 2026-09-15 17:24 UTC, failures=0
(log: `/tmp/ebarilga_attrs.log`). 5 layers are geometry-only (`--`).

## Batch 1 - reference (boundaries, zones, roads)

| Layer | Features | G | A | Notes |
|---|---|---|---|---|
| district_border | 9 | ☑ | ☑ | |
| city_border | 1 | ☑ | ☑ | |
| khoroo_border | 204 | ☑ | ☑ | |
| zippolygons | 513 | ☑ | ☑ | |
| map_office_khoroo | 167 | ☑ | ☑ | |
| map_road | 5362 | ☑ | ☑ | ~1.5h attrs |
| data_street_name | 185 | ☑ | ☑ | |

## Batch 2 - transit, education, health

| Layer | Features | G | A | Notes |
|---|---|---|---|---|
| data_trans_bus_route | 88 | ☑ | ☑ | |
| data_trans_bus_station | 607 | ☑ | ☑ | |
| data_edu_school | 323 | ☑ | ☑ | |
| data_edu_kindergarten | 296 | ☑ | ☑ | |
| data_edu_private_kinder | 477 | ☑ | ☑ | |
| data_edu_university | 112 | ☑ | ☑ | |
| data_clinic_gov | 46 | ☑ | ☑ | |
| data_clinic_pharmacy | 1016 | ☑ | ☑ | |

## Batch 3 - construction permits (slow attrs, background)

| Layer | Features | G | A | Notes |
|---|---|---|---|---|
| plan_building | 25174 | ☑ | ☑ | ~7h attrs |
| planning_area | 7007 | ☑ | ☑ | ~2h attrs |
| plan_dedbutets | 572 | ☑ | ☑ | |
| plan_landscaping | 3972 | ☑ | ☑ | ~1h attrs |
| plan_road | 2663 | ☑ | ☑ | |
| planning_landscaping | 169 | ☑ | ☑ | |

## Batch 4 - everything else (geometries + attrs)

POI, culture, zones, protection, redevelopment, emergency; transco
geometry-only (`--insecure-tls`). ~15 layers unprobed: attrs pull doubles
as richness survey.

| Layer | Features | G | A | Notes |
|---|---|---|---|---|
| data_solidwaste | 4 | ☑ | ☑ | |
| data_auto_shts | 192 | ☑ | ☑ | |
| data_pub_restaurant | 76 | ☑ | ☑ | |
| data_cul_entertainment | 82 | ☑ | ☑ | |
| data_pub_supermarket | 1581 | ☑ | ☑ | |
| data_pub_shopping | 144 | ☑ | ☑ | |
| data_gov_org | 256 | ☑ | ☑ | |
| data_auto_service | 107 | ☑ | ☑ | |
| data_pub_camp_resorts | 115 | ☑ | ☑ | |
| data_pub_atm | 328 | ☑ | ☑ | |
| data_pub_bank | 228 | ☑ | ☑ | |
| data_pub_hotel | 241 | ☑ | ☑ | |
| data_sport_org | 86 | ☑ | ☑ | |
| data_sport_halls | 208 | ☑ | ☑ | |
| data_pub_toilet | 9 | ☑ | ☑ | |
| data_sport_complex | 95 | ☑ | ☑ | |
| data_cul_statue | 319 | ☑ | ☑ | |
| Cultural_heritage_building | 39 | ☑ | ☑ | |
| ddt_road_2030 | 3317 | ☑ | ☑ | ~1h attrs |
| ddt_plan_units_2030 | 49 | ☑ | ☑ | |
| ddt_aoz_tuluvlult_2030 | 5391 | ☑ | ☑ | ~1.5h attrs |
| zoning | 372 | ☑ | ☑ | |
| plannig_road | 30 | ☑ | ☑ | |
| sub_center_border | 12 | ☑ | ☑ | |
| technological_park_zoning | 275 | ☑ | ☑ | |
| technological_park_planning_road | 10 | ☑ | ☑ | |
| technological_planning_border | 13 | ☑ | ☑ | |
| special_economic_zone_border | 1 | ☑ | ☑ | |
| special_economic_zone_road | 1 | ☑ | ☑ | |
| special_economic_zoning | 475 | ☑ | ☑ | |
| pz_comm_atc | 11 | ☑ | ☑ | |
| pz_yer_drainage | 36 | ☑ | ☑ | |
| pz_air_strip | 3 | ☑ | ☑ | |
| pz_land_using | 10 | ☑ | ☑ | |
| pz_solid_waste | 3 | ☑ | ☑ | |
| data_pz_cemetry | 13 | ☑ | ☑ | |
| pz_nuur_200m | 2 | ☑ | ☑ | |
| pz_bulag_200m | 10 | ☑ | ☑ | |
| d902_as | 829 | ☑ | ☑ | |
| ddp_dahin_tolovlolt_block | 89 | ☑ | ☑ | |
| ddp_hunam_nygtral_bairshil | 143 | ☑ | ☑ | |
| ddp_build_bound | 1 | ☑ | ☑ | |
| ddp_daguul_haya_hot | 14 | ☑ | ☑ | |
| ddp_het_buschlel | 5315 | ☑ | ☑ | ~1.5h attrs |
| ddp_boundary | 94 | ☑ | ☑ | |
| ddp_road | 2362 | ☑ | ☑ | |
| data_gam_turtsuglarah_2023_58 | 213 | ☑ | ☑ | |
| data_gam_turtsuglarah_old_192sh | 190 | ☑ | ☑ | |
| data_gam_nuulgeh | 32 | ☑ | ☑ | |
| town_2023 | 327 | ☑ | -- | geometry-only |
| ddp_heating_line | 3170 | ☑ | -- | geometry-only |
| pz_city_line | 49 | ☑ | -- | transco, --insecure-tls |
| pz_city_substation | 39 | ☑ | -- | transco, --insecure-tls |

## Batch 5 - building footprints (last, big)

| Layer | Features | G | A | Notes |
|---|---|---|---|---|
| built_building | 325072 | ☑ | -- | geometry-only, ~300MB |

## Empty layers (verified zero features, skip)

emergency_alarm, data_clinic_family, post, Public_land,
no_construction_GEOPORTAL_empty.
