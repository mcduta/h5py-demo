# Experimenting with HDF5 in Python


## Material
 - this README;
 - the associated python files;
 - a Singularity container for `miniconda`, `mpi4py` and `h5py`.

**Note**: `jupyter` notebooks to experiment with MPI are very limited in scope by the very logic of parallel execution.


## Reading
 - [Python and HDF5](https://twiki.cern.ch/twiki/pub/Sandbox/JaredDavidLittleSandbox/PythonandHDF5.pdf
) by Andrew Collette (O'Reilly 2014)
 - [Some notes about chinks and compression](https://ntrs.nasa.gov/api/citations/20180008456/downloads/20180008456.pdf)
 - [h5py online documentation on parallel HDF5](https://docs.h5py.org/en/stable/mpi.html#)


## Container

### DIY
The Singularity container for `miniconda`, `mpi4py` and `h5py` can be generated with
```bash
singularity build --fakeroot h5py_latest.sif Singularity.centos-7__openmpi-4.0.5__h5py
```

### Download
The Singularity container can be directly downloaded from [SyLabs](https://cloud.sylabs.io/library/mcduta/default/h5py) using the command
```
singularity pull library://mcduta/default/h5py
```

### Interactive Shell
To experiment with the python scripts, obtain an interactive shell in the container
```
singularity shell h5py_latest.sif
```
Basic configuration settings can be checked once in a container shell, _e.g._
```
orte-info --config
h5pcc -showconfig
```
The above commands shows how `h5py` was built. See also [h5py notes on building HDF5](https://docs.h5py.org/en/stable/mpi.html#building-against-parallel-hdf5).

The expected HDF5 tools, _e.g._ `h5dump` and `h5ls` are already in path.


### Input and Output
Neither the Python scripts nor the HDF5 files generated are part of the container. The Python scripts can be anywhere in a path on DLS storage. For the purpose of experimentation for I/O performance, the HDF5 files generated can be on a path that is mounted as `gpfs`, `nfs` or local `ext4` (_e.g._ local scratch).

**Tip**: an easy way to verify what a certain path is mounted as is `df -PT /path`.

Controlling input and output can be done by bind-mounting paths in the Singularity container. For example, supposing the Python files are in `$HOME/h5pytest` and the output is to go to `/dls/p45/path/to/somewhere`, the command to start the Singularity shell is
```
singularity shell --bind $HOME/h5pytest:/apps/input,/dls/p45/path/to/somewhere:/apps/output h5py_latest.sif

```
Once in a container shell, go to the designated output path in the container and experiment, _e.g._
```
cd /apps/output/
mpirun -np 4 python /apps/input/h5py_write_demo.py
```
Any files written to `/apps/output` are "seen" outside the container in the path `/dls/p45/path/to/somewhere`.

An easier alternative to the above is to have the Python scripts and output in the same path, case in which bind-mounting the current working directory is sufficient. For example, the following command lands the Singularity shell in the current directory
```
singularity shell --home $PWD h5py_latest.sif
```
Any files generated in the container shell are visible in `$PWD` outside.

### Cluster
An interactive session on the Hamilton cluster is a good idea for a) the availability of a significant number of cores on which the `mpirun`-launched Python processes can execute and b) the availability of `gpfs` mounted paths. An example of request for an interactive job is
```
qrsh -pe openmpi-savu 20 -l h_rt=01:00:00,m_mem_free=8G -P tomography
```


## `h5py` Experiments
First, experiment with parallel writes and reads from local disk (`ext4` file system). Create a user writable directory in `/tmp` and then obtain an interactive session on Hamilton. Use the commands

```
mkdir -p /tmp/$USER
singularity shell --bind $PWD:/apps/input,/tmp/$USER:/apps/output h5py_latest.sif
```

Once in the container shell, run the "write" `h5py` demo with a varying number of processes:
```
cd /apps/output/
for np in 4 8 16; do mpirun -np ${np} python /apps/input/h5py_write_demo.py; done
```

Edit the file `h5py_write_demo.py` and observe the following:
 - the HDF5 files is open using the `mpio` driver and the operation makes use of the default MPI communicator `MPI.COMM_WORLD`;
 - each process initialises only a part of the data that is written to file;
 - there is no _global_ (across-process) view of the data; the variable `dataset` is a handle for the data;
 - data initialisation is an "independent" `h5py` operation, while file open and close are "collective" (see the [h5py notes on this](https://docs.h5py.org/en/stable/mpi.html#collective-versus-independent-operations).

The data size is fixed, so increasing the number of processes means each process initialises less data.

Now, run the "reader" demo, which reads the data from the file written by the "writer" demo. Use the command

```
for np in 4 8 16; do mpirun -np ${np} python /apps/input/h5py_read_demo.py; done
```

Edit the file `h5py_read_demo.py` and observe the similarities with the "write" demo.

---
*Exercise*:
In the "read" demo, print additional information on data read by each process, _e.g._
```
print (" iproc = {}, shape = {}, data[0,0] = {}".format(iproc, dataproc.shape, dataproc[0,0]))
```
Place this just after the last `MPI.Wtime` call. Rerun the demo with 4 processes and observe the output. Now replace the "process view" of the data `dataproc[0,0]` with the "global view" `dataset[0,0]` and rerun. What happens?
```

---



> **Exercise**: Repeat the write and read runs above on `gpfs` rather
> than `etx4`. Use an interactive cluster session and an appropriate
> path (_e.g._ `/dls/p45`) that is mounted as `gpfs` on Hamilton
> nodes. How do write/read times compare with `ext4`. Repeat the same
> operations, on the same path but this time on your workstations,
> which mounts the path as `nfs` (check!).







Singularity> for np in 4 8 16; do mpirun -np ${np} python /apps/input/h5py_read_demo.py; done
 Dataset size: 4882.8125 MB
 Collective read time: 0.42280503 seconds
 Dataset size: 4882.8125 MB
 Collective read time: 0.244647239 seconds
 Dataset size: 4882.8125 MB
 Collective read time: 0.15891313500000004 seconds
Singularity> for np in 4 8 16; do mpirun -np ${np} python /apps/input/h5py_write_demo.py; done
 Dataset size: 4882.8125 MB
 Collective write time: 20.165045275 seconds
 Dataset size: 4882.8125 MB
 Collective write time: 18.179607823 seconds
 Dataset size: 4882.8125 MB
 Collective write time: 16.264138609 seconds





gpfs

Singularity> for np in 4 8 16; do mpirun -np ${np} python h5py_write_demo.py; done
 Dataset size: 4882.8125 MB
 Collective write time: 4.477490683 seconds
 Dataset size: 4882.8125 MB
 Collective write time: 2.5929337930000003 seconds
 Dataset size: 4882.8125 MB
 Collective write time: 1.784692006 seconds


Singularity> for np in 4 8 16; do mpirun -np ${np} python h5py_read_demo.py; done
 Dataset size: 4882.8125 MB
 Collective read time: 0.646904899 seconds
 Dataset size: 4882.8125 MB
 Collective read time: 0.411342949 seconds
 Dataset size: 4882.8125 MB
 Collective read time: 0.39751512 seconds






chunks
------

gpfs03
 contiguous dataset read in 0.37422990798950195 secs
 chunked dataset ((1, 200, 200)) read in 0.5271344184875488 secs

/tmp (hamilton)
 contiguous dataset read in 0.23818206787109375 secs
 chunked dataset ((1, 200, 200)) read in 0.13118767738342285 secs

/scratch (ws404)
 contiguous dataset read in 2.823690414428711 secs
 chunked dataset ((1, 200, 200)) read in 1.273721694946289 secs

compression may reduce time (but not on random data)
and makes files smaller




Chunk size is set at dataset creation time and cannot be changed later. One can use the
h5repack tool to change storage layout properties. This command will repack and change the
chunk size of the /All_Data/CrIS-SDR_All/ES_ImaginaryLW dataset from 4x9x30x717 to
1x1x30x717, making chunk size ~82K instead of the original 3MB size:
% h5repack -l /All_Data/CrIS-SDR_All/ES_ImaginaryLW:CHUNK=1x1x30x717
gz6_SCRIS_npp_d20140522_t0754579_e0802557_b13293__noaa_pop.h5 new.h5

When compression is enabled for an HDF5 dataset, the library must always read the entire
chunk for each call to H5Dread unless the chunk is already in cache. To avoid trashing the
cache, make sure that chunk cache size is big enough to hold the chunks containing the data
read or an application reads the whole chunk at once.
When compression is disabled, the library’s behavior depends on the cache size relative to the
chunk size. If the chunk fits in the cache, the library reads the entire chunk for each call to
H5Dread unless it is in the cache. If the chunk doesn’t fit the cache, the library reads only the
data that is selected. There will be more read operations, especially if the read plane does not
include the fastest changing dimension.
