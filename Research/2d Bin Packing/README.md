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

In a survey by Lodi, Martello & Monaci (2002), the problem of two-dimensional
bin packing (2D-BPP) is described as fitting *n* rectangular items into the minimum
number of identical rectangular bins of width *w* and height *h* [1]. It can be applied 
in areas such as cutting materials, loading and transportation, where objects cannot
overlap and need to be arranged efficiently.

In the classical 2D-BPP, the goal is to minimise the number of bins 
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

Christensen et al. (2017) describe NFDH as ordering the items from tallest to shortest, before placing them into "shelves". Each shelf consists of items placed next to each other with their bases aligned horizontally, with the first shelf starting at the bottom of the bin and subsequent shelves placed with its base resting flat on top of the tallest item in the shelf below [2].

### 3.2 First Fit (FF)

First Fit is a simple algorithm where items are considered one at a time. Johnson et al. (1974) describe it as placing each item into the first bin in which it fits. If it cannot be placed in any of the existing bins, a new bin is opened. [3] Once an item has been placed, the algorithm does not at any point go back and change its position. Because of this, the algorithm is less efficient than "enumerate" approaches, but it is certainly faster.

### 3.3 Maximal Rectangles (MaxRects)

In Jukka Jylänki's paper A Thousand Ways To Pack The Bin, he describes MaxRects as an algorithm that divides the bin into the largest rectangular regions available [4]. When an item is placed, these regions are updated to represent the space that remains available. The algorithm then chooses a suitable free rectangle for the next item using a heuristic such as Best Area Fit or Best Short Side Fit. This allows MaxRects to make use of irregular spaces left by previously placed items. Although it is an efficient algorithm, its complexity costs significant runtime.

## 4. Methodology

After considering these approaches I felt that First Fit was the most practical 
candidate for implementation in Blender Geometry Nodes. However, there were 
some parts of the algorithm, like how it involved multiple bins, that differed from 
my end goal. Thus, I adapted it into a new algorithm called First Feasible.

First Feasible depends on the order of the modules. For example, inputting
modules in the order *3×3 -> 2×2 -> 1×3* can result in a completely different 
packing from inputting the same modules as *1×3 -> 3×3 -> 2×2*.

For each module, the algorithm scans the grid in the configured direction and
immediately selects the first position where the module fits. It does not
compare all feasible positions or reconsider earlier placements to improve the
final result. My visualiser provides six scan-order variants:

- Bottom to Top, Left to Right
- Bottom to Top, Right to Left
- Top to Bottom, Left to Right
- Top to Bottom, Right to Left
- Left to Right, Bottom to Top
- Right to Left, Bottom to Top

The algorithm also includes a completion step specific for my application. The
`_fill_empty_cells()` method adds `1×1` filler modules to any cells that remain
empty after the requested modules have been processed. This completion step is
not inherently part of the First Feasible algorithm. I simply added it because the 
building facade use case requires a completely filled grid. Filler modules are marked 
with the attribute `is_filler=True`, so they can be distinguished from the originally 
generated modules when calculating utilisation (the proportion of cells successfully filled 
by the packing algorithm) and analysing the results.

### 4.1 Visualisation and experimentation

The Matplotlib visualiser connects `first_feasible.py` to an interactive grid
representation. It allows the grid dimensions, module count, module-size
weights, and scan-order variant to be changed. It reports the runtime, requested
module cells, number of filler cells, occupied cells, and utilisation. The controls
update the packing in real time so that the effect of each parameter can be inspected 
without re-running the experiment.

## 5. Experiments

The `stats_gen.py` script is a separate quantitative experiment. It can run
up to 30 trials for a set grid size and module count, then reports runtime,
utilisation, and the proportion of requested modules successfully packed for
each trial. It also has options generate scaling graphs for each of these measures 
as the module count changes.

## 6. Results

### 6.1 Visual Evidence

The following renders show some snapshots of the First Feasible visualiser output
during different stages as I worked on cleaning up its interface.

![First Feasible packing](disc_bin_packing/algorithms/First%20Feasible.png)

![First Feasible packing variation 2](disc_bin_packing/algorithms/First%20Feasible%202.png)

![First Feasible packing variation 3](disc_bin_packing/algorithms/First%20Feasible%203.png)

![First Feasible packing variation 4](disc_bin_packing/algorithms/First%20Feasible%204.png)

The placement process is shown in the animation below:

![First Feasible animation](disc_bin_packing/algorithms/First%20Feasible%20(Anim).gif)

The scaling experiments produced the following graphs using a fixed 10 × 8 grid/bin:

![Runtime scaling](disc_bin_packing/scaling%20experiment/Runtime%20Scaling.png)

![Utilisation scaling](disc_bin_packing/scaling%20experiment/Utilisation%20Scaling.png)

![Packed-module scaling](disc_bin_packing/scaling%20experiment/Packed%20Scaling.png)

![Convergence point](disc_bin_packing/scaling%20experiment/Convergence_Point.png)

### 6.2 Experimental Observations

For the scaling experiments, I kept the grid at 10 × 8 cells and varied the 
target module count.

**Utilisation**

Utilisation initially increases as the module count increases. This is
expected expected as the requested modules are all successfully packed until the 
grid starts to fill up. At a module count of around 40, the grid was almost uniformly 
at 100% utilisation.

The trend eventually levels off and can dip slightly. Once the grid becomes
dense, the order-dependent placements can cause fragmentation, creating gaps 
that cannot be used. These gaps can prevent future modules from fitting even though
some cells are still available. Filler modules still complete the physical grid, but
they are excluded from the useful module utilisation calculation.

**Runtime**

Runtime follows quite a linear upward trend as the module count increases because 
each additional requested module creates more work. As the module count grows, 
the uncertainty in the gradient decreases. This suggests that latency becomes more 
predictable when a larger amount of work has to be done.

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

These results show that First Feasible is a good fit for Blender Geometry
Nodes where speed, simplicity, and predictable behaviour matters more than
getting an optimal packing.

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

The final aim of this research is to apply my First Feasible algorithm to my procedural building generator, _Metropolis_. The algorithm will determine where each architectural module can be placed on a predefined discrete facade grid, while ensuring that modules do not overlap or extend beyond the building. 

In Geometry Nodes, I plan to use the ***grid*** node followed by ***mesh to points*** and ***instance on points*** to generate the cells. I will then implement the algorithm using Blender's ***repeat zone*** as well as boolean nodes like ***and***, ***or*** and ***not*** to control which cells are being selected. I will use an "occupied" ***attribute*** to control which cells are chosen to place modules on. 

The algorithm's output will determine the coordinates and module types, which can then be used to instance the corresponding geometry. This separates the computational problem of deciding where modules can be placed from the visual design of the modules themselves, allowing different facade styles to be generated using the same underlying algorithm.

## 9. Conclusion

First Feasible works quite well for quick and interactive facade generation
when speed, simplicity, and predictable behaviour matter more than optimal
packing. It produces valid, completely filled grid representations, but its
dependence on order and its tendency to create fragmentation makes it less
suitable when every requested module must be placed or material efficiency is
important.

**Note**: these results came from a fixed 10 × 8 grid for the scaling experiments, so
the observed thresholds should not be treated as universal properties of the
First Feasible algorithm. Different grid dimensions, module distributions, and
ordering strategies may produce different results.

## References

1. Lodi, A., Martello, S. and Monaci, M. (2002). ‘Two-dimensional packing problems: A survey’. _European Journal of Operational Research_, 141(2), pp. 241–252. DOI: 10.1016/S0377-2217(02)00123-6.
2. Christensen, H. I., Khan, A., Pokutta, S. and Tetali, P. (2017). ‘Approximation and online algorithms for multidimensional bin packing: A survey’. _Computer Science Review_, 24, pp. 63–79. DOI: 10.1016/j.cosrev.2016.12.001.
3. Johnson, D. S., Demers, A., Ullman, J. D., Garey, M. R. and Graham, R. L. (1974). ‘Worst-Case Performance Bounds for Simple One-Dimensional Packing Algorithms’. _SIAM Journal on Computing_, 3(4), pp. 299–325. DOI: 10.1137/0203025.
4. Jylänki, J. (2010). ‘A Thousand Ways to Pack the Bin – A Practical Approach to Two-Dimensional Rectangle Bin Packing’. Technical report.

