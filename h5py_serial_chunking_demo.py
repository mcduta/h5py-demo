"""
  Chunked Writes / Reads
  ----------------------
  * creates a dataset of shape (nimgs, nrows, ncols), of random numbers
  * the data is written to two separate HDF5 files: one serialised and one chunked
  * data is read from the two files and read times are measured

  Usage:
  -----
  python h5py_serial_chunking_demo.py
"""

import h5py
import numpy
import time
import os

# dataset dimensions
nimgs =  500    # number of images
nrows =  768    # number of rows in each image
ncols = 1366    # number of columns in each image

# image "corner" dimensions
ksize =  200    # defines data access pattern dataset[i,0:ksize-1,0:ksize-1]


# chunk dimensions
csize = ksize


#
# === write and read h5 file: NO chunks
#
with h5py.File ("h5py_test_contig.h5", "w") as h5file:
    dataset = h5file.create_dataset ("test", (nimgs, nrows, ncols), dtype=numpy.float64)
    numpy.random.seed(746574366)
    dataset[:,:,:] = numpy.random.uniform(size=(nimgs, nrows, ncols))

with h5py.File ("h5py_test_contig.h5", "r") as h5file:
    dataset = h5file["test"]
    nimgs, nrows, ncols = dataset.shape
    t = time.time ()
    for i in range(nimgs):
        tile = dataset[i,0:ksize-1,0:ksize-1]
    t = time.time () - t
    print (" contiguous dataset read in {} secs".format(t))

try:
    os.remove ("h5py_test_contig.h5")
except OSError as e:
    print("Error: %s : %s" % (file_path, e.strerror))


#
# === write and read h5 file: WITH chunks
#
with h5py.File ("h5py_test_chunked.h5", "w") as h5file:
    dataset = h5file.create_dataset("test", (nimgs, nrows, ncols), dtype=numpy.float64, chunks=(1,csize,csize))
    numpy.random.seed(746574366)
    dataset[:,:,:] = numpy.random.uniform(size=(nimgs, nrows, ncols))

with h5py.File ("h5py_test_chunked.h5", "r") as h5file:
    dataset = h5file["test"]
    nimgs, nrows, ncols = dataset.shape
    t = time.time ()
    for i in range(nimgs):
        tile = dataset[i,0:ksize-1,0:ksize-1]
    t = time.time () - t
    print (" chunked dataset ({}) read in {} secs".format(dataset.chunks, t))

try:
    os.remove ("h5py_test_contig.h5")
except OSError as e:
    print("Error: %s : %s" % (file_path, e.strerror))


#
# === write and read h5 file: WITH chunks AND compression
#
with h5py.File ("h5py_test_compress.h5", "w") as h5file:
    dataset = h5file.create_dataset("test", (nimgs, nrows, ncols), dtype=numpy.float64, chunks=(1,csize,csize), compression="gzip")
    numpy.random.seed(746574366)
    dataset[:,:,:] = numpy.random.uniform(size=(nimgs, nrows, ncols))

with h5py.File ("h5py_test_chunked.h5", "r") as h5file:
    dataset = h5file["test"]
    nimgs, nrows, ncols = dataset.shape
    t = time.time ()
    for i in range(nimgs):
        tile = dataset[i,0:ksize-1,0:ksize-1]
    t = time.time () - t
    print (" chunked and compressed dataset ({}) read in {} secs".format(dataset.chunks, t))

try:
    os.remove ("h5py_test_compress.h5")
except OSError as e:
    print("Error: %s : %s" % (file_path, e.strerror))
