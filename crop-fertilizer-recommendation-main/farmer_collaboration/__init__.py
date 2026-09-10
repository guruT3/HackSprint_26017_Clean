"""
Farmer Collaboration & Mandi Marketplace Module (Farmer Connect)
Modular, portable Flask blueprint providing a digital agricultural collaboration ecosystem:
Community, Discussion Forum, Marketplace, Requirements Board, Mandi Hub, Messaging, and Trust Verification.
"""

from .routes import farmer_collaboration_bp, init_farmer_collaboration

__all__ = ['farmer_collaboration_bp', 'init_farmer_collaboration']
