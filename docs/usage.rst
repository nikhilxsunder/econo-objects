Usage
=====

Here's an example of how to use the package:

.. code-block:: python

   from econo_objects import FredObject

   fred_obj = FredObject("GDP", "2020-01-01", "2023-01-01")
   plot = fred_obj.plot_df