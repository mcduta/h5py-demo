"""
  Parallel H5PY Write Example
  ---------------------------
  * creates a HDF5 file with a single dataset of dimensions (nrows X ncols)
  * dataset consists of random numbers (an attempt is made at making these
    numbers independent per process via appropriate seeding)
  * writing to groups of rows is parallelized using MPI
  * default dimensions are nrows = 128, ncols = 10**7, which produce a file
    of close to 5GB in size (single precision)

  Usage:
  -----
    mpirun -np 8 python h5py_write_demo.py
    mpirun -np 8 python h5py_write_demo.py 32 1000 mytest.h5
"""

from mpi4py import MPI
import h5py
import numpy
import sys

# dataset dimensions
nrows = 128
ncols = 10**7
if len(sys.argv) > 1:
    nrows = int(sys.argv[1])
    ncols = int(sys.argv[2])

# file name
filename = "test.h5"
if len(sys.argv) > 3:
    filename = str(sys.argv[3])

# parallel process details
nproc = MPI.COMM_WORLD.size  # total number of processes mpirun/mpiexec launched
iproc = MPI.COMM_WORLD.rank  # process ID (integer from 0 to nproc-1)

# randomise using seed + process rank
numpy.random.seed(746574366 + iproc)

# open file (collective / global operation) and write to data handle (individual / per process operation)
tstart = MPI.Wtime ()

with h5py.File (filename, "w", driver="mpio", comm=MPI.COMM_WORLD) as h5file:
    # data handle
    dataset = h5file.create_dataset("test", (nrows, ncols), dtype=numpy.float32)
    # create data in parallel
    #     process 0: rows 0 to (ncols // nproc) - 1
    #     process 1: rows (ncols // nproc) to (2 * ncols // nproc) - 1
    #     ...
    # process iproc gets data rows i1 to i2
    i1 = (iproc    * nrows) // nproc
    i2 = (iproc+1) * nrows  // nproc - 1
    # random data for i2-i1 rows (no +1: indexing is 0 based!)
    data = numpy.random.uniform(size=(i2-i1, ncols))
    dataset[i1:i2,:] = data + 10**3 * (iproc+1)

tstop = MPI.Wtime ()

if iproc == 0:
    print ( " Dataset size: {} MB".format((nrows*ncols*numpy.float32().itemsize)/1024**2) )
    print ( " Collective write time: {} seconds".format(tstop-tstart) )
