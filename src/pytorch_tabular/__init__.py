"""Top-level package for Pytorch Tabular."""

__author__ = """Manu Joseph"""
__email__ = "manujosephv@gmail.com"
__version__ = "1.0.2"

from . import models, ssl_models
from .categorical_encoders import CategoricalEmbeddingTransformer
from .feature_extractor import DeepFeatureExtractor
from .tabular_datamodule import TabularDatamodule
from .tabular_model import TabularModel
from .tabular_model_tuner import TabularModelTuner

__all__ = [
    "TabularModel",
    "TabularModelTuner",
    "TabularDatamodule",
    "models",
    "ssl_models",
    "CategoricalEmbeddingTransformer",
    "DeepFeatureExtractor",
    "utils",
]

# fix Sphinx issues, see https://bit.ly/2K2eptM
for item in __all__:
    if hasattr(item, "__module__"):
        setattr(item, "__module__", __name__)


def available_models():
    return [cl for cl in dir(models) if "config" in cl.lower()]
