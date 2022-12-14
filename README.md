## How to run
Instructions to run


Providing a couple of options to run:
- Running it in the CLI 
- Using docker, which is preferred to avoid any environment issues, setup issues, etc

## Running it in the CLI
Make sure to have python 3.10 installed in your environment and run the following commands in your CLI (the python and pip commands could be python3 and pip3 depending on your environment)

If desired, user can pass an CLI argument to specify a different URL to get the data. Program will fail if more than one user argument is passed

```
    $ pip install -r requirements.txt 
    $ python solution.py
```    

### Using docker 
If you have docker installed in your machine, it's preferrable as the container would have the matching environment used for development. You can run the following commands in your CLI, make sure docker is running

```
    $ docker build  -t solution:latest .
    $ docker create -it --name solution-runner-container solution:latest
    $ docker start solution-runner-container 
    $ docker exec -it solution-runner-container bash
```
This will open up a build a docker container, start and open a bash session with python installed where then you can run to get the output

If desired, user can pass an CLI argument to specify a different URL to get the data. Program will fail if more than one user argument is passed


```
    $ python solution.py
```

After running the script, exit the docker container and use the following command to delete container 
``` $ exit
    $ docker container rm solution-runner-container -f
```

### Output of script
The script will print out the value of the upcoming qualifying offer along with some information about the dataset such as total number of salary records found, valid record per expected format and loss of records due to inability to process correctly; this will be printed out in tables to the command line. The script also creates a backup file of the dataset info for further inspection, and creates a file with records that couldn't be processed in case a pattern needs to be investigated. 

If the script is run several times it can create a cluster of backup data, this can be removed by running the following command 
```
    $ rm bad-data-* data-set-info-*
```