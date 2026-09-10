"""
Precision Field Zoning & Satellite Water-Stress Detection Module for Agri Mitra.
Modular, portable Flask blueprint for spatial grid zoning, Sentinel-2 NDMI/NDVI water-stress detection,
multi-source data fusion (Satellite + Soil + Weather + Crop), and explainable irrigation attention.
"""

from .routes import precision_field_bp, init_precision_field

__all__ = ['precision_field_bp', 'init_precision_field']
