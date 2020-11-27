"""
A simple implementation of ploting Probe and ProbeBunch
using matplotlib.

Depending Probe.ndim the plotting is done in 2d or 3d
"""

# matplotlib is a weak dep
import numpy as np


def plot_probe(probe, ax=None, electrode_colors=None, with_channel_index=False,
                    electrodes_kargs = {}, probe_shape_kwargs={}):
    
    import matplotlib.pyplot as plt
    if probe.ndim == 2:
        from matplotlib.collections import PolyCollection
    elif probe.ndim == 3:
        from mpl_toolkits.mplot3d.art3d import Poly3DCollection
    
    
    if ax is None:
        if probe.ndim == 2:
            fig, ax = plt.subplots()
            ax.set_aspect('equal')
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1, projection='3d')
    
    _probe_shape_kwargs = dict(facecolor='green', edgecolor='k', lw=0.5, alpha=0.3)
    _probe_shape_kwargs.update(probe_shape_kwargs)
    
    _electrodes_kargs = dict(alpha=0.7, edgecolor=[0.3, 0.3, 0.3], lw=0.5)
    _electrodes_kargs.update(electrodes_kargs)
    

    n = probe.get_electrode_count()
    
    if electrode_colors is None:
        electrode_colors = [ 'orange'] * n
    
    # electrodes
    positions = probe.electrode_positions
    min_, max_ = np.min(positions), np.max(positions)
    
    vertices = probe.get_electrodes_vertices()
    if probe.ndim == 2:
        poly = PolyCollection(vertices,color=electrode_colors,  **_electrodes_kargs)
        ax.add_collection(poly)        
    elif probe.ndim == 3:
        poly3d = Poly3DCollection(vertices,color=electrode_colors,  **_electrodes_kargs)
        ax.add_collection3d(poly3d)
    
    # probe shape
    vertices = probe.probe_shape_vertices
    if vertices is not None:
        if probe.ndim == 2:
            poly = PolyCollection([vertices], **_probe_shape_kwargs)
            ax.add_collection(poly)
        elif probe.ndim == 3:
            poly = Poly3DCollection([vertices], **_probe_shape_kwargs)
            ax.add_collection3d(poly)
        
        min_, max_ = np.min(vertices), np.max(vertices)

    if with_channel_index:
        if probe.ndim == 3:
            raise NotImplementedError('Channel index is 2d only')
        for i in range(n):
            x, y = probe.electrode_positions[i]
            if probe.device_channel_indices is None:
                txt = f'{i}'
            else:
                chan_ind = probe.device_channel_indices[i]
                txt = f'prb{i}\ndev{chan_ind}'
            ax.text(x, y, txt, ha='center', va='center')

    min_ -= 40
    max_ += 40
    
    ax.set_xlim(min_, max_)
    ax.set_ylim(min_, max_)
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    
    if probe.ndim == 3:
        ax.set_zlim(min_, max_)
        ax.set_zlabel('z')
    
    if probe.ndim == 2:
        ax.set_aspect('equal')


def plot_probe_bunch(probebunch, same_axe=True, **kargs):
    import matplotlib.pyplot as plt
    n = len(probebunch.probes)
    
    if same_axe:
        if probebunch.ndim == 2:
            fig, ax = plt.subplots()
        else:
            fig = plt.figure()
            ax = fig.add_subplot(1, 1, 1, projection='3d')
        axs = [ax] * n
    else:
        if probebunch.ndim == 2:
            fig, axs = plt.subplots(ncols=n, nrows=1)
            if n==1:
                axs = [axs]
        else:
            raise NotImplementedError

    for i, probe in enumerate(probebunch.probes):
        plot_probe(probe, ax=axs[i], **kargs)
