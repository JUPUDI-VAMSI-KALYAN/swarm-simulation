#!/usr/bin/env python3
"""
Swarm Simulation - Real-time GUI visualization of swarm intelligence.

Main entry point for the application.
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.simulation.simulation import Simulation


def main():
    """Run the simulation."""
    sim = Simulation()
    sim.run()


if __name__ == "__main__":
    main()
