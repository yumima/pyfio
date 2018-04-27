import os
import argparse
import time
import json
import subprocess
from pprint import pprint

parser = argparse.ArgumentParser(description = "FIO wrapper in python")
parser.add_argument('-c', action="store", dest='conf_file', help='configuration json')
args = parser.parse_args()
conf_file=args.conf_file
conf=json.load(open(conf_file))
print (conf_file, conf)

wl=(conf["readwrite"]) if 'readwrite' in conf else  "randrw"
datasize=(conf["datasize"]) if 'datasize' in conf else  "4G"
runtime=(conf["runtime"]) if 'runtime' in conf else  "120"
numjobs=(conf["numjobs"]) if 'numjobs' in conf else  "1, 9, 18"
engine=(conf["engine"]) if 'engine' in conf else  "libaio"
iterations=(conf["nruns"]) if 'nruns' in conf else  "3"
blocksize=(conf["blocksize"]) if 'blocksize' in conf else  "1k, 4k, 16k, 64k, 256k, 1M, 4M"
iodepth=(conf["iodepth"]) if 'iodepth' in conf else  "1,  2,  4,  8,  16,  32,  64,  128"
devices=(conf["devices"]) if 'devices' in conf else  {'dev': '/tmp', 'cpu': '0-1', 'rw': 'randrw'}

#print (wl, datasize, runtime, numjobs, engine, iterations, blocksize, iodepth, devices)

# fio --minimal hardcoded positions
fio_iops_pos=7
fio_slat_pos_start=9
fio_clat_pos_start=13
fio_lat_pos_start=37

columns="device;iotype;bs;njobs;iodepth;iops;slatmin;slatmax;slatavg;clatmin;clatmax;clatavg;latmin;latmax;latavg"

# create base dir with unique identifier
conf_name=os.path.splitext(conf_file)[0]
identifier=time.strftime("%H%M%S") 
base_dir=conf_name + "-" + identifier
if not os.path.exists(base_dir ): os.makedirs(base_dir)
f = open(base_dir + "-fio.csv", "w+")
f.write(columns+"\n")

# for now, loop through each device at a time
# eventually, rewrite to fire one thread per device
for dev in devices:
    dev_name=(dev["dev"]) if 'dev' in dev else "/tmp"
    dev_str = dev_name.replace("/", "_")
    dev_dir = base_dir + "/" + dev_str
    #if not os.path.exists(dev_dir): os.makedirs(dev_dir)

    # read and configure per device settings
    cpu=(dev["cpu"]) if 'cpu' in dev else "0-71"
    iotypes=(dev["rw"]) if 'rw' in dev else wl 
    print (dev_name, dev_dir, cpu, iotypes)

    for rw in iotypes.split():
        rw_dir = dev_dir + "/" + rw
        #if not os.path.exists(rw_dir): os.makedirs(rw_dir)
        
        for bs in blocksize:
            bs_dir = rw_dir + "/" + bs
            #if not os.path.exists(bs_dir): os.makedirs(bs_dir)
            
            for nj in numjobs:
                nj_dir = bs_dir + "/" + nj + "-job"
                #if not os.path.exists(nj_dir): os.makedirs(nj_dir)

                for qd in iodepth:
                    qd_dir = nj_dir + "/" + qd + "-depth"
                    #if not os.path.exists(qd_dir): os.makedirs(qd_dir)
        
                    fio_type_offset = 0
                    iops = 0.0
                    slat = [0.0 for i in range(3)]
                    clat = [0.0 for i in range(3)]
                    lat = [0.0 for i in range(3)]
                    fname=dq_dir + "/" + conf_name + "-" + dev_str + "-" + rw + "-" + bs + qd +"d" + ".fio"
                    result = "" + str(dev_name) + ";" + str(rw) + ";" + str(bs) + ";" + str(numjobs) + ";" + str(qd) + ";"
                    command = "sudo fio --minimal -name="+str(fname) + \
                        " --bs="+str(bs)+" --ioengine="+str(engine)+ \
                        " --iodepth="+str(qd)+" --size="+str(datasize) + \
                        " --direct=1 --cpus_allowed_policy=split" + \
                        " --cpus_allowed="+str(cpu) + \
                        " --rw="+str(rw)+" --filename="+str(dev_name) + \
                        " --numjobs="+str(numjobs)+" --time_based" + \
                        " --runtime="+runtime+" --group_reporting"
                    print (command)

                    n_iterations=int(iterations)
                    for i in range (0, n_iterations):
                        os.system("sleep 2") #Give time to finish inflight IOs
                        output = subprocess.check_output(command, shell=True)
                        if "write" in rw:
                            fio_type_offset=41

                        # fio is called with --group_reporting. This means that all
                        # statistics are group for different jobs.

                        # iops
                        iops = iops + float(output.split(";")[fio_type_offset + fio_iops_pos])

                        # slat
                        for j in range (0, 3):
                            slat[j] = slat[j] + float(output.split(";")[fio_type_offset+fio_slat_pos_start+j])
                        # clat
                        for j in range (0, 3):
                            clat[j] = clat[j] + float(output.split(";")[fio_type_offset+fio_clat_pos_start+j])
                        # lat
                        for j in range (0, 3):
                            lat[j] = lat[j] + float(output.split(";")[fio_type_offset+fio_lat_pos_start+j])
                    # end of for n_iterations
                    # iops
                    result = result+str(iops / n_iterations)
                    # slat
                    for i in range (0, 3):
                        result = result+";"+str(slat[i] / n_iterations)
                    # clat
                    for i in range (0, 3):
                        result = result+";"+str(clat[i] / n_iterations)
                    # lat
                    for i in range (0, 3):
                        result = result+";"+str(lat[i] / n_iterations)

                    print (result)
                    f.write(result+"\n")
                    f.flush()
                # end of  for qd
            # end of  for nj
        # end of  for bs 
    # end of  for dev 
f.closed
