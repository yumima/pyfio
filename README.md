## Python wrapper for fio to test and measure disk performance. 

### JSON input exmaple:

{
  "readwrite": "randrw",
  "datasize": "5G",
  "numjobs":  "1, 8, 16",
  "runtime": "120",
  "engine": "libaio",
  "iterations": "3",
  "blocksize": [ "1k", "4k", "16k", "64k", "256k", "1M", "4M" ],
  "iodepth": [  "1",  "2",  "4",  "8",  "16",  "32",  "64",  "128"  ], 

  "": "//customize each device to run workload in parallel",
  "devices": [
    { "dev": "nvme0n1", "cpu": "0-8",   "rw": "read" },
    { "dev": "nvme1n1", "cpu": "9-17",  "rw": "write" },
    { "dev": "nvme2n1", "cpu": "18-26", "rw": "randread" },
    { "dev": "nvme3n1", "cpu": "27-35", "rw": "randwrite" },
    { "dev": "nvme4n1", "cpu": "36-44", "rw": "randrw", "rwmixread": "70" },
    { "dev": "nvme5n1", "cpu": "45-53" },
    { "dev": "nvme6n1", "cpu": "54-62" },
    { "dev": "nvme7n1", "cpu": "63-71" }
  ]
}

### Usage:
$ pyfio -c <config_file_name.json>

### Output:
config_file_name/config_file_name-fio.cvs
