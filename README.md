# Geographic Diversity in SE Research: Key Findings

A 15-year bibliometric study of author geographic representation at ICSA
and ICSE (2010-2025). Full paper by Amy Hoyt, Tina Jiang, Grace Koo, and
Rona Liu-Zhong, Northeastern University.


## Major Findings

Neither conference has genuinely diversified. Changes in geographic
representation reflect shifts between dominant powers, not broader global
inclusion.

ICSA is and has historically been a Western European conference. Western Europe
never fell below 51% of annual paper representation across the full 15-year
period, peaking at 83% in 2013. Germany, France, and the Netherlands
consistently lead this conference.

ICSE flipped from US-dominated to China-dominated, but that is the extent
of the change. The US led every single year from 2010-2021. China overtook
the US in 2022 and by 2024 contributed 2.5x more author-institution rows
(651 vs. 265).

Asia-Pacific now leads ICSE. The region grew from 16% of papers in
2010-2012 to 55% in 2022-2024, almost entirely driven by Chinese
institutions.

Latin America,Eastern Europe, the Middle East, and Africa together account for
less than 10% of papers in either venue across all 15 years, with no meaningful
upward trend. Proving lack of geographic diversification and consistent 
marginalization of these regions.

Australia is also a strong contributor in the ICSA despite size and location. 
CSIRO, Data61, and UNSW Sydney collectively account for 121 author-institution 
rows, making Australia the third most represented country at the institutional 
level.


## By the Numbers

                        ICSA            ICSE
Papers collected        479             2,900
Author-institution rows 1,943           13,030
Unique countries        39              67
Top country (all-time)  Germany (268)   USA (3,481)
W. Europe 2010-2012     65.2%           40.2%
W. Europe 2022-2024     68.6%           24.1%
Asia-Pacific 2010-2012  10.3%           16.0%
Asia-Pacific 2022-2024  21.6%           55.3%
Global South (all-time) under 10%       under 10%


## Charts

figures/geo_map_icsa.png
    Choropleth map of cumulative ICSA author counts by country, 2010-2025

figures/geo_map_icse.png
    Choropleth map of cumulative ICSE author counts by country, 2010-2025

figures/icsa_fig_region_line.png
    Regional share per year at ICSA, showing Western Europe's persistent
    dominance and slow Asia-Pacific growth

figures/icse_fig_region_line.png
    Regional share per year at ICSE, showing the US-to-Asia-Pacific
    crossover around 2022


## Data and Reproducibility

Pipeline: DBLP HTML scraping for DOIs, then OpenAlex API for country codes
Coverage: 94.1% ICSA, 95.9% ICSE
Code: src/ingest/fetch_icsa.py, src/ingest/fetch_icse.py
Raw data: data/raw/icsa_affiliations.json, data/raw/icse_affiliations.json


## Bottom Line

Software engineering's most prestigious venues are not globally inclusive.
ICSA is a Western European dominated venue. ICSE traded US dominance for Chinese
dominance. Researchers from the Middle East, Africa, and Latin America remain
largely locked out of both conferences, and the trend lines show no sign of 
changing.
