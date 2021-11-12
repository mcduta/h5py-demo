from mpi4py import MPI
import h5py

# parallel process details
nproc = MPI.COMM_WORLD.size  # total number of processes mpirun/mpiexec launched
iproc = MPI.COMM_WORLD.rank  # process ID (integer from 0 to nproc-1)

if nproc <= 4:
    # open h5 file for writing
    with h5py.File ("h5py_simple_test.hdf5", "w", driver="mpio", comm=MPI.COMM_WORLD) as h5file:
        # create and initialise dataset
        dataset = h5file.create_dataset ("test", (4,), dtype="uint32")
        dataset[iproc] = iproc + 1

else:
    # rank 0 prints an error
    if iproc == 0:
        print (" *** error: number of processes should be <= 4")
