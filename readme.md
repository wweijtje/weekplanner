
Program
-------

The program runs when the raspberry pi is connected to a power source. It will 
automatically shut down the pi 5 minutes after completing the routine.


To prevent this automatic shutdown, either interrupt the shutdown;
``sudo shutdown -c``
Or alternatively make a no-shutdown flag:

run ``touch ~/STOP_SHUTDOWN`` in a shell


Transfer images
---------------

To quickly transfer files to the raspberry pi

PS C:\Pycharm\WeekPlanner> scp -r icons wout@192.168.0.203:/home/wout/weekplanner/icons