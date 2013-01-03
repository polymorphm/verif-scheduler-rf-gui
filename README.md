verif-scheduler-rf-gui
======================

``verif-scheduler-rf-gui`` -- is single-minded focus utility for 
scheduling device verification process.

Used GUI special for users of Russian Federation.

Branch status
-------------

Beta branch.

Compiling for Win32
-------------------

Using cx_Freeze like:

    $ cxfreeze \
            --base-name=Win32GUI \
            --target-name=verif-scheduler-rf-gui.exe \
            --include-path=verif-scheduler \
            start_verif_scheduler_rf_gui_2013_01_02.py
    $ git rev-list HEAD^.. > dist/VERSION.txt

