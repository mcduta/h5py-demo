
"""
  Parallel H5PY Read Example
  --------------------------
  * reads a HDF5 file with a single dataset of dimensions (nrows X ncols)
  * reading to groups of rows is parallelized using MPI

  Usage:
  -----
    mpirun -np 8 python h5py_read_demo.py
    mpirun -np 8 python h5py_read_demo.py mytest.h5
"""

from mpi4py import MPI
import h5py
import numpy
import sys

# file name
filename = "test.h5"
if len(sys.argv) > 1:
    filename = str(sys.argv[1])

# parallel process details
nproc = MPI.COMM_WORLD.size  # total number of processes mpirun/mpiexec launched
iproc = MPI.COMM_WORLD.rank  # process ID (integer from 0 to nproc-1)

# open file
tstart = MPI.Wtime ()

with h5py.File (filename, "r", driver="mpio", comm=MPI.COMM_WORLD) as h5file:

    # dataset dimensions
    dataset = h5file["test"]
    nrows, ncols = dataset.shape

    # process iproc gets data rows i1 to i2
    i1 = (iproc    * nrows) // nproc
    i2 = (iproc+1) * nrows  // nproc - 1
    # random data for i2-i1 rows (no +1: indexing is 0 based!)
    dataproc = dataset[i1:i2,:]

    # record the number of bytes (NB: collective operation)
    nbytes_read = dataset.nbytes

tstop = MPI.Wtime ()

if iproc == 0:
    print ( " Dataset size: {} MB".format(nbytes_read/1024**2) )
    print ( " Collective read time: {} seconds".format(tstop-tstart) )
