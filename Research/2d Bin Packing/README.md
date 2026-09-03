
First feasible is order-dependant. If you give it 3×3 → 2×2 → 1×3, the packing is completely different from if you give it 1×3 → 3×3 → 2×2.

it scans from bottom to top (left to right on each row)

the first valid position is immediately selected, with no consideration as to whether the placement is optimal.


Additonal feature: _fill_empty_cells()
fills the remaining unoccupied cells with 1x1 modules.
-> not inherently a part of the algorithm. I added it for my use case

is_filler=true distinguishes actual generated modules from filler modules

