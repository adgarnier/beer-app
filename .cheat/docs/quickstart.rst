Quickstart
==========

From Python
-----------

Load the bundled sample measurements, summarise every column, and write a
report:

.. code-block:: python

   import ci_course

   measurements = ci_course.load_measurements()
   summaries = ci_course.summarise_all(measurements)
   ci_course.write_report(summaries, "report.txt")

Missing values in the input are read as ``nan`` and are left out of the
summary, so a blank cell is never treated as a measurement of zero.

From the command line
---------------------

The package installs a ``ci-course`` command:

.. code-block:: bash

   ci-course                        # summarise the bundled sample data
   ci-course measurements.csv       # summarise your own file
   ci-course measurements.csv -o report.txt
