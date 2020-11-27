"""
Read/write some formats:
  * probeinterface h5
  * PRB (.prb)
  * CVS (.csv)
  * mearec (.h5)
  * spikeglx (.meta)
  * ironclust/jrclust (.mat)

Also include some generator:
  * fake probe for testing.
  * generate tetrode, linear probe, multi columns probe, ...



"""
import csv
from pathlib import Path
import re
from pprint import pformat, pprint

import numpy as np

from .probe import Probe
from .probebunch import ProbeBunch


def read_probeinterface(file):
    """
    Read probeinterface own format hdf5 based.
    
    Implementation is naive but ot works.
    """
    import h5py
    
    probebunch = ProbeBunch()
    
    file = Path(file)
    with h5py.File(file, 'r') as f:
        for key in f.keys():
            if key.startswith('probe_'):
                probe_ind = int(key.split('_')[1])
                probe_dict = {}
                for k in Probe._dump_attr_names:
                    path = f'/{key}/{k}'
                    if not path in f:
                        continue
                    v = f[path]
                    if k == 'electrode_shapes':
                        v2 = np.array(v).astype('U')
                    elif k == 'electrode_shape_params':
                        l = []
                        for e in v:
                            d = {}
                            exec(e.decode(), None, d)
                            l.append(d['value'])
                        v2 = np.array(l, dtype='O')
                    elif k == 'si_units':
                        v2 = str(v[0])
                    elif k == 'ndim':
                        v2= int(v[0])
                    else:
                        v2 = np.array(v)
                    probe_dict[k] = v2
                
                probe = Probe.from_dict(probe_dict)
                probebunch.add_probe(probe)
    return probebunch


def write_probeinterface(file, probe_or_probebunch):
    """
    Write to probeinterface own format hdf5 based.
    
    Implementation is naive but ot works.
    """
    import h5py
    if isinstance(probe_or_probebunch, Probe):
        probebunch = ProbeBunch()
        probebunch.add_probe(probe)
    elif isinstance(probe_or_probebunch, ProbeBunch):
        probebunch = probe_or_probebunch
    else:
        raise valueError('Bad boy')
    
    file = Path(file)
    
    with h5py.File(file, 'w') as f:
        for probe_ind, probe in enumerate(probebunch.probes):
            d = probe.to_dict()
            for k, v in d.items():
                if k == 'electrode_shapes':
                    v2 =v.astype('S')
                elif k == 'electrode_shape_params':
                    v2 = np.array(['value='+pformat(e) for e in v], dtype='S')
                elif k == 'si_units':
                    v2 = np.array([v.encode('utf8')])
                elif k == 'ndim':
                    v2 = np.array([v])
                else:
                    v2 = v
                path = f'/probe_{probe_ind}/{k}'
                f.create_dataset(path, data=v2)


def read_prb(file):
    """
    Read a PRB file and return a ProbeBunch object.
    
    Since PRB do not handle electrode shape then circle of 5um are put.
    Same for electrode shape a fake tip is put.
    
    PRB format do not contain any information about the channel of the probe
    Only the channel index on device is given.
    
    """

    file = Path(file).absolute()
    assert file.is_file()
    with file.open('r') as f:
        contents = f.read()
    contents = re.sub(r'range\(([\d,]*)\)',r'list(range(\1))',contents)
    prb = {}
    exec(contents, None, prb)
    prb = {k.lower(): v for (k, v) in prb.items()}
    
    if 'channel_groups' not in prb:
        raise ValueError('This file is not a standard PRB file')
    
    probebunch = ProbeBunch()
    for i, group in prb['channel_groups'].items():
        probe = Probe(ndim=2, si_units='um')
        
        chans = np.array(group['channels'], dtype='int64')
        positions = np.array([group['geometry'][c] for c in chans], dtype='float64')
        
        probe.set_electrodes(positions=positions, shapes='circle', shape_params={'radius': 5})
        probe.create_auto_shape(probe_type='tip')
        
        
        probe.set_device_channel_indices(chans)
        probebunch.add_probe(probe)
    
    return probebunch

def write_prb(file, probebunch):
    """
    Write ProbeBunch into a prb file.
    
    This format handle:
      * multi Probe with channel group index key
      * channel positions with "geometry"
      * device_channel_indices with "channels "key
    
    Note: many information are lost in the PRB format:
      * electrode shape
      * shape
      * channel index
    """
    raise NotImplementedError

def read_cvs(file):
    """
    Return a 2 or 3 columns csv file with electrodes position
    """
    raise NotImplementedError

def write_cvs(file, probe):
    """
    Write probe postions into a 2 or 3 columns csv file
    """
    raise NotImplementedError

def read_mearec(file):
    """
    read probe position, and electrode shape from a mearec file
    
    Alesio : this is for you
    """
    raise NotImplementedError
    
def read_spikeglx(file):
    """
    read probe position for the meta file generated by spikeglx
    """
    raise NotImplementedError
    