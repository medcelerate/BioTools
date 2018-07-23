import yaml
import os
import glob
import sys
from shutil import copyfile
from pathlib import *

def prepare_fastq(filepath):
    file_dict = {}
    fastq_list = [glob.glob(e) for e in ['*.fastq', '*.fastq.gz']]
    if os.path.isfile(str(PurePath(filepath, 'project.yml'))):
        try:
            os.stat(str(PurePath(filepath, 'Project')))
        except:
            os.makedirs(str(PurePath(filepath, 'Project')))  
        with open(str(PurePath(filepath, 'project.yml'))) as stream:
            project = yaml.load(stream)
        for k, v in project.items():
            if isinstance(v, dict):
                if k == 'groups':
                    for k2, v2 in v.items():
                        for k3, v3 in v2.items():
                            for k4, v4 in v3.items():
                                for i in range(len(v4)):
                                    t = list(v4[i][str(list(v4[i].keys())[0])].keys())
                                    for j in t:
                                        filename = v4[i][str(list(v4[i].keys())[0])][j]
                                        #print(filename)
                                        new_name = k2 + '_' + k4 + '_' + str(list(v4[i].keys())[0]) + '_'  + j 
                                        file_dict[filename] = new_name                          
                                         
            else:
                continue
        for f in fastq_list:
            if len(f) > 0:
                for x in f:
                    ext = os.path.splitext(x)[-1]
                    if ext == '.gz' or '.bz' or '.bz2':
                        key = os.path.splitext(os.path.splitext(x)[0])[0]
                        print(file_dict[key] + '.fastq' + ext)
                        copyfile(key + '.fastq' + ext, 'Project/' + file_dict[key] + '.fastq' + ext)
                        #print (filename + x)
                    else:
                        key = os.path.splitext(x)[0]
                        copyfile(key + ext, 'Project/' + file_dict[key] + ext)   
                    #ext = os.path.splitext(x)[-1]
                    #
                        #print(new_name + '.fastq' + ext)
                        #print(filename + '.fastq' + ext)
                    #    copyfile(filename + '.fastq' + ext, 'Project/' + new_name + '.fastq' + ext)
                    #else:
                    #    copyfile(filename + ext, 'Project/' + new_name + ext)        
                    
    else:
        print("Could not find project.yml file")
        sys.exit()


def majiq(filepath):
    readlen = input("Please input read length >>> ")
    samdir = input("Please input full path to BAM files >>> ")
    genome = input("Please input genome name >>> ")
    genome_path = input("Please input path to genome fasta >>> ")
    gff_path = input("Please input path to GFF3 file >>> ")
    experiments = ''
    delta_psi_command = 'majiq deltapsi -grp1 {grp1} -grp2 {grp2} -j 15 -o ./majiq/dpsi/{grp_name} --names control experiment'
    delta_psi_commands = []
    voila_command = 'voila deltapsi ./majiq/dpsi/{grp_name}/*.deltapsi.voila -s ./majiq/build/splicegraph.sql -o ./majiq/voila/{grp_name} --show-all'
    voila_commands = []
    with open(str(PurePath(filepath, 'majiq.yml'))) as stream:
            majiq = yaml.load(stream)
    for k, v in majiq.items():
        if isinstance(v, dict):
                if k == 'groups':
                    for k2, v2 in v.items():
                        for k3, v3 in v2.items():
                            groups = []
                            for k4, v4 in v3.items():
                                append_list = []
                                for i in range(len(v4)):
                                    t = v4[i][str(list(v4[i].keys())[0])]
                                    append_list.append(t) #Here I have a list containing the replicates for a group
                                exp = ",".join(append_list) #Here that list is turned to csv style for majiq config
                                experiments += k2 + '_' + k4 + '=' + exp + '\n' #These join each experiment in the config on a new line
#                                for replicate in append_list:
                                append_list = ['./majiq/build/' + s + '.majiq' for s in append_list] 
                                #I append the .majiq extension when designing the build commands
                                groups.append(append_list)
                            print(" ".join(groups[0]))
                            delta_psi_commands.append(delta_psi_command.format(
                                grp1=" ".join(groups[1]),
                                grp2=" ".join(groups[0]),
                                grp_name=k2))
                            voila_commands.append(voila_command.format(
                                grp_name=k2))

                                                    
                                         
        else:
            continue
    #print(experiments)
    file_name = majiq['project-name'] + '.conf'
    #print(file_name)
    file_content = """[info]
readlen={readlen}
samdir={samdir}
genome={genome}
genome_path={genome_path}
 
[experiments]
{experiments}
"""
    #print(file_content.format(readlen=readlen, samdir=samdir, genome=genome, genome_path=genome_path, experiments=experiments))
    f = open(file_name, 'w')
    
    f.write(file_content.format(readlen=readlen, samdir=samdir, 
    genome=genome, genome_path=genome_path, experiments=experiments))

    f.close()   

    sbatch_template = """#!/bin/bash
#SBATCH --nodes=1
#SBATCH --job-name=majiq
#SBATCH --output=slurm_%j.out
#SBATCH --exclusive
#SBATCH --partition=longq7
module load anaconda3/5.0.1
module load majiq/1.1.3a0
majiq build -o ./majiq/build {gff_path} -c ./{file_name}
{deltapsi_commands}
{voila_commands}
"""
    file_name = majiq['project-name'] + '.sh'
    f = open(file_name, 'w')
    f.write(sbatch_template.format(gff_path=gff_path, 
    file_name=file_name, 
    deltapsi_commands="\n".join(delta_psi_commands),
    voila_commands="\n".join(voila_commands)
    ))
    f.close()


def main():
    if len(sys.argv) != 2:
        print("This script requires at least 1 argument")
        sys.exit(0)
    print("""

  _______    ________  ______    _______   ______   ___   __    ______   ___   ___     
/_______/\  /_______/\/_____/\ /_______/\ /_____/\ /__/\ /__/\ /_____/\ /__/\ /__/\    
\::: _  \ \ \__.::._\/\:::_ \ \\\::: _  \ \\\::::_\/_\::\_\\\  \ \\\:::__\/ \::\ \\\  \ \   
 \::(_)  \/_   \::\ \  \:\ \ \ \\\::(_)  \/_\:\/___/\\\:. `-\  \ \\\:\ \  __\::\/_\ .\ \  
  \::  _  \ \  _\::\ \__\:\ \ \ \\\::  _  \ \\\::___\/_\:. _    \ \\\:\ \/_/\\\:: ___::\ \ 
   \::(_)  \ \/__\::\__/\\\:\_\ \ \\\::(_)  \ \\\:\____/\\\. \`-\  \ \\\:\_\ \: \ \\\::\  \\ \\
    \_______\/\________\/ \_____\/ \_______\/ \_____\/ \__\/ \__\/ \_____\/ \__\/ \::\/
                                                                                       
    """)
    while True:
        print("\n")
        print("1: Prepare FastQ Files")
        print("2: Prepare MAJIQ")
        task = input("What task would you like to complete in this directory? >>> ")
    
        if task == '1':
            pass
            prepare_fastq(sys.argv[-1])
            break
        elif task == '2':
            pass
            majiq(sys.argv[-1])
            break
        else:
            continue

if __name__ == "__main__":
    main()