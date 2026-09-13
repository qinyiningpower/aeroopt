# data_loader.py


import json
import os
import base64
from typing import Dict, List, Optional, Any


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data')
MODELS_DIR = os.path.join(DATA_DIR, 'models')

class DataLoader:


    def __init__(self):
        self.current_model_id = None
        self.result = None
        self.shape_regions = None
        self.pressure_regions = None
        self.click_map = None

        self._load_default_model()

    def _load_default_model(self):

        available = self.get_available_models()
        if available:
            self.load_model(available[0])
        else:
            print("No models found in data/models/")

    def get_available_models(self) -> List[str]:

        if not os.path.exists(MODELS_DIR):
            return []

        models = []
        for item in os.listdir(MODELS_DIR):
            item_path = os.path.join(MODELS_DIR, item)
            result_path = os.path.join(item_path, 'result.json')
            if os.path.isdir(item_path) and os.path.exists(result_path):
                models.append(item)
        return sorted(models)

    def load_model(self, model_id: str) -> bool:


        if model_id not in self.get_available_models():
            return False
        model_path = os.path.join(MODELS_DIR, model_id)

        if not os.path.exists(model_path):
            print(f"Model {model_id} not found at {model_path}")
            return False

        print(f"Loading model: {model_id}")


        self.current_model_id = model_id
        self.result = None
        self.shape_regions = None
        self.pressure_regions = None
        self.click_map = None


        result_path = os.path.join(model_path, 'result.json')
        if os.path.exists(result_path):
            with open(result_path, 'r', encoding='utf-8') as f:
                self.result = json.load(f)
            print(f"Loaded: result.json")
        else:
            print(f"result.json not found in {model_path}")
            return False


        shape_path = os.path.join(model_path, 'shape_regions.json')
        if os.path.exists(shape_path):
            with open(shape_path, 'r', encoding='utf-8') as f:
                self.shape_regions = json.load(f)
            print(f"Loaded: shape_regions.json")


        pressure_path = os.path.join(model_path, 'pressure_regions.json')
        if os.path.exists(pressure_path):
            with open(pressure_path, 'r', encoding='utf-8') as f:
                self.pressure_regions = json.load(f)
            print(f"Loaded: pressure_regions.json")


        click_path = os.path.join(model_path, 'click_map.json')
        if os.path.exists(click_path):
            with open(click_path, 'r', encoding='utf-8') as f:
                self.click_map = json.load(f)
            print(f"Loaded: click_map.json")

        self.current_model_id = model_id
        print(f"Model {model_id} loaded successfully")
        return True


    def get_current_model_id(self) -> str:
        return self.current_model_id

    def get_case_id(self) -> str:
        return self.result.get('case_id', 'unknown') if self.result else 'unknown'

    def get_case_name(self) -> str:
        return self.result.get('case_name', 'unknown') if self.result else 'unknown'

    def get_drag_before(self) -> float:
        return self.result.get('drag', {}).get('before', 0.0) if self.result else 0.0

    def get_drag_after(self) -> float:
        return self.result.get('drag', {}).get('after', 0.0) if self.result else 0.0

    def get_drag_delta(self) -> float:
        return self.result.get('drag', {}).get('delta', 0.0) if self.result else 0.0

    def get_drag_reduction_percent(self) -> float:
        return self.result.get('drag', {}).get('reduction_percent', 0.0) if self.result else 0.0


    def get_image_path(self, key: str = 'before_pressure') -> Optional[str]:


        if not self.result or not self.current_model_id:
            return None

        image_rel_path = self.result.get('images', {}).get(key, '')
        if not image_rel_path:
            return None

        model_path = os.path.join(MODELS_DIR, self.current_model_id)
        return os.path.join(model_path, image_rel_path)

    def get_image_base64(self, key: str = 'before_pressure') -> Optional[str]:


        image_path = self.get_image_path(key)
        if not image_path or not os.path.exists(image_path):
            print(f" Image not found: {image_path}")
            return None

        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                return base64.b64encode(image_data).decode('utf-8')
        except Exception as e:
            print(f" Error reading image {image_path}: {e}")
            return None

    def get_both_images_base64(self):


        before = self.get_image_base64('before_pressure')
        after = self.get_image_base64('after_pressure')
        return before, after


    def get_shape_regions(self) -> Optional[List]:

        return self.shape_regions

    def get_shape_region_by_id(self, region_id: str) -> Optional[Dict]:

        if not self.shape_regions:
            return None
        for region in self.shape_regions:
            if region.get('region_id') == region_id:
                return region
        return None

    def get_all_shape_region_ids(self) -> List[str]:
        if not self.shape_regions:
            return []
        return [r.get('region_id') for r in self.shape_regions if r.get('region_id')]


    def get_pressure_regions(self) -> Optional[List]:

        return self.pressure_regions

    def get_pressure_region_by_id(self, region_id: str) -> Optional[Dict]:

        if not self.pressure_regions:
            return None
        for region in self.pressure_regions:
            if region.get('region_id') == region_id:
                return region
        return None

    def get_pressure_change(self, region_id: str) -> Optional[float]:

        region = self.get_pressure_region_by_id(region_id)
        return region.get('pressure_change') if region else None


    def get_click_map(self) -> Optional[List]:

        return self.click_map

    def get_click_coords_by_id(self, region_id: str) -> Optional[Dict]:

        if not self.click_map:
            return None
        for item in self.click_map:
            if item.get('region_id') == region_id:
                return item
        return None

    def find_region_by_point(self, x: float, y: float) -> Optional[str]:

        if not self.click_map:
            return None
        for item in self.click_map:
            region_id = item.get('region_id')
            coords = self.get_click_coords_by_id(region_id)
            if coords:
                x_min = coords.get('x_min', 0)
                x_max = coords.get('x_max', 0)
                y_min = coords.get('y_min', 0)
                y_max = coords.get('y_max', 0)
                if x_min <= x <= x_max and y_min <= y <= y_max:
                    return region_id
        return None


    def get_region_summary(self, region_id: str) -> Dict:

        return {
            'region_id': region_id,
            'shape': self.get_shape_region_by_id(region_id),
            'pressure': self.get_pressure_region_by_id(region_id),
            'click_coords': self.get_click_coords_by_id(region_id)
        }


    def get_full_context_for_ai(self) -> str:

        context = f"""
   Vehicle Case: {self.get_case_name()}
   Case ID: {self.get_case_id()}
   Drag Coefficient: {self.get_drag_before()} → {self.get_drag_after()}
   Reduction: {self.get_drag_reduction_percent()}%

   """
        if self.shape_regions:
            context += "Vehicle Shape Regions:\n"
            for region in self.shape_regions:
                region_id = region.get('region_id', 'Unknown')
                avg_disp = region.get('average_displacement', 0)
                context += f"  - {region_id}: avg displacement = {avg_disp * 1000:.1f}mm\n"

        if self.pressure_regions:
            context += "\nPressure Changes:\n"
            for region in self.pressure_regions:
                region_id = region.get('region_id', 'Unknown')
                before = region.get('pressure_before_mean', 0)
                after = region.get('pressure_after_mean', 0)
                context += f"  - {region_id}: {before:.3f} → {after:.3f}\n"

        return context

    def is_data_loaded(self) -> bool:
        return self.result is not None


from flask import g
from werkzeug.local import LocalProxy

def current_loader():
    if "case_loader" not in g:
        g.case_loader = DataLoader()
    return g.case_loader

data_loader = LocalProxy(current_loader)
