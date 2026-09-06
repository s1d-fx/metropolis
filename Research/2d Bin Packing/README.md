# An Investigation into 2D Bin Packing

## Abstract

This investigation looks at heuristic approaches to two-dimensional bin
packing in the context of procedural building generation. Existing packing
algorithms were researched and a continuous packing prototype was implemented
in Python to see how it behaved under different conditions. The problem was
then reformulated as a discrete, grid-based packing problem using a fixed set
of building-module dimensions. The resulting grid-based prototypes were used to
assess their suitability for procedural generation and to inform the development
of a grid-based packing system in Blender Geometry Nodes.

## 1. Introduction

I began by examining existing bin-packing algorithms, including First Fit,
Next Fit Decreasing Height (NFDH), and MaxRects. These methods are generally
continuous, allowing shapes to be placed at arbitrary coordinates within a
container. Although this is useful for general bin-packing problems, it does
not directly suit the intended use case in Blender Geometry Nodes, where
building facades are represented by a controlled, discrete grid. A continuous
Next Fit prototype is retained in the `cont_bin_packing` folder, while
discrete versions of NFDH and MaxRects were implemented for comparison.

The main implementation is contained in the `disc_bin_packing` folder. It
includes module generation, grid occupancy management, several packing
algorithms, and a Matplotlib visualiser for inspecting the results
interactively. The purpose of this work is to compare these approaches and
assess how suitable they are for fast, repeatable procedural facade
generation.


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
starting point for implementation in Blender Geometry Nodes. However, there were
some parts of the algorithm, like how it involved multiple bins, that differed
from my end goal. Thus, I adapted it into a new algorithm called First Feasible
and implemented discrete versions of NFDH and MaxRects for comparison.

First Feasible depends on the order of the modules. For example, inputting
modules in the order *3×3 -> 2×2 -> 1×3* can result in a completely different
packing from inputting the same modules as *1×3 -> 3×3 -> 2×2*.

For each module, First Feasible scans the grid and immediately selects the first
position where the module fits. It does not compare all feasible positions or
reconsider earlier placements to improve the final result. NFDH instead sorts
modules by height and places them into horizontal shelves. MaxRects maintains
the available rectangular regions and selects a position using the Best Short
Side Fit heuristic. These differences make it possible to compare a simple
first-fit style approach with methods that use more information about the remaining
space.

All three algorithms also include a completion step specific for my application. The
`_fill_empty_cells()` method adds `1×1` filler modules to any cells that remain
empty after the requested modules have been processed. This completion step is
not inherently part of the First Feasible algorithm. I simply added it because the 
building facade use case requires a completely filled grid. Filler modules are marked 
with the attribute `is_filler=True`, so they can be distinguished from the originally 
generated modules when calculating utilisation (the proportion of cells successfully filled 
by the packing algorithm) and analysing the results.

### 4.1 Visualisation and experimentation

The Matplotlib visualiser connects the algorithms' scripts to an interactive grid
representation. It allows the grid dimensions, module count, module-size
weights, and algorithm to be changed. It reports the runtime, requested module
cells, number of filler cells, occupied cells, and utilisation. The controls
update the packing in real time so that the effect of each algorithm can be
inspected without restarting the visualiser.

## 5. Experiments

The `stats_gen.py` script is a separate quantitative experiment. It can run
up to 30 trials for a set grid size and module count, then reports runtime,
utilisation, and the proportion of requested modules successfully packed for
each trial. It also has options to generate scaling graphs for each of these measures
as the module count changes.

For the scaling plots, I used a 10 × 8 grid, 10 trials per module count, and
equal weights for each permitted module size. Module counts start at 1 and then
increase in steps of 5 up to a final point at 120. The default base seed is 2026. Each action advances a run counter and uses
`base seed + (run number - 1)`, so clicking Run experiment again produces a new input
distribution. The active seed and run number are shown in the interface. The
base seed can be changed from the command line with
`python stats_gen.py --seed 1234`. To reproduce a result, use the same base
seed and the same run number. Packing metrics are therefore repeatable;
measured runtime can still vary slightly with system load.

Runtime measures only the call to the packing algorithm; the runtime plot
shows the mean with error bars of ±1 standard deviation.

The algorithm comparison uses the same generated module list for First Feasible,
NFDH, and MaxRects (Best Short Side Fit) within each trial. The generator uses
the same generated module list, module-size weights, grid dimensions, and
requested module counts within each comparison run. This controls the input
distribution so that differences in the results are attributable to the
placement heuristics rather than different random inputs. The algorithms are
still timed independently, and the chart reports their mean runtime, useful
utilisation before filler modules, and proportion of requested modules packed.

To check how close the heuristics are to a best possible result, I also added
`optimal_baseline.py`. It uses exhaustive search on small 4 × 4 instances,
trying every legal placement and every possible decision to leave a module
unpacked. The baseline maximises the number of requested module cells placed,
then uses the number of packed modules as a tie-breaker. I deliberately
limited this to small inputs because a full search becomes impractical as the
grid and module count increase.

## 6. Results

### 6.1 Visual Evidence

The following renders show snapshots of the three algorithm visualiser outputs
using the same generated module inputs.

![Algorithm packing comparison](disc_bin_packing/algorithms/First%20Feasible.png)

*Figure 1. First Feasible, NFDH, and MaxRects packing the same 20 × 15 input grid with 105 requested modules.*

![Algorithm packing comparison variation 2](disc_bin_packing/algorithms/First%20Feasible%202.png)

*Figure 2. A three-algorithm comparison on a 10 × 8 grid with 40 requested modules.*

![Algorithm packing comparison variation 3](disc_bin_packing/algorithms/First%20Feasible%203.png)

*Figure 3. A three-algorithm comparison on a 10 × 8 grid, showing useful module placement before filler completion.*

![Algorithm packing comparison variation 4](disc_bin_packing/algorithms/First%20Feasible%204.png)

*Figure 4. The current three-algorithm visualiser comparison, with one panel for each algorithm.*

The placement process is shown in the animation below:

![Algorithm packing animation](disc_bin_packing/algorithms/First%20Feasible%20(Anim).gif)

*Animation 1. First Feasible, NFDH, and MaxRects placing the same generated
sequence of modules into the grid.*

The scaling experiments produced the following graphs using a fixed 10 × 8 grid/bin:

![Runtime scaling](disc_bin_packing/Scaling_Experiments/Runtime%20Scaling.png)

*Figure 5. Mean packing runtime as module count increases, shown separately for each algorithm across 10 trials.*

![Utilisation scaling](disc_bin_packing/Scaling_Experiments/Utilisation%20Scaling.png)

*Figure 6. Mean useful utilisation as module count increases, shown separately for each algorithm on a fixed 10 × 8 grid.*

![Modules packed scaling](disc_bin_packing/Scaling_Experiments/Packed%20Scaling.png)

*Figure 7. Mean proportion of requested modules successfully packed as module count increases, shown separately for each algorithm.*

![Algorithm runtime experiment](disc_bin_packing/Scaling_Experiments/Convergence_Point.png)

*Figure 8. An 18-trial runtime experiment for 25 requested modules on a 10 × 8 grid, shown separately for each algorithm.*

![Algorithm comparison](disc_bin_packing/Scaling_Experiments/Algorithm%20Comparison.png)

*Figure 9. Controlled comparison of First Feasible, NFDH, and MaxRects (BSSF) on
the same generated module sequences.*

### 6.2 Experimental Observations

For the scaling experiments, I kept the grid at 10 × 8 cells and varied the
target module count for each algorithm.

**Utilisation**

Utilisation initially increases as the module count increases. This is expected
as the requested modules are all successfully packed until the grid starts to
fill up. At a module count of around 40, the grid was close to full for all
three algorithms, although the exact point at which each curve levels off
depends on the seed of module generation.

The trend eventually levels off and can dip slightly. For First Feasible, the
order-dependent placements can create fragmented gaps that prevent later
modules from fitting even when some cells are still available. NFDH reduces
some of this variation by grouping modules into shelves, but unused horizontal
space at the end of a shelf can also reduce utilisation. MaxRects can make
better use of irregular gaps because it tracks free rectangles, although its
result still depends on the order of the modules and the selected fit
heuristic. Filler modules complete the physical grid, but they are excluded
from the useful module utilisation calculation.

**Runtime**

Runtime also increases as the module count increases because each
additional requested module creates more work. First Feasible performs a direct
grid scan, so its work is relatively simple but can increase when many
positions must be checked. NFDH adds the cost of sorting the modules before
placement. MaxRects performs more bookkeeping while splitting and comparing
free rectangles, so it is expected to take longer even when it produces a
better packing. As the module count grows, the uncertainty in the gradient
decreases, making the relative runtime behaviour easier to compare.

**Successfully Packed Modules**

The proportion of successfully packed modules shows a very different pattern.
At low module counts it stays at 100% because the grid always has enough cells
for all requested modules. Once a "threshold" module count is reached, the grid
cannot accommodate every request. The ratio of successfully packed modules to
the total requested modules then decreases as more requests are made.

This exposes the main limitation of First Feasible. Once the grid passes its
threshold, additional modules are increasingly likely to be rejected. Because
the algorithm does not go back to question earlier decisions, fragmentation can
prevent a later module from fitting even when enough total area appears to remain.
NFDH can avoid some of these fragmented gaps when the module heights suit its
shelf structure, but it may reject modules that do not fit the current shelf.
MaxRects
usually has more information available when choosing a placement, so it can
delay this point on some inputs, but that improvement comes with extra runtime
and is not guaranteed for every random sequence.

**Controlled algorithm comparison**

The comparison chart should be interpreted as a trade-off rather than a single
ranking. First Feasible scans for the first valid location and is therefore
simple and predictable, but it can leave fragmented gaps. NFDH groups modules
into height-based shelves, which can use space efficiently for compatible
height distributions but can waste horizontal space at shelf boundaries.
MaxRects keeps a set of free rectangles and selects the best short-side fit,
so it can usually respond better to irregular gaps at the cost of additional
bookkeeping and runtime. A higher useful-utilisation or packed-module curve
means more of the requested modules were placed before completion fillers were
added; it does not mean the filler cells themselves were useful placements.
Runtime differences should be considered alongside those packing metrics, since
the measurements include only each algorithm's `pack` call and exclude chart
rendering and input generation.

**Small-instance optimality baseline**

The exhaustive baseline provides a reference point rather than another
scalable algorithm. On the 4 × 4 benchmark cases, the gap is the number of
requested module cells between the optimal result and each heuristic result.
A gap of zero means that the heuristic matched the best packing for that input;
it does not prove that the heuristic is always optimal on larger or different
inputs. The baseline is useful because it tests the main claim directly: how
much packing quality is being traded for the speed and simplicity of each
heuristic.

| Seed | Optimal cells | First Feasible | NFDH | MaxRects (BSSF) |
| ---: | ---: | ---: | ---: | ---: |
| 11 | 16 | 16 (gap 0) | 12 (gap 4) | 16 (gap 0) |
| 22 | 14 | 14 (gap 0) | 12 (gap 2) | 14 (gap 0) |
| 33 | 15 | 15 (gap 0) | 15 (gap 0) | 15 (gap 0) |

These three cases are too small to support a general ranking, but they show
why the baseline is useful. First Feasible and MaxRects matched the optimum
on these inputs, while NFDH left more unused requested-module area on two of
the cases. More cases and larger small instances would be needed before
drawing a stronger conclusion.

## 7. Discussion

These results show that the three algorithms offer different trade-offs for
Blender Geometry Nodes. First Feasible is a promising fit where speed,
simplicity, and predictable behaviour matter more than getting an optimal
packing. NFDH provides a structured alternative that can work well when the
module heights form compatible shelves. MaxRects is the most deliberate of the
three because it considers the available rectangular regions, but this also
increases its runtime and implementation complexity.

First Feasible is simple to implement procedurally, fast enough for interactive
generation, and naturally fills sparse regions with `1×1` filler modules.
NFDH remains relatively straightforward while imposing a consistent shelf
structure. MaxRects can make better use of fragmented space and can improve
the number of requested modules packed on some inputs, but it requires more
bookkeeping and does not guarantee a better result for every sequence.

None of the approaches guarantees that every requested module will be placed.
For dense layouts, the output can depend on module order and the available
space left by earlier decisions. This makes First Feasible and NFDH less
suitable when material efficiency is the main priority, while MaxRects is less
suitable when the additional runtime and complexity cannot be justified.

## 8. Application to Metropolis

The final aim of this research is to apply the most suitable packing approach
to my procedural building generator, _Metropolis_. The selected algorithm will
determine where each architectural module can be placed on a predefined
discrete facade grid, while ensuring that modules do not overlap or extend
beyond the building.

In Geometry Nodes, I plan to use the ***grid*** node followed by ***mesh to points*** and ***instance on points*** to generate the cells. I will then implement the algorithm using Blender's ***repeat zone*** as well as boolean nodes like ***and***, ***or*** and ***not*** to control which cells are being selected. I will use an "occupied" ***attribute*** to control which cells are chosen to place modules on. 

The algorithm's output will determine the coordinates and module types, which can then be used to instance the corresponding geometry. This separates the computational problem of deciding where modules can be placed from the visual design of the modules themselves, allowing different facade styles to be generated using the same underlying algorithm.

## 9. Conclusion

First Feasible works quite well for quick and interactive facade generation
when speed, simplicity, and predictable behaviour matter more than optimal
packing. NFDH offers a useful shelf-based alternative, while MaxRects can
achieve stronger space usage on some inputs by considering irregular free
regions. The comparison shows that no single heuristic is best for every
facade: First Feasible prioritises simplicity, NFDH prioritises structured
placement, and MaxRects prioritises space management at a higher computational
cost. All three produce valid, completely filled grid representations, but
their dependence on the input order and their different runtime costs should
be considered when choosing an approach.

**Note**: these results came from a fixed 10 × 8 grid for the scaling experiments, so
the observed thresholds should not be treated as universal properties of any of
the three algorithms. Different grid dimensions, module distributions, and
ordering strategies may produce different results.

## References

1. Lodi, A., Martello, S. and Monaci, M. (2002). ‘Two-dimensional packing problems: A survey’. _European Journal of Operational Research_, 141(2), pp. 241–252. DOI: 10.1016/S0377-2217(02)00123-6.
2. Christensen, H. I., Khan, A., Pokutta, S. and Tetali, P. (2017). ‘Approximation and online algorithms for multidimensional bin packing: A survey’. _Computer Science Review_, 24, pp. 63–79. DOI: 10.1016/j.cosrev.2016.12.001.
3. Johnson, D. S., Demers, A., Ullman, J. D., Garey, M. R. and Graham, R. L. (1974). ‘Worst-Case Performance Bounds for Simple One-Dimensional Packing Algorithms’. _SIAM Journal on Computing_, 3(4), pp. 299–325. DOI: 10.1137/0203025.
4. Jylänki, J. (2010). ‘A Thousand Ways to Pack the Bin – A Practical Approach to Two-Dimensional Rectangle Bin Packing’. Technical report.
