# Interface Mock-ups

This folder contains standalone mock-ups for the application interfaces described in `requirements/applicationRequirements.html`.

Files:

- `explore.svg`: main exploration view with map, monitoring stations, nearby terraces and filters.
- `station-detail.svg`: station detail view with summary indicators, nightly LAeq trend and nearby terrace records.
- `compare.svg`: comparison view showing the relationship between nearby terraces and nighttime acoustic measurements across stations.

The date-range control selects noise observations, using period N and average nightly LAeq. Terrace counts use the fixed 4 October 2026 inventory; choosing a noise range does not reconstruct a historical terrace inventory. Counts refer to registered terraces, including temporarily suspended registrations, and use only records with usable locations.

These are illustrative wireframes: markers, chart traces and displayed counts are placeholders. Station district/neighbourhood and external identity links are outside the current model. The district and neighbourhood columns in the nearby-terrace table describe terraces, whose geographic relationships are represented in the ontology.
