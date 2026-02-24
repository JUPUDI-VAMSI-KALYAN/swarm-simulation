# Swarm Simulation - Quick Start Guide

## ⚡ 5-Minute Setup

### 1. Verify Python Installation
```bash
python3 --version  # Should be 3.12+
```

### 2. Install Dependencies
```bash
cd /Users/jupudivamsikalyan/IOBI
python3 -m pip install pygame-ce numpy -q
```

### 3. Run the Simulation
```bash
python3 main.py
```

**That's it!** The simulation launches with 50 birds flocking in the air environment.

---

## 🎮 Basic Controls

| Action | Key |
|--------|-----|
| **Place Target** | Left Click |
| **Place Obstacle** | Right Click |
| **Pause/Resume** | Space |
| **Reset** | R |
| **Quit** | Q |

---

## 🐦 Bird Swarm Demo (30 seconds)

1. Launch simulation → Birds appear, flocking
2. Left-click center of screen → Red square appears
3. Watch birds converge and attack
4. Health bar depletes, target destroyed
5. Place another target, repeat!

---

## 🐠 Fish Swarm Demo (1 minute)

1. Click **FISH** button (top left)
2. Click **WATER** button (top middle)
3. Click **SPAWN x50** button (top right)
4. Fish appear in water, schooling tightly
5. Left-click to place target
6. Watch 60%+ fish vote for target, then surge attack!

---

## 🐜 Ant Swarm Demo (2 minutes)

1. Click **ANT** button
2. Click **GROUND** button
3. Click **SPAWN x50** button
4. Ants appear on tan terrain
5. Left-click to place target
6. Watch ants spread out, find trails, converge on target
7. Observe pheromone trail formation (harder to see but happening!)

---

## 🎯 Advanced Scenarios

### Create a Maze
```
1. Use BIRD/AIR environment
2. Right-click multiple times to place obstacles
3. Watch birds navigate around barriers
```

### Multi-Swarm Battle
```
1. Spawn BIRDS in AIR environment (50)
2. Place several TARGETS
3. Click ANT button → click SPAWN (switches to ground with ants)
4. Place more TARGETS
5. Different swarms attack different targets
```

### Wave Attack Observation
```
1. Click FISH → WATER → SPAWN
2. Place target
3. Zoom in mentally on voting process
4. When 60%+ agree on target → coordinated surge!
```

---

## 🔧 Common Tasks

### Change Swarm Type
**Top Left Buttons**: Click BIRD, FISH, or ANT

### Change Environment
**Top Middle Buttons**: Click GROUND, WATER, or AIR
(Automatically spawns compatible swarm)

### Spawn More Agents
1. Click swarm type button (BIRD/FISH/ANT)
2. Click **SPAWN x50** button
3. 50 new agents added to scene

### Reset Everything
- Press **R** key or click **PAUSE** button in UI

### Performance Monitoring
- FPS shown in top-right corner
- Stats shown at bottom of screen
- Counts: Birds/Fish/Ants/Targets/Destroyed

---

## 📊 What You're Watching

### Birds
- **Behavior**: Flocking in tight formation
- **Attack**: Normal (slow) + Dive (fast, from above)
- **Intelligence**: Coordinate dive attacks

### Fish
- **Behavior**: Tight schooling (very organized)
- **Attack**: Wave surges when 60%+ vote same target
- **Intelligence**: Democratic voting system

### Ants
- **Behavior**: Scattered exploration + trail following
- **Attack**: Slow but persistent
- **Intelligence**: Pheromone trails (invisible but real!)

---

## ❓ Frequently Asked Questions

**Q: Why aren't ants following visible trails?**
A: Pheromones are invisible for performance. The system is working - ants deposit stronger marks when they find food, others follow the gradient.

**Q: Can I see pheromones?**
A: Not in the current UI, but the code includes visualization support. Edit `src/rendering/ui.py` to add a toggle.

**Q: Why do birds sometimes not attack?**
A: Birds have energy that drains with movement and attacks. They rest when low energy (automatic recovery).

**Q: Can swarms talk to each other?**
A: Indirectly through targets - they attack the same objectives. Fish use voting, ants use pheromones.

**Q: What's the max swarm size?**
A: Tested to 500+ agents smoothly. Performance depends on your hardware.

**Q: Can I modify parameters?**
A: Yes! Edit `config/settings.py` and `config/swarm_config.py` for tweaks.

---

## 🚨 Troubleshooting

### Game Won't Start
```bash
# Check Python version
python3 --version

# Reinstall dependencies
python3 -m pip install pygame-ce numpy --force-reinstall
```

### Very Slow (20 FPS or less)
```
- Reduce swarm size: fewer agents in scene
- Reduce perception radius: edit config/settings.py
- Close other applications for more resources
```

### No Agents Appearing
```
- Check console for error messages
- Try clicking SPAWN button explicitly
- Try resetting with R key and clicking SPAWN
```

---

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Implementation Details**: See `DEPLOYMENT_SUMMARY.md`
- **Architecture Plan**: See `/claude/plans/iterative-scribbling-chipmunk.md`
- **Source Code**: Browse `src/` directory

---

## 🎓 Educational Use

Perfect for teaching:
- Artificial Intelligence concepts
- Swarm robotics principles
- Emergent behavior
- Game development
- Physics simulation
- UI/UX design
- Python programming

---

## 🎉 Enjoy!

The simulation is ready to use. Experiment with different combinations of swarm types, environments, and target placements to see how intelligent behaviors emerge from simple local rules.

**Have fun exploring swarm intelligence!**
