import os, subprocess
from rich import print
from tabulate import tabulate

# Command to run
cmd = [
    'df',
]

# Need to convert from 1k blocks to mb/gb/tb etc
# https://stackoverflow.com/questions/12523586/python-format-size-application-converting-b-to-kb-mb-gb-tb/37423778
def format_bytes(size):
    # 2**10 = 1024
    power = 2**10
    # Since df doesn't list in bytes but kilobytes we need to start at n=1
    n = 1
    power_labels = {0 : '', 1: 'K', 2: 'M', 3: 'G', 4: 'T'}
    while size > power:
        size /= power
        n += 1
    return size, power_labels[n]+'B'

def parse_output(output_lst):
    
    # Set the header row to the first row in the list
    header = output_lst[0]

    # Rename the "1K-block" header to "Size"
    header[1] = 'Size'

    # Put the renamed header into the new list that will be shown below.
    new_lst = [header]

    # Initialize some counter vars
    total_size_all = 0
    total_used = 0
    total_avail = 0
    
    # Loop over the list
    for idx, col in enumerate(output_lst[1:]):
        # Alright, now we break everything down into it's individual cells
        filesys = col[0]
        total_size_all += int(col[1])
        total_used += int(col[2])
        total_avail += int(col[3])
        size_total, t_unit = format_bytes(int(col[1]))
        size_used, u_unit = format_bytes(int(col[2]))
        size_avail, a_unit = format_bytes(int(col[3]))                
        perc_used = col[4]
        mounted_at = col[5]

        # Append to the new list.
        new_lst.append([filesys, f"{size_total:.2f} {t_unit}", f"{size_used:.2f} {u_unit}", f"{size_avail:.2f} {a_unit}", perc_used, mounted_at])
    
    # Calculate totals
    total_perc_used = (total_used / total_size_all) * 100
    total_size, ts_unit = format_bytes(total_size_all)
    total_used, tu_unit = format_bytes(total_used)
    total_avail, ta_unit = format_bytes(total_avail)

    # Append totals to the end of the list. 
    new_lst.append(['Totals',f"{total_size:.2f} {ts_unit}", f"{total_used:.2f} {tu_unit}", f"{total_avail:.2f} {ta_unit}", f"{total_perc_used:.0f}%"])

    # output the reformated df -h output.
    print(tabulate(new_lst,headers="firstrow"))


try:
    result = subprocess.run(cmd, check=True, capture_output=True)
    output_string = result.stdout.decode().splitlines()
    output_lst = []
    for idx, outline in enumerate(output_string):
        if idx == 0:
            header = outline.split(maxsplit=5)
            output_lst.append(header)
            continue
        row = outline.split(maxsplit=5)
        output_lst.append(row)

    parse_output(output_lst)    
        
except subprocess.CalledProcessError as e:
    print("Error:", e)