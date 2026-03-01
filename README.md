# Swarm Simulation - Real-time GUI Visualization

A comprehensive interactive simulation of swarm intelligence featuring three distinct swarm types (ants, fish, birds) with emergent collective behaviors, multiple environments, intelligent communication systems, and coordinated attacks.

## ✨ Features

### 🐦 Bird Swarm (Air)
- **Behavior**: Boids flocking algorithm with cohesion, separation, alignment
- **Attacks**: Normal (1.0 dmg/sec) + Dive attacks (3.0 dmg, 4s cooldown)
- **Intelligence**: Coordinated dive attacks with chain reactions
- **Speed**: 4.0 px/sec

### 🐠 Fish Swarm (Water)
- **Behavior**: Tight schooling with democratic voting
- **Attacks**: Normal (1.5 dmg/sec) + Wave attacks (60% majority)
- **Intelligence**: Collective target voting, coordinated surges
- **Speed**: 3.0 px/sec

### 🐜 Ant Swarm (Ground)
- **Behavior**: Pheromone-based communication and trail following
- **Attacks**: Persistent attacks (1.0 dmg/sec)
- **Intelligence**: Emergent foraging via indirect stigmergy
- **Speed**: 2.0 px/sec

### 🌍 Three Dynamic Environments
- **Air**: Dynamic wind forces affecting movement
- **Water**: Realistic current patterns for navigation
- **Ground**: Terrain friction and pheromone grids

### 🔧 Advanced Systems
- **Spatial Hashing**: O(1) neighbor queries for 200+ agents
- **Pheromone Grid**: NumPy-based ant communication
- **Health System**: Targets with real-time health bars
- **Obstacle System**: Static barriers with collision avoidance
- **UI System**: Interactive buttons and real-time statistics

## 🚀 Quick Start

### Requirements
- Python 3.12+
- pygame-ce or pygame 2.5.2+
- NumPy 1.26.4+

### Installation
```bash
git clone https://github.com/JUPUDI-VAMSI-KALYAN/swarm-simulation.git
cd swarm-simulation
python3 -m pip install -r requirements.txt
```

### Running
```bash
python3 main.py
```

## 🎮 Controls

| Input | Action |
|-------|--------|
| **Left Click** | Place target |
| **Right Click** | Place obstacle |
| **Space** | Pause/Resume |
| **R** | Reset |
| **Q** | Quit |

### UI Buttons (Top Bar)
| Button | Effect |
|--------|--------|
| **BIRD / FISH / ANT** | Select swarm type |
| **GROUND / WATER / AIR** | Switch environment |
| **SPAWN x50** | Spawn 50 agents |
| **PAUSE** | Pause/Resume |

## 📊 How It Works

### Bird Flocking
```
Cohesion (30%):   Move toward group center
Separation (30%): Avoid crowding neighbors
Alignment (40%):  Match neighbor velocity
```
Birds dive on targets for 3x damage with coordinated attacks.

### Fish Schooling
```
Cohesion (25%):   Loose grouping
Separation (40%):  Strong spacing
Alignment (35%):  Moderate heading match
```
Fish vote democratically - 60%+ agreement triggers wave attacks.

### Ant Foraging
```
Pheromone Following:  Find food trails
Trail Deposition:     Mark successful paths
Evaporation (0.99):   Trails fade over time
Diffusion (0.1):      Spread to neighbors
```
Emergent collective intelligence without central planning.

## 🏗️ Architecture

```
src/
├── core/              # Foundation (Vector2D, Entity, Physics)
├── swarm/             # Three swarm types (Bird, Fish, Ant)
├── intelligence/      # AI behaviors (Flocking, Schooling, Pheromone)
├── environment/       # Three environments (Air, Water, Ground)
├── entities/          # Game objects (Targets, Obstacles)
├── rendering/         # Pygame visualization and UI
└── simulation/        # Main loop and input handling
```

## 📈 Performance

**Target**: 60 FPS with 200+ agents

**Tested Results**:
- 50 agents: 60 FPS stable
- 100 agents: 55-60 FPS
- 200 agents: 50-60 FPS
- 500 agents: 30-45 FPS

## 🎓 Learning Topics

This project demonstrates:
1. **Emergence**: Complex behaviors from simple rules
2. **Collective Intelligence**: Group decisions without central control
3. **Steering Behaviors**: Navigation and path planning
4. **Communication**: Direct and indirect messaging
5. **Physics Simulation**: Frame-rate independent movement
6. **Optimization**: Spatial hashing for scalability
7. **Game Development**: Real-time rendering and interaction

## 🎯 Try These Scenarios

1. **Basic Attack**: Spawn birds → Click to place target → Watch swarm attack
2. **Wave Attack**: Switch to fish/water → Place target → See 60%+ voting trigger wave
3. **Maze Navigation**: Place obstacles → Watch swarms navigate intelligently
4. **Pheromone Trails**: Switch to ants/ground → Observe emergent trail formation

## 📊 Simulation Parameters

### Swarm Stats
| Swarm | Speed | Attack Range | Perception | Solo Time |
|-------|-------|------|----------|---------|
| Birds | 4.0 px/s | 15 px | 100 px | 33-100s |
| Fish | 3.0 px/s | 12 px | 80 px | 50-67s |
| Ants | 2.0 px/s | 8 px | 60 px | 100s |

### Target Health
- Default: 100 HP
- Bird normal attack: 1.0 damage/sec
- Bird dive attack: 3.0 damage
- Fish normal attack: 1.5 damage/sec
- Fish wave attack: 2.0 damage

## 🤝 Contributing

The codebase is designed for extension:
1. Add new swarm type by inheriting `SwarmAgent`
2. Implement `calculate_steering_force()` method
3. Register in `SwarmController.spawn_swarm()`
4. Add UI button for the new type

## 📄 License

MIT License - Open source and free to use

## 📚 Documentation

- **QUICKSTART.md**: 5-minute getting started guide
- **DEPLOYMENT_SUMMARY.md**: Technical implementation details
- Inline code comments: Comprehensive documentation

## 🔬 Key Technologies

- **Python 3.12+**: Latest language features and optimizations
- **Pygame-CE**: Real-time 2D graphics rendering
- **NumPy**: Vectorized pheromone calculations
- **Object-Oriented Design**: Clean, extensible architecture
- **Boids Algorithm**: Proven swarm simulation technique
- **Spatial Hashing**: Performance optimization

---

**Status**: Production Ready ✓ | **Tests**: 19/19 Passing ✓

Built with passion for swarm intelligence and AI simulation.

i am dual
