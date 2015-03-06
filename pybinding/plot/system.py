import matplotlib.pyplot as _plt
import numpy as _np


def blend_colors(color, bg, blend):
    from matplotlib.colors import colorConverter
    color, bg = map(lambda c: _np.array(colorConverter.to_rgb(c)), (color, bg))
    return (1 - blend) * bg + blend * color


def make_cmap_and_norm(colors=None, blend=1):
    # default color palettes
    if not colors or colors == 'default':
        colors = ["#377ec8", "#ff7f00", "#41ae76", "#e41a1c",
                  "#984ea3", "#ffff00", "#a65628", "#f781bf"]
    elif colors == 'pairs':
        colors = ["#a6cee3", "#1f78b4", "#b2df8a", "#33a02c", "#fb9a99", "#e31a1c",
                  "#fdbf6f", "#ff7f00", "#cab2d6", "#6a3d9a"]

    if blend < 1:
        colors = [blend_colors(c, 'white', blend) for c in colors]

    # colormap with an integer norm to match the sublattice indices
    from matplotlib.colors import ListedColormap, BoundaryNorm
    cmap = ListedColormap(colors)
    norm = BoundaryNorm(list(range(len(colors)+1)), len(colors))

    return cmap, norm


def plot_hoppings(ax, positions, hoppings, width,
                  offset=(0, 0, 0), boundary=False, blend=0.5, **kwargs):
    if width == 0:
        return

    defaults = dict(color='black', zorder=-1)
    kwargs = dict(defaults, **kwargs)
    kwargs['color'] = blend_colors(kwargs['color'], 'white', blend)

    ndims = 3 if ax.name == '3d' else 2
    offset = offset[:ndims]
    positions = positions[:ndims]

    if not boundary:
        # positions += offset
        positions = tuple(v + v0 for v, v0 in zip(positions, offset))
        # coor = x[n], y[n], z[n]
        coor = lambda n: tuple(v[n] for v in positions)
        lines = ((coor(i), coor(j)) for i, j in hoppings.indices())
    else:
        coor = lambda n: tuple(v[n] for v in positions)
        coor_plus = lambda n: tuple(v[n] + v0 for v, v0 in zip(positions, offset))
        coor_minus = lambda n: tuple(v[n] - v0 for v, v0 in zip(positions, offset))

        from itertools import chain
        lines = chain(
            ((coor_plus(i), coor(j)) for i, j in hoppings.indices()),
            ((coor(i), coor_minus(j)) for i, j in hoppings.indices())
        )

    if ndims == 2:
        from matplotlib.collections import LineCollection
        ax.add_collection(LineCollection(lines, lw=width, **kwargs))
        ax.autoscale_view()
    else:
        from mpl_toolkits.mplot3d.art3d import Line3DCollection
        had_data = ax.has_data()
        ax.add_collection3d(Line3DCollection(list(lines), lw=width, **kwargs))

        ax.set_zmargin(0.5)
        minmax = tuple((v.min(), v.max()) for v in positions)
        ax.auto_scale_xyz(*minmax, had_data=had_data)


def plot_sites(ax, positions, sublattice, radius,
               colors=None, offset=(0, 0, 0), blend=1, **kwargs):
    if radius == 0:
        return

    defaults = dict(alpha=0.95, lw=0.1)
    kwargs = dict(defaults, **kwargs)
    kwargs['cmap'], kwargs['norm'] = make_cmap_and_norm(colors, blend)

    # create array of (x, y) points
    points = _np.column_stack(v + v0 for v, v0 in zip(positions[:2], offset[:2]))

    if ax.name != '3d':
        from pybinding.support.collections import CircleCollection
        idx = positions[2].argsort()  # sort points and sublattice based on z position
        col = CircleCollection(radius, offsets=points[idx], transOffset=ax.transData, **kwargs)
        col.set_array(sublattice[idx])

        ax.add_collection(col)
        ax.autoscale_view()
    else:
        from pybinding.support.collections import Circle3DCollection
        col = Circle3DCollection(radius/8, offsets=points, transOffset=ax.transData, **kwargs)
        col.set_array(sublattice)
        z = positions[2] + offset[2]
        col.set_3d_properties(z, 'z')

        had_data = ax.has_data()
        ax.add_collection(col)
        minmax = tuple((v.min(), v.max()) for v in positions)
        ax.auto_scale_xyz(*minmax, had_data=had_data)


def plot_site_indices(system):
    # show the Hamiltonian index next to each atom (for debugging)
    for i, (x, y) in enumerate(zip(system.x, system.y)):
        _plt.annotate(
            str(i), (x, y), xycoords='data', color='black',
            horizontalalignment='center', verticalalignment='center',
            bbox=dict(boxstyle="round,pad=0.2", fc='white', alpha=0.5, lw=0.5)
        )