
# An Investigation into 2D Bin Packing

## Abstract

This investigation looks at heuristic approaches to two-dimensional bin
packing in the context of procedural building generation. Existing packing
algorithms were researched and implemented in Python to see how they behaved
under different conditions. The problem was then reformulated as a discrete,
grid-based packing problem using a fixed set of building-module dimensions.
The results were used to assess how suitable the different approaches were for
procedural generation and to inform the development of a grid-based packing
system in Blender Geometry Nodes.

## 1. Introduction

I started by looking at existing bin-packing algorithms, including the classic
First Fit algorithm. These approaches are continuous, meaning
they generally allow shapes to be placed at arbitrary coordinates within a
container. This is useful for general bin-packing problems, but it did not
quite fit the intended use case in Blender Geometry Nodes, where the building
face needed a more controlled, discrete structure. The continuous First Fit
implementation is kept in the `cont_bin_packing` folder as part of this work.

The discrete implementation is in the `disc_bin_packing` folder. It includes
module generation, grid occupancy management, packing algorithms, and a
matplotlib visualiser for inspecting the results interactively.


## 2. Background

### 2.1 The 2D Bin Packing Problem

In a survey by Lodi, Martello & Monaci, the problem of two-dimensional
bin packing (2D-BPP) is described as fitting *n* rectangular items into the minimum
number of identical rectangular bins of width *w* and height *h* [1]. It can be applied 
in areas such as cutting materials, loading and transportation, where objects cannot
overlap and need to be arranged efficiently.

In the classical 2D-BPP, the primary objective is to minimise the number of bins 
required to accommodate all items. In my case, the problem is slightly different.

### 2.2 Exact Algorithms

Exact algorithms search for the best possible solution to a problem. In the survey, 
Lodi et al. also discuss an "enumerate" strategy developed by Martello and Vigo for 
finding exact solutions to the 2D-BPP [1]. They can provide certainty that the most 
optimal solution has been found, but as the problem becomes more complicated, so 
does the computational demand.

### 2.3 Approximation Algorithms and Heuristics

On the other hand, approximation algorithms do not always guarantee the optimal
solution. Instead, they aim to find a satisfactory solution in less time. This makes
them more suitable for my use case, where the generative add-on needs to calculate
and render building facades quickly. Hence my decision to prioritise research on 
approximation algorithms over exact ones.

### 2.4 Problem Formulation

My problem is formulated as a discrete variant of the 2D-BPP based on the
following rules:

- There exists only a single "bin" of predetermined width and height.
- The bin is a grid made up of square 1×1 cells, each with integer coordinates.
- Modules (or "items") have fixed dimensions (1×1, 1×2, 2×2 etc).
- Modules may only be placed such that each of their constituent squares lie on 
  coordinates of cell(s).
- Modules must not overlap with each other.
- Every cell must be occupied in the final representation.


## 3. Existing Heuristic Algorithms

### 3.1 Next Fit Decreasing Height (NFDH)

The Next Fit Decreasing Height algorithm was one of the heuristics I
looked at. In this approach, rectangles are sorted by decreasing height and
placed into the current bin until the next rectangle no longer fits, at which
point a new bin is started. My continuous Next Fit implementation is kept in
`cont_bin_packing` folder as part of this work.

### 3.2 First Fit (FF)

Skyline packing was also considered as an alternative approach for the
investigation.

### 3.3 MaxRects

MaxRects was considered alongside First Feasible and shelf-based packing.

## 4. Methodology

I considered several packing approaches, including First Feasible, MaxRects,
and shelf-based packing. I selected First Feasible because its simple control
flow makes it a practical candidate for implementation in Blender Geometry
Nodes.

First Feasible depends on the order of the modules. For example, presenting
modules in the order
`3×3 -> 2×2 -> 1×3` can produce a completely different packing from presenting
the same modules as `1×3 -> 3×3 -> 2×2`.

For each module, the algorithm scans the grid in its configured direction and
immediately selects the first position where the module fits. It does not
compare all feasible positions or reconsider earlier placements to improve the
final result. The visualiser provides six scan-order variants:

- Bottom to Top, Left to Right
- Bottom to Top, Right to Left
- Top to Bottom, Left to Right
- Top to Bottom, Right to Left
- Left to Right, Bottom to Top
- Right to Left, Bottom to Top

The algorithm also has an application-specific completion step. The
`_fill_empty_cells()` method adds `1×1` filler modules to any cells that remain
empty after the requested modules have been processed. This completion step is
not inherently part of First Feasible. I added it because the building-face
use case requires a completely filled grid. Filler modules are marked with
`is_filler=True`, so they can be distinguished from the originally generated
modules when calculating utilisation and analysing the results.

### 4.1 Visualisation and experimentation

The Matplotlib visualiser connects First Feasible to an interactive grid
representation. It allows the grid dimensions, module count, module-size
weights, and scan-order variant to be changed. It reports runtime, requested
module cells, filler cells, occupied cells, and utilisation. The controls
update the packing so the effect of each parameter can be inspected without
manually rebuilding the experiment.

## 5. Experiments

The `stats_gen.py` script provides a separate quantitative experiment. It runs
multiple trials for a fixed grid and module count, then reports runtime,
utilisation, and the proportion of requested modules successfully packed for
each trial. It also generates scaling graphs for these measures as the module
count changes.

## 6. Results

### 6.1 Visual Evidence

The following renders show some example outputs from the First Feasible
visualiser:

![First Feasible packing](disc_bin_packing/algorithms/First%20Feasible.png)

![First Feasible packing variation 2](disc_bin_packing/algorithms/First%20Feasible%202.png)

![First Feasible packing variation 3](disc_bin_packing/algorithms/First%20Feasible%203.png)

![First Feasible packing variation 4](disc_bin_packing/algorithms/First%20Feasible%204.png)

The placement process is shown in the animation below:

![First Feasible animation](disc_bin_packing/algorithms/First%20Feasible%20(Anim).gif)

The scaling experiments produced the following graphs using a fixed 10 × 8
grid:

![Runtime scaling](disc_bin_packing/Scaling_Experiments/Runtime%20Scaling.png)

![Utilisation scaling](disc_bin_packing/Scaling_Experiments/Utilisation%20Scaling.png)

![Packed-module scaling](disc_bin_packing/Scaling_Experiments/Packed%20Scaling.png)

![Convergence point](disc_bin_packing/Scaling_Experiments/Convergence_Point.png)

### 6.2 Experimental Observations

For the scaling experiments, I kept the grid at 10 × 8 cells and varied the
target module count.

**Utilisation**

Utilisation initially increases as the module count increases. This is
expected: more requested modules generally occupy more cells, so fewer filler
modules are needed to complete the grid. At a module count of approximately
40, the grid was almost uniformly at 100% utilisation.

The trend eventually levels off and can dip slightly. Once the grid becomes
dense, the order-dependent placements can create fragmented gaps that cannot
be used. These gaps can prevent later modules from fitting even when some cell
area is still available. Filler modules still complete the physical grid, but
they are excluded from the useful-module utilisation measure.

**Runtime**

Runtime follows a fairly linear upward trend as the module count increases.
Each additional requested module creates more placement work, and the
algorithm checks candidate positions until it finds a feasible one or runs out
of grid space. As the module count grows, the runtime trend becomes less
uncertain. This suggests that latency becomes more predictable when the
algorithm has a larger and more consistent amount of work to perform.

**Successfully Packed Modules**

The proportion of successfully packed modules shows a different pattern. At
low module counts it stays at 100% because the grid has enough capacity for
all requested modules. Once a threshold module count is reached, the grid
cannot accommodate every request. The ratio of successfully packed modules to
the total requested modules then steadily decreases as more requests are made.

This shows the main limitation of First Feasible. Once the grid passes its
threshold, additional modules are increasingly likely to be rejected. Because
the algorithm does not revisit earlier decisions, fragmentation can prevent a
later module from fitting even when enough total area appears to remain.

## 7. Discussion

These results suggest that First Feasible is a good fit for Blender Geometry
Nodes when speed, simplicity, and predictable behaviour matter more than
optimal packing.

Its main strengths are:

- It is simple to implement procedurally.
- It is fast enough for interactive generation and parameter changes.
- Its runtime becomes increasingly predictable as the workload grows.
- It naturally fills sparse regions with `1×1` filler modules.
- It produces valid, completely filled grid representations without an
	expensive global optimisation stage.
- Its order dependence creates variation that can be useful for stylised
	procedural facades.

However, it is less suitable when every requested module must be placed, when
material efficiency matters, or when the facade has to satisfy strict
architectural constraints. For dense layouts, the output can depend strongly
on module order and scan direction, and the number of rejected modules can
become significant.

## 8. Application to Metropolis

For this use case, First Feasible is a strong candidate for interactive and
exploratory facade generation. A more powerful offline pass could be added
later for final production layouts. In the meantime, ordering larger modules
first, reserving regions for large modules, or comparing the six scan
directions can reduce fragmentation without giving up the algorithm's speed
and procedural simplicity.

## 9. Conclusion

First Feasible works well for interactive and exploratory facade generation
when speed, simplicity, and predictable behaviour matter more than optimal
packing. It produces valid, completely filled grid representations, but its
dependence on order and its tendency to create fragmentation make it less
suitable when every requested module must be placed or material efficiency is
important.

These results came from a fixed 10 × 8 grid for the scaling experiments, so
the observed thresholds should not be treated as universal properties of the
First Feasible algorithm. Different grid dimensions, module distributions, and
ordering strategies may produce different results.

## References

No external references are currently listed.

