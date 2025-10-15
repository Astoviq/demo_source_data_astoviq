"""
EuroStyle Data Generation Generators Package
==========================================

WARP.md compliant entity generators following configuration-driven principles.

This package provides specialized generators for different domain entities:
- WebshopEntityGenerator: Product reviews, email marketing, search queries, etc.

All generators follow YAML configuration patterns and dependency injection.
"""

from .webshop_generators import WebshopEntityGenerator

__all__ = ['WebshopEntityGenerator']