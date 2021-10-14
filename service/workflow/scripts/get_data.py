#!/usr/bin/env python3
import os
import sys
import re
def get_asti(strdata):
    defocus_vals=re.findall('\s+Defocus_U\s+Defocus_V\s+Angle\s+CCC\n\s+(.*?\..*?)\s+(.*?\..*?)\s+(.*?\..*?)\s+(.*?\..*?)\s+Final\s+Values',gf)
    if defocus_vals != []:
        return str(round(float(defocus_vals[0])-float(defocus_vals[1]),2))
    else:
        return "0"
def get_reso(strdata):
    reso_vals=re.findall('Resolution\s+limit\s+estimated\s+by\s+EPA\:.*?\s+(.*?\..*?)\s+.*',gf)
    if reso_vals != []:
        return str(round(float(reso_vals[0]),2))
    else:
        return "0"
def get_avg_shifts(strdata):
            avg_shifts=""
            with open(os.path.join(os.path.join(self.shared_scratch_dir, self.wf_name), mc2_stdout.lfn) as f):
    all_shifts=re.findall('\.\.\.\.\.\.\s+Frame\s+\(.*?\)\s+shift:\s+(.*?\..*?)\s+(.*?\..*?)\n',f.read())
    if all_shifts != []:
        #calculate avg_shifts
        shifts_1=[float(x[0]) for x in all_shifts]
        shifts_2=[float(x[1]) for x in all_shifts]
        avg_shifts_1=str(round(sum(shifts_1)/len(shifts_1)),2)
        avg_shifts_2=str(round(sum(shifts_2)/len(shifts_2)),2)
        avg_shifts="%s %s"%(avg_shifts_1, avg_shifts_2)
        return avg_shifts
    else:
        return "0 0"

if __name__ == '__main__':
    with open(sys.argv[2] as f):
        gf=f.read()
        if sys.argv[1]=="ctf_a":
            print("%s"%get_asti(gf))
        elif sys.argv[1]=="ctf_r":
            print("%s"%get_reso(gf))
        elif sys.argv[1]=="mc":
            print("%s"%get_avg_shifts(gf))
