# API and export contract

The Flask application serves both the frontend and API on port 5000 by default.

## Case context

Send `X-Model-ID: model_01` on every API request. Valid shipped IDs are `model_01` through `model_07`. Alternatively, provide `model_id` in a POST body. The header takes precedence. The default is `model_01`.

`POST /switch_model` validates and returns a case for compatibility with the original frontend. It does not mutate a global selection; subsequent requests must identify their case. The shared frontend fetch wrapper does this automatically.

## Endpoints

| Method | Path | Request | Response |
| --- | --- | --- | --- |
| GET | `/health` | Case header optional | AI availability and case status |
| GET | `/models` | Case header optional | Available IDs and current request case |
| POST | `/switch_model` | `{"model_id":"model_02"}` | Case summary |
| GET | `/case_info` | Case header | Case ID, name, drag values, reduction |
| GET | `/shape_regions` | Case header | `success`, regional `data` |
| GET | `/pressure_regions` | Case header | `success`, regional `data` |
| GET | `/click_map` | Case header | `success`, mapping `data` |
| GET | `/region_summary/<region>` | Case header | Shape, pressure, click coordinates |
| POST | `/analyze` | `{}` or optional base64 `image_before`, `image_after` | Image explanation and recorded drag |
| POST | `/explain_shape` | `{"zone_name":"front"}` | Region explanation |
| POST | `/explain_pressure` | `{"zone_name":"front"}` | Region explanation |
| POST | `/explain_drag` | `{"zone_name":"front"}` | Region explanation and recorded drag |
| POST | `/explain_zone` | `zone_name`, optional `question` | Combined explanation |
| POST | `/chat` | `{"question":"What changed?"}` | `success`, `answer` |
| POST | `/clear_history` | `{}` | Compatibility acknowledgment; chat is stateless |

Regions: `front`, `roof`, `side`, `rear`. POST requests require a JSON object. Invalid requests return 400; unknown cases/regions return 404; AI endpoints return 503 without a configured key. Provider failures return a generic 500 response. The request size limit is 12 MiB; chat questions are limited to 4,000 characters. `OPTIONS` is supported for CORS preflight.

```bash
curl -H 'X-Model-ID: model_02' http://127.0.0.1:5000/case_info
curl -H 'Content-Type: application/json' -H 'X-Model-ID: model_02' \
  -d '{"zone_name":"roof"}' http://127.0.0.1:5000/explain_shape
```

## Export directory

```text
backend/data/models/model_01/
  result.json
  shape_regions.json
  pressure_regions.json
  click_map.json
  images/before_pressure.png
  images/after_pressure.png
```

`result.json` identifies `case_id`, `case_name`, a `drag` object (`before`, `after`, `delta`, `reduction_percent`), and relative image paths. `delta = before - after`; `reduction_percent = 100 * delta / before`. The before value must be positive.

Shape records contain `region_id`, `average_displacement`, `max_displacement`, `change_level`, `description`, and `possible_effect`. Displacement display assumes source meters. Pressure records contain `region_id`, `pressure_before_mean`, `pressure_after_mean`, `pressure_change`, and explanatory metadata. `pressure_change = after - before`; pressure units are unspecified in the supplied data.

Click records contain `region_id`, `image_keys`, and percentage image bounds (`x_min`, `x_max`, `y_min`, `y_max`). The original UI uses fixed hotspot positions and region IDs; these are illustrative, not pixel-accurate segmentation boundaries.
